# 🏛️ PARIKSHAK-AI (परीक्षक-AI)

> **Bhashini-Aligned Cognitive Copilot & Quality Assurance Architecture for On-Screen Marking**  
> *Technical Proposal & System Architecture for MPOnline Idea & Innovation Hackathon 2026 — Challenge 03*  
> **Track:** Technical Track | **Team:** eMitra | **Submission Date:** October 1, 2026

[![Hackathon](https://img.shields.io/badge/MPOnline_Hackathon-Challenge_03-blue.svg)](https://innovate.mponline.gov.in)
[![Track](https://img.shields.io/badge/Track-Technical-orange.svg)]()
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Status-Ideation_%26_Architecture_Ready-teal.svg)]()
[![Compliance](https://img.shields.io/badge/Compliance-DPDP_2023_%7C_BSA_2023_%7C_MeghRaj-purple.svg)]()

---

## 📌 Executive Summary

**PARIKSHAK-AI** is a comprehensive technical architecture and system design for transforming university examination evaluation across Madhya Pradesh. Engineered as an asynchronous, stateless cognitive microservice, it is designed to bolt directly onto **MPOnline's existing ASP.NET Core presentation layer and Oracle 19c Enterprise database cluster** hosted at the **MP State Data Centre (SDC) in Bhopal**.

Rather than attempting an unviable "autonomous AI auto-grader" that violates UGC academic statutes, PARIKSHAK-AI operates as a **Human-in-the-Loop (HITL) Examiner Copilot**. It pairs university professors with multimodal intelligence that eliminates human fatigue, catches data entry errors in real time, and produces legally unassailable audit trails.

> ℹ️ **Current Phase:** This repository represents our **Round 1 Idea Submission, Research Dossier, and Complete System Specification**. We have validated core pipeline feasibility (multimodal Indic parsing, dwell-time reading floor, seed calibration, and BSA 2023 legal dossier generation) through isolated technical POC experiments, and established the end-to-end blueprint ready to be built into an interactive working prototype during the on-site hackathon phase (Oct 9–10, 2026 at SSR Global Skills Park, Bhopal).

---

## 🔍 The Ground Reality of Madhya Pradesh Higher Education

State higher education evaluation in Madhya Pradesh operates at staggering scale under severe physical and economic constraints:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MADHYA PRADESH HIGHER EDUCATION SCALE                           │
├──────────────────────────┬──────────────────────────┬──────────────────────────────────┤
│    94 Universities       │   2,610+ Colleges        │      28.0 Lakh Students          │
│ (25 State, 55 Private,   │ (Govt, Aided & Private   │ (6th largest state higher-ed     │
│  2 Central, 12 National) │  across 55 districts)    │  enrollment in India - AISHE)    │
├──────────────────────────┴──────────────────────────┴──────────────────────────────────┤
│             ANNUAL VOLUME: OVER 3.0 CRORE HANDWRITTEN ANSWER BOOKLETS                  │
│       (2 Semesters × 5–6 Papers/Semester × 28 Lakh Students = ~30–33M Scripts)         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Recent Systemic Failures in MP University Evaluation

1. **Barkatullah University (BU Bhopal, 2024–2026):** Outsourcing result data processing led to an estimated **30% error rate**—present candidates marked absent, double-digit marks truncated to single digits, and over 10,000 student grievances requiring a high-level inquiry panel.
2. **Devi Ahilya Vishwavidyalaya (DAVV Indore):** Following an evaluation cycle where **3,800 out of 4,000 B.Ed students failed**, protests paralyzed administration. Subsequent tenders for digital On-Screen Marking (OSM) were deferred due to physical security concerns regarding **spine-cutting and sheetfed scanning** that risked page swapping.
3. **Vikram University (Ujjain):** A tabulation software glitch declared an MBA student with **1604 marks out of 1600** (100.25%), highlighting the absence of basic bounds validation.
4. **Rajiv Gandhi Proudyogiki Vishwavidyalaya (RGPV Bhopal):** Physical paper handling vulnerabilities were exposed when 9 sealed question paper bundles were stolen from the confidential examination branch.
5. **The Economic Toll on Students:** Universities collect **₹30 to ₹45 Crore annually** across MP in non-refundable revaluation fees (₹500 to ₹1,500/paper). Over 80% of these revaluations stem directly from totalization slips, unchecked pages, and evaluator fatigue.
6. **The Linguistic Gap:** In general degree streams (BA, B.Com, B.Sc, B.Ed, LLB), an estimated **60%+ of students write examinations in Hindi (Devanagari)**. Off-the-shelf OCR engines (Tesseract, PaddleOCR) exhibit Character Error Rates (CER) of **35%–55%** on unconstrained cursive Devanagari, rendering traditional text-first AI pipelines useless.

---

## 🏛️ Legal & Judicial Backing

PARIKSHAK-AI is specifically architected to comply with recent landmark legal standards in Madhya Pradesh and India:

- **June 2026 MP High Court Ruling (Jabalpur Division Bench):** While upholding digital evaluation for MPMSU, the High Court bench specifically recommended that **examiners evaluate scanned scripts using a digital stylus on touch-screen devices** to mimic conventional marking and eliminate ambiguous deductions.
- **Section 63, Bharatiya Sakshya Adhiniyam (BSA), 2023:** Having replaced Section 65B of the Indian Evidence Act on July 1, 2024, Section 63 governs the admissibility of electronic records. It mandates cryptographic hash values (**SHA-256**) and formal Schedule Part A/B certification for electronic evidence presented in court.
- **Ordinance No. 5 (MP Vishwavidyalaya Adhiniyam, 1973):** Governs the conduct of examinations, appointment of examiners, and evaluation center procedures across all state universities.

---

## 💡 Five Core Architectural Innovations

```
                                  PARIKSHAK-AI
                                5-PILLAR ARCHITECTURE
                                         │
    ┌──────────────────┬─────────────────┼─────────────────┬──────────────────┐
    ▼                  ▼                 ▼                 ▼                  ▼
[ Indic Vision ]  [ Blind Seed ]   [ Velocity Guard ]  [ Collusion ]    [ BSA Cryptographic ]
[  Multimodal  ]  [ Calibration]   [ Progressive    ]  [ Detection ]    [ Legal Dossier     ]
Direct Devanagari  Cambridge/IB    Cognitive Floor     Residual Index   Section 63 BSA 2023
No brittle OCR    In-flight seeds  T_min (No hard lock)Center-level     SHA-256 Merkle Proof
```

### 1. Direct Multimodal Vision Evaluation for Hindi & Hinglish
Bypasses the error-prone `Image → OCR → Text → LLM` pipeline entirely. Raw handwritten answer crops are processed directly via multimodal vision encoders (e.g., Gemini 2.0 Flash / Indic Multimodal VLMs), understanding unconstrained Devanagari script, regional idioms, and mixed Hinglish technical terminology (e.g., *"ट्रांजिस्टर का कलेक्टर-बेस जंक्शन रिवर्स बायस्ड होता है"*).

### 2. Blind Seed-Script Calibration (Cambridge / IB Quality Standard)
To eliminate subjective grading variance across thousands of evaluators, Chief Examiners pre-score 5 benchmark "Anchor Scripts" across performance bands. These are invisibly injected into live examiner queues. If an evaluator drifts beyond a configurable **±15% tolerance window**, the system detects evaluator drift in real-time and routes scripts for moderation before erroneous marks propagate.

### 3. Progressive 3-Tier Velocity Sentinel
Examiners in MP are paid ₹15–₹20 per booklet and face quotas that force 3-minute "glance-checking" on 36-page scripts. Instead of rigid countdown timers that provoke faculty strikes, PARIKSHAK-AI calculates an adaptive cognitive reading floor:
$$T_{min} = \left(\frac{N_{\text{words}}}{200} + 0.5 \times N_{\text{equations}} + 0.75 \times N_{\text{diagrams}}\right) \times 60 + 10\text{s}$$
Submissions significantly below $T_{min}$ trigger a **Progressive Friction Protocol**:
- **Tier 1 (Soft Nudge):** Warning banner identifying unverified pages.
- **Tier 2 (Touchpoint Gate):** Evaluator must touch at least one rubric verification chip before submitting.
- **Tier 3 (Silent Shadow Review):** Chronic speed-checkers have their batches routed for independent secondary verification without workflow interruption.

### 4. Center-Level Cohort Collusion Engine
To detect organized mass-copying at compromised rural examination centers, the system runs an offline forensic audit batch calculating the **Residual Plagiarism Index (RPI)** across student answer embeddings, flagging anomalous clusters that exhibit identical syntax, identical non-standard arguments, or identical arithmetic errors.

### 5. Section 63 BSA Cryptographic Defense Dossier
Every evaluated booklet automatically generates a court-admissible audit PDF containing:
- High-resolution scanned answer crops with examiner stylus annotations.
- Analytic rubric breakdown with extracted verbatim text justifications.
- Biometric dwell-time telemetry proving the examiner read the script.
- Cryptographic **SHA-256 Merkle root tree** and digital signatures complying with Section 63 of Bharatiya Sakshya Adhiniyam 2023.

---

## 🏗️ System Architecture & Bolt-On Integration

PARIKSHAK-AI is explicitly engineered **not** to replace MPOnline's existing systems, but to bolt onto them as a stateless cognitive microservice:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MP STATE DATA CENTRE (SDC) - BHOPAL                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [ EXISTING INFRASTRUCTURE ]                                                           │
│  ┌───────────────────────────────┐        ┌─────────────────────────────────────────┐  │
│  │ MPOnline ASP.NET Web Portal   │        │ Oracle 19c Enterprise Database Cluster  │  │
│  │ (User Auth, Center Mgmt)      │        │ (Tabulation Registers, Student Roster)  │  │
│  └──────────────┬────────────────┘        └────────────────────▲────────────────────┘  │
│                 │ Pre-Signed URLs                              │ Batch Commit          │
│                 ▼                                              │                       │
│  [ PARIKSHAK-AI BOLT-ON MICROSERVICE ]                         │                       │
│  ┌───────────────────────────────┐        ┌────────────────────┴────────────────────┐  │
│  │ MinIO / S3 Object Storage     │───────▶│ Apache Kafka / RabbitMQ Event Queue     │  │
│  │ (Encrypted 300 DPI Scans)     │        │ (Topic: `exam.evaluation.events`)       │  │
│  └──────────────┬────────────────┘        └────────────────────▲────────────────────┘  │
│                 │                                              │                       │
│                 ▼                                              │                       │
│  ┌─────────────────────────────────────────────────────────────┴────────────────────┐  │
│  │ FastAPI Cognitive Engine (Python 3.11 / Pydantic v2)                             │  │
│  │ • Local DocLayout-YOLO: Question-Answer Crop Segmentation                        │  │
│  │ • Multimodal Vision Inference: Gemini 2.0 Flash / Indic VLM                      │  │
│  │ • Velocity Sentinel & Seed Drift Analyzers                                       │  │
│  │ • Section 63 BSA Merkle PDF Compiler (ReportLab / WeasyPrint)                   │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Why This Design Protects MPOnline's Investments
- **Zero Database Locking:** Scanned booklets never hit Oracle transaction tables. Uploads use 120-second pre-signed S3 URLs.
- **Asynchronous Decoupling:** Evaluator marks are emitted into Kafka and batch-synced to the Oracle Tabulation Register during low-traffic windows.
- **Non-Destructive Scanning:** Compatible with overhead V-cradle book scanners (e.g., CZUR M3000 Pro / Zeutschel OS 12002), eliminating the thread-cutting and spine destruction that halted DAVV's digital evaluation pilot.

---

## 💻 What We Can Build: Hackathon Prototype Plan

During the upcoming hackathon development sprint, Team eMitra will implement and demonstrate the core interactive prototype:

```
Mphack/
├── README.md                           # Master Architecture & Project Documentation
├── LICENSE                             # Apache 2.0 Open Source License
├── .gitignore                          # Clean repository hygiene
│
├── submissions/                        # Complete 10-Document Portal Submission Dossier
│   ├── 01_Solution_Synopsis_Executive_Summary.md
│   ├── 02_Solution_Presentation.md
│   ├── 03_Problem_Statement_Proposed_Solution.md
│   ├── 04_Innovation_Differentiation_Note.md
│   ├── 05_Impact_Benefits_Document.md
│   ├── 06_Implementation_Feasibility_Plan.md
│   ├── 07_Technology_Architecture_Technical_Approach.md
│   ├── 08_Prototype_Demo_Proof_Of_Concept.md
│   ├── 09_Code_Repository_Details.md
│   └── 10_Why_Should_This_Solution_Be_Selected_3000_Chars.txt
│
├── backend/                            # FastAPI Cognitive Microservice (Sprint Scope)
│   ├── main.py                         # App entrypoint & CORS middleware
│   ├── requirements.txt                # Python dependencies
│   ├── core/
│   │   ├── config.py                   # Environment settings & cloud configurations
│   │   ├── grading_engine.py           # Gemini 2.0 Flash multimodal rubric evaluation
│   │   ├── velocity_sentinel.py        # Reading floor T_min algorithm & tier logic
│   │   ├── seed_calibration.py         # In-flight anchor script drift detector
│   │   └── rti_dossier.py              # Section 63 BSA Merkle tree & PDF compiler
│   └── api/
│       ├── routes_grading.py           # Endpoints for question pre-scoring
│       └── routes_examiner.py          # Examiner workspace session handlers
│
└── frontend/                           # React 18 Examiner Workspace PWA (Sprint Scope)
    ├── package.json                    # Dependencies
    ├── vite.config.ts                  # Vite build configuration
    └── src/
        ├── App.tsx                     # Main application layout
        └── components/
            ├── AnswerViewer.tsx        # Fabric.js stylus annotation canvas
            ├── RubricCopilot.tsx       # AI evidence & 1-click accept panel
            └── VelocityAlert.tsx       # 3-Tier progressive friction modal
```

### Demonstration Flow Planned for Hackathon Jury
1. **Act 1: The Bilingual Ground Reality** — Upload a handwritten Hindi university answer sheet; watch the multimodal engine extract candidate quotes and recommend rubric-aligned marks in ~1.5s; approve with digital stylus.
2. **Act 2: The Evaluator Sentinel** — Attempt a 6-second rapid submission on a 4-page answer to trigger the Progressive Velocity Alert; enter an anomalous score on an invisible Seed Script to trigger evaluator drift moderation.
3. **Act 3: The 1-Click Court Defense** — Click "Generate RTI Defense Dossier" to produce a Section 63 BSA compliant PDF with cryptographic SHA-256 hashes in under 2 seconds.

---

## 💰 Feasibility & Fiscal Economics

### AI Layer Unit Economics (Gemini 2.0 Flash)
- **Token Pricing:** \$0.10 / 1M prompt tokens, \$0.40 / 1M output tokens.
- **Booklet Profile:** 6 questions $\times$ 1,800 input tokens = 10,800 tokens (\$0.00108); 6 questions $\times$ 350 output tokens = 2,100 tokens (\$0.00084).
- **Raw AI Token Cost:** **₹0.162 INR** per 36-page booklet.
- **Total Incremental AI Infrastructure Cost:** Factoring in S3 object storage (162 TB state-wide), egress networking, and SDC compute overhead, the incremental AI layer costs **~₹1.14 per booklet**.

### University Net Operating Balance Sheet (30 Lakh Scripts Model)
| Financial Stream | Legacy Model | With PARIKSHAK-AI | Net Impact |
|:---|:---:|:---:|:---:|
| Revaluation Fee Revenue | +₹35.00 Cr | +₹5.00 Cr | -₹30.00 Cr (returned to students) |
| Physical Answer Book Logistics | -₹12.00 Cr | -₹5.00 Cr | **+₹7.00 Cr Savings** |
| RTI & High Court Legal Defense | -₹3.50 Cr | -₹0.50 Cr | **+₹3.00 Cr Savings** |
| Total Net University Position | High Friction | Sustainable | **Surplus maintained; student trust restored** |

---

## 📑 Complete Portal Submission Dossier

All 10 documents prepared for the MPOnline Hackathon portal are available in the [`submissions/`](./submissions/) directory:

| # | Document Title | Portal Field | Description |
|:---:|:---|:---|:---|
| **01** | [Solution Synopsis / Executive Summary](./submissions/01_Solution_Synopsis_Executive_Summary.md) | `1. Solution Synopsis *` | 2-page executive summary covering MP higher education context and core solutions |
| **02** | [Solution Presentation Deck](./submissions/02_Solution_Presentation.md) | `2. Solution Presentation *` | 12-slide comprehensive pitch deck specification with slide-by-slide notes |
| **03** | [Problem Statement & Proposed Solution](./submissions/03_Problem_Statement_Proposed_Solution.md) | `3. Problem Statement & Proposed Solution *` | In-depth white paper detailing root causes, systemic failures, and technical response |
| **04** | [Innovation & Differentiation Note](./submissions/04_Innovation_Differentiation_Note.md) | `4. Innovation & Differentiation Note *` | Detailed breakdown of 5 core innovations and competitor comparison matrix |
| **05** | [Impact & Benefits Document](./submissions/05_Impact_Benefits_Document.md) | `5. Impact & Benefits *` | Quantified social, educational, and fiscal balance sheet impact metrics |
| **06** | [Implementation & Feasibility Plan](./submissions/06_Implementation_Feasibility_Plan.md) | `6. Implementation & Feasibility Plan *` | 4-phase rollout roadmap, infrastructure sizing, and risk mitigation matrix |
| **07** | [Technology Architecture & Technical Approach](./submissions/07_Technology_Architecture_Technical_Approach.md) | `7. Technology Architecture & Technical Approach *` | Complete 5-stage architecture specification, data flows, and security protocols |
| **08** | [Prototype / Demo / Proof of Concept](./submissions/08_Prototype_Demo_Proof_Of_Concept.md) | `8. Prototype / Demo / Proof of Concept *` | Prototype technical specification, 3-act demo workflow, and validated POC code |
| **09** | [Code Repository Details](./submissions/09_Code_Repository_Details.md) | `9. Code Repository URL *` | Repository specification, architecture quickstart, and file catalog |
| **10** | [Why Should This Solution Be Selected](./submissions/10_Why_Should_This_Solution_Be_Selected_3000_Chars.txt) | `10. Why should this solution be selected *` | 2,953-character summary pitch formatted specifically for the portal character limit |

---

## 👥 Team Information

* **Team Name:** eMitra
* **Hackathon:** MPOnline Idea & Innovation Hackathon 2026
* **Organizers:** MPOnline Limited (Joint Venture of MPSEDC, Govt. of MP & Tata Consultancy Services)
* **Challenge:** Challenge 03 — AI-Driven Examination & On-Screen Marking Transformation
* **Track:** Technical Track
* **Grand Finale:** October 9–10, 2026 at Sant Shiromani Ravidas Global Skills Park, Bhopal

---

## 📄 License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
