# DOCUMENT 6: IMPLEMENTATION & FEASIBILITY PLAN

**Project Name:** PARIKSHAK-AI (परीक्षक-AI)  
**Challenge:** Challenge 03 — AI-Driven Examination & On-Screen Marking Transformation  
**Track:** Technical Track | **Team Name:** eMitra  

---

## 1. Feasibility Assessment: Non-Invasive Bolt-On Architecture

The primary reason previous digital evaluation tenders in Madhya Pradesh failed (such as Barkatullah University's cancelled ₹8 Crore RFP and DAVV Indore's frozen pilot) was their insistence on monolithic overhauls—attempting to replace existing university databases, examination registers, and scanning logistics all at once.

PARIKSHAK-AI is engineered with a **Non-Invasive Microservice Architecture**. It does not replace MPOnline’s established ASP.NET Core portal or Oracle 19c database at the MP State Data Centre (SDC) in Bhopal. Instead, it operates as an **Intelligent Cognitive Sidecar**:
* Ingests scanned booklet imagery via temporary, pre-signed HTTPS URLs.
* Performs offline layout analysis, question segmentation, and rubric alignment.
* Provides examiners with a responsive, low-bandwidth web evaluation canvas.
* Asynchronously commits validated marks directly into MPOnline's Tabulation Register via standard REST APIs and message queues.

---

## 2. Four-Phase Phased Rollout Roadmap

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       PARIKSHAK-AI DEPLOYMENT TIMELINE                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  [ PHASE 1: PROTOTYPE & BENCHMARKING ] ──► Oct 2026 – Dec 2026                  │
│  • Hackathon prototype hardening                                                │
│  • Corpus ingestion: 10,000 sample MP university answer scripts (Hindi/English) │
│  • CERT-In Empaneled Security VAPT & STQC Code Quality Audit                    │
│                                                                                 │
│  [ PHASE 2: CONTROLLED UNIVERSITY PILOT ] ──► Jan 2027 – Mar 2027 (Winter Exam) │
│  • Live 25,000-script pilot at DAVV Indore (MBA) or BU Bhopal (B.Tech)          │
│  • Non-destructive V-cradle scanning deployment at Central Valuation Center    │
│  • Calibration testing with 50 empanelled university professors                 │
│                                                                                 │
│  [ PHASE 3: TOP-5 STATE UNIVERSITY EXPANSION ] ──► Apr 2027 – Sep 2027 (Summer)│
│  • Rollout across DAVV, BU Bhopal, RGPV, Jiwaji, and Vikram University          │
│  • ~50 Lakh answer scripts evaluated across 55 districts                        │
│  • Integration with MP State Data Centre (SDC) private GPU cluster              │
│                                                                                 │
│  [ PHASE 4: STATEWIDE INSTITUTIONAL SCALE ] ──► 2028 Onwards                    │
│  • Full coverage across all 25 State Public Universities (3.0+ Crore booklets)  │
│  • Integration with DigiLocker and National Academic Depository (NAD / ABC)     │
│  • Citizen-centric governance: transparent result portals and diagnostic cards   │
│                                                                                 │
│  [ PHASE 5: NATIONAL EXPANSION & MULTI-LANGUAGE SCALE ] ──► 2029 Onwards        │
│  • Replicate to 3–5 high-demand states: UP, Rajasthan, Bihar, Maharashtra, CG   │
│  • Extend multimodal vision to additional Indic scripts: Bangla, Tamil, Telugu   │
│  • Serve non-university examination bodies: CBSE, State Boards, ICAI, Pharmacy  │
│  • White-label SaaS offering through MPOnline/TCS iON partnership network       │
│  • Pan-India TAM: 49 Crore scripts/year (AISHE 2022-23, ₹10,000+ Cr market)   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Physical-to-Digital Scanning Protocol (The Anti-Tampering Standard)

To eliminate the physical security vulnerabilities that halted DAVV Indore’s digital evaluation rollout in July 2026 (fear of guillotine spine-cutting, page-swapping, and unstitched sheet theft), PARIKSHAK-AI establishes a **Two-Tier Non-Destructive Scanning Standard**:

### Tier 1: Non-Destructive Overhead V-Cradle Scanning (High-Stakes & Professional Exams)
* **Equipment:** High-speed overhead book scanners (e.g., CZUR M3000 Pro / Zeutschel OS 12002) equipped with V-shaped book cradles and auto-flattening curve algorithms.
* **Integrity:** The physical cotton thread binding (*Dhaga Silayi*) of the 36-page booklet remains **100% intact**. Not a single staple or thread is cut.
* **Throughput:** Scans an entire 36-page booklet in under 60 seconds at 300 DPI color/grayscale.

### Tier 2: Leaf-Level 2D DataMatrix Validation (High-Volume General Exams)
* Where automatic document feeder (ADF) scanners are deployed for extreme volume (B.A. / B.Com. examinations):
  * Every physical page features a pre-printed, serialized 2D DataMatrix code encoding both booklet UUID and sequential page number (`BK-94812-P14`).
  * The scanning daemon enforces a strict **Discontinuity Trap**: if any page sequence is missing, skipped, or duplicated, the scanning batch halts instantly, and the physical packet is sequestered.
  * Scanning operations occur strictly within the **University Strong Room (*Gopneeya Shakha*)** under dual-key access and continuous 360-degree CCTV surveillance.

---

## 4. Hardware Sizing & Sovereign Cloud Deployment

