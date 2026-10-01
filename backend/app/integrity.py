"""Tamper evidence: SHA-256 leaves, a Merkle root, an Ed25519 signature and a hash-chained ledger."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def merkle_root(leaf_hashes: list[str]) -> str:
    if not leaf_hashes:
        raise ValueError("no leaves")
    level = [bytes.fromhex(h) for h in leaf_hashes]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256(level[i] + level[i + 1]).digest() for i in range(0, len(level), 2)]
    return level[0].hex()


def evidence_leaves(page_bytes: list[bytes], record: dict) -> list[list[str]]:
    """One leaf per scanned page plus the AI pre-read, the marks, the annotations and the telemetry."""
    leaves = [[f"page_{i}_image", sha256_hex(b)] for i, b in enumerate(page_bytes, start=1)]
    leaves.append(["ai_preread", sha256_hex(canonical_json(record["preread"]))])
    leaves.append(["examiner_marks", sha256_hex(canonical_json({
        "examiner_id": record["examiner_id"],
        "marks": record["marks"],
        "total": record["total"],
        "submitted_at": record["submitted_at"],
    }))])
    leaves.append(["annotations", sha256_hex(canonical_json(record["annotations"]))])
    leaves.append(["telemetry", sha256_hex(canonical_json({
        "telemetry": record["telemetry"],
        "velocity": record["velocity"],
    }))])
    return leaves


class Signer:
    """Ed25519 key standing in for the university's e-Sign / HSM key in this POC."""

    def __init__(self, key_path: Path):
        key_path.parent.mkdir(parents=True, exist_ok=True)
        if key_path.exists():
            self._key = serialization.load_pem_private_key(key_path.read_bytes(), password=None)
        else:
            self._key = Ed25519PrivateKey.generate()
            key_path.write_bytes(self._key.private_bytes(
                serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
            os.chmod(key_path, 0o600)
        raw = self._key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.public_key_hex = raw.hex()
        fp = sha256_hex(raw)[:16].upper()
        self.fingerprint = " ".join(fp[i:i + 4] for i in range(0, 16, 4))

    def sign(self, root_hex: str) -> str:
        return self._key.sign(bytes.fromhex(root_hex)).hex()

    def verify(self, root_hex: str, signature_hex: str) -> bool:
        try:
            self._key.public_key().verify(bytes.fromhex(signature_hex), bytes.fromhex(root_hex))
            return True
        except (InvalidSignature, ValueError):
            return False


class Ledger:
    """Append-only, hash-chained log of signed roots (a stand-in for WORM storage)."""

    def __init__(self, path: Path):
        self.path = path
        self.entries: list[dict] = []

    def reset(self) -> None:
        self.entries = []
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")

    def append(self, script_id: str, root: str, signature: str, leaves: list[list[str]]) -> dict:
        entry = {
            "index": len(self.entries),
            "script_id": script_id,
            "merkle_root": root,
            "signature": signature,
            "leaves": leaves,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "prev_hash": self.entries[-1]["entry_hash"] if self.entries else "0" * 64,
        }
        entry["entry_hash"] = sha256_hex(canonical_json(entry))
        self.entries.append(entry)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def find(self, script_id: str) -> dict | None:
        return next((e for e in reversed(self.entries) if e["script_id"] == script_id), None)

    def chain_ok(self) -> bool:
        prev = "0" * 64
        for e in self.entries:
            body = {k: v for k, v in e.items() if k != "entry_hash"}
            if e["prev_hash"] != prev or sha256_hex(canonical_json(body)) != e["entry_hash"]:
                return False
            prev = e["entry_hash"]
        return True

    @property
    def head(self) -> str:
        return self.entries[-1]["entry_hash"] if self.entries else "0" * 64