To guarantee total compliance with the **Digital Personal Data Protection (DPDP) Act 2023** and maintain 100% data residency within Madhya Pradesh:

* **Primary Hosting Facility:** MP State Data Centre (SDC), Bhopal.
* **Disaster Recovery (DR) Site:** TCS Tier-4 Data Centre / MeitY-empanelled CSP (AWS / Azure Central India).
* **Compute Sizing for Statewide Peak Load (500,000 Booklets / Day):**
  * *Inference Cluster:* 4x Enterprise AI Nodes, each hosting 4x NVIDIA L40S 48GB GPUs (16 GPUs total) running quantized open-weights Indic Multimodal Vision models (e.g., Qwen2.5-VL / Sarvam Indic VLM) with vLLM PagedAttention.
  * *Throughput Capacity:* 480 question-bundle evaluations per second, clearing 500,000 booklets daily during peak valuation hours (10:00 AM – 5:00 PM).
  * *Storage Infrastructure:* 150 TB encrypted NVMe-backed MinIO S3 object storage configured with write-once-read-many (WORM) immutability policies.

---

## 5. Risk Assessment & Comprehensive Mitigation Matrix

| # | Identified Risk Domain | Severity | Operational / Technical Mitigation in PARIKSHAK-AI |
|---|------------------------|:--------:|----------------------------------------------------|
| **1** | **Teacher Union Resistance (University Faculty Associations)** | **HIGH** | Replace punitive screen lockouts with a **3-Tier Progressive Friction Protocol** (Soft Nudge $\rightarrow$ Touchpoint Gate $\rightarrow$ Silent Shadow Review). Recommend hiking examiner honorariums from ₹15 to ₹40/copy funded by ₹25 Cr logistics savings. |
| **2** | **Rural Bandwidth Fluctuation** | **MEDIUM** | Deploy **Local Edge Caching Appliances (LECA)** at District Lead Colleges (*Agrani Mahavidyalayas*) to pre-download daily bundles overnight, serving evaluators over local high-speed LAN without active internet dependencies. |
| **3** | **Spine-Cutting / Page Swapping** | **HIGH** | Mandate non-destructive V-cradle overhead scanners for professional courses; require leaf-level 2D serialized DataMatrix codes for ADF scanners. |
| **4** | **Adversarial Prompt Injection** | **MEDIUM** | Dual-turn sandboxed inference: Turn 1 extracts visual text into strict JSON schemas with zero command execution; Turn 2 evaluates within CDATA boundaries. Transcribed text pre-screened for injection signatures. |
| **5** | **Low Paper GSM & Ink Bleed-Through** | **MEDIUM** | Adaptive preprocessing pipeline applying Sauvola binarization and morphological background subtraction to eliminate reverse-page ink bleed-through on 54–60 GSM paper. |
| **6** | **Displaced Revaluation Cash Flow** | **MEDIUM** | Provide university Executive Councils with audited Net Fiscal Surplus models showing +₹1.26 Crore annual net savings from eliminated paper transport, armed escorts, and court litigation costs. |

---

## 6. Regulatory & Statutory Certification Strategy

Prior to Phase 2 university pilot commissioning, PARIKSHAK-AI will undergo formal statutory certification:
1. **STQC Directorate Clearance:** Functional and performance testing for electronic governance applications under Ministry of Electronics and Information Technology (MeitY) guidelines.
2. **CERT-In Empaneled Security VAPT:** Rigorous vulnerability assessment and penetration testing verifying zero Broken Object Level Authorization (BOLA/IDOR) flaws.
3. **University Executive Council Resolutions:** Amending Ordinance No. 5 across participating universities to formally recognize digital assistive evaluation and Section 63 BSA electronic audit trails.

---

## 7. Commercial Sustainability & Revenue Model

### A. SaaS Pricing Architecture (Per-Script Transaction Model)
PARIKSHAK-AI operates as a **zero-capex AI intelligence layer** atop existing OSM scanning infrastructure, charging a per-booklet transaction fee:

| Component | Unit Cost | Volume (MP Statewide) | Annual Revenue |
| :--- | :--- | :--- | :--- |
| AI Copilot Inference (Gemini Flash) | ₹1.14 / booklet | 3.04 Crore scripts | ₹3.47 Crore |
| Seed Calibration & Velocity Sentinel SaaS | ₹1.50 / booklet | 3.04 Crore scripts | ₹4.56 Crore |
| Section 63 BSA Dossier Generation | ₹0.50 / booklet | 3.04 Crore scripts | ₹1.52 Crore |
| Command Center Dashboard (Annual License) | ₹15 Lakh / university | 25 universities | ₹3.75 Crore |
| **Total MP Annual Revenue** | | | **₹13.30 Crore** |

### B. Strategic Alignment with MPOnline's Revenue Expansion
MPOnline currently earns ~₹25 Crore/year from higher education form fees alone. The evaluation market (₹60–₹75 Crore/year for 3.04 Crore scripts across MP) remains **uncaptured revenue** lost to fragmented private vendor tenders. PARIKSHAK-AI enables MPOnline to expand from upstream form collection into high-value downstream evaluation processing—doubling higher education revenue without additional kiosk infrastructure.

### C. Funding via PM-USHA & RUSA Grants
MP state universities are eligible for **₹20 to ₹40 Crore per institution** under PM-USHA (₹12,926 Crore national outlay) specifically for examination automation and IT infrastructure. PARIKSHAK-AI deployment qualifies as a **PM-USHA-compliant examination reform investment**, making the solution **self-funded from central government grants** rather than university operating budgets.
