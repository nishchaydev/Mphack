# DOCUMENT 2: SOLUTION PRESENTATION (SLIDE DECK SPECIFICATION)

**Project Name:** PARIKSHAK-AI (परीक्षक-AI)  
**Subtitle:** Cognitive Copilot & Fairness Architecture for On-Screen Marking in MP Universities  
**Challenge:** Challenge 03 — AI-Driven Examination & On-Screen Marking Transformation  
**Track:** Technical Track | **Team Name:** eMitra  

---

### SLIDE 1: Title & Executive Vision
* **Title:** PARIKSHAK-AI (परीक्षक-AI)
* **Tagline:** Bhashini-Powered Cognitive Copilot & Quality Assurance Architecture for On-Screen Marking
* **Target Environment:** MPOnline Portal & 94 State & Private Universities across Madhya Pradesh
* **Core Philosophy:** *Human-in-the-Loop AI* — AI empowers and calibrates the examiner; final evaluative authority remains strictly with faculty.
* **Presented by:** Team eMitra (Technical Track)

---

### SLIDE 2: The Operational Magnitude of Madhya Pradesh Higher Education
* **Student Body:** **28,00,165 Enrolled Students** (AISHE Data — Ranked Top 6 in India).
* **Institutional Network:** **94 Universities** (25 State Public, 55 Private, 2 Central, 12 National/Specialized) and **2,610+ Affiliated Colleges**.
* **Examination Volume:** **1.4 to 1.7 Crore answer sheets per semester cycle** → Over **3.0 to 3.4 Crore booklets evaluated annually**.
* **Faculty Evaluator Workforce:** **15,000 to 25,000 examiners** mobilized every 6 months.
* **The Valuation Reality:** Examiners are compensated just **₹12 to ₹20 per booklet**.
* **The 3-Minute Trap:** To clear daily quotas (40–50 copies), examiners spend only **180 to 300 seconds per 36-page script**, making detailed reading biologically impossible.

---

### SLIDE 3: Ground Reality — Recent Systemic Failures in MP
* **Barkatullah University (BU), Bhopal (Aug 2026):** Outsourced evaluation vendor triggered a **30% error rate across published results**; 10,000+ student grievances; attended students marked "Absent"; single-digit truncations.
* **Devi Ahilya Vishwavidyalaya (DAVV), Indore (2025–2026):** **3,800 out of 4,000 B.Ed candidates failed** due to uncalibrated grading; MBA digital evaluation stalled after CBSE tender security red flags.
* **Vikram University, Ujjain:** Processing anomalies resulted in an MBA student officially awarded **1604 marks out of 1600**.
* **Result Delays:** Average turnaround of **3 to 14 months** across regional universities (BU, Jiwaji, RDVV), causing revoked corporate job offers and missed postgraduate admission deadlines.
* **The Revaluation Levy:** Students in MP pay **₹30 to ₹45 Crore annually** in non-refundable revaluation fees to fix evaluator oversights.

---

### SLIDE 4: Challenge 03 — 100% Requirement Coverage Matrix
| # | Challenge 03 Requirement | PARIKSHAK-AI Architectural Response |
|---|-------------------------|--------------------------------------|
| 1 | AI-Assisted Answer Evaluation Support | Multimodal Rubric Engine (Step-wise evidence extraction & score suggestions) |
| 2 | Detection of Unchecked Answers / Anomalies | Computer Vision Page Traversal & Blank Page Enforcer |
| 3 | Examiner Performance Analytics | Cognitive Velocity Profiling & Dwell-Time Tracking |
| 4 | Smart Moderation Workflows | Blind Seed-Script Injection & Automated Variance Routing |
| 5 | Handwriting Recognition Assistance | Native Devanagari, English & Hinglish Multimodal Transcription |
| 6 | AI-Generated Evaluation Summaries | Student-Specific Competency & Misconception Diagnostics |
| 7 | Real-Time Evaluation Dashboards | Controller of Examinations (CoE) Live State-wide Command Center |
| 8 | Scoring Malpractice / Bias Detection | Shannon Entropy Profiling & Isolation Forest Anomaly Detection |
| 9 | Faster Result Processing | Zero-Touch Auto-Tabulation directly into MPOnline ERP |
| 10| Mobile-Enabled Examiner Interface | Touch & Stylus Responsive PWA (MP High Court June 2026 Mandate) |

---

### SLIDE 5: Solution Architecture — The 4 Core Pillars
```
┌────────────────────────────────────────────────────────────────────────┐
│                          PARIKSHAK-AI ENGINE                           │
├────────────────────────────────────────────────────────────────────────┤
│  [ PILLAR 1: SMART INGESTION ]                                         │
│  • Barcode/QR Anonymization Tokenizer • Missing Page & Skew Detection  │
│  • Native Multimodal Ingestion (Devanagari, English, Mixed Diagrams)   │
├────────────────────────────────────────────────────────────────────────┤
│  [ PILLAR 2: EXAMINER COGNITIVE COPILOT ]                             │
│  • Decomposed Analytic Rubric Pre-Scoring • Step-Wise Evidence Quotes   │
│  • Stylus & Canvas Annotation Palette • 1-Click Accept/Modify/Override │
├────────────────────────────────────────────────────────────────────────┤
│  [ PILLAR 3: INTEGRITY & CALIBRATION SENTINEL ]                        │
│  • Blind Seed Script Injection (Cambridge Standard)                    │
│  • Cognitive Reading Floor (Velocity Anomaly Guard)                    │
│  • Shannon Entropy Rubber-Stamp Detector (H(X) < 1.5 bits)             │
├────────────────────────────────────────────────────────────────────────┤
│  [ PILLAR 4: GOVERNANCE & LEGAL AUDIT COMMAND CENTER ]                 │
│  • Live CoE Bottleneck Heatmap • Real-Time Question Paper Forensics    │
│  • 1-Click Cryptographic RTI Defense Dossier (SHA-256 Verified)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

### SLIDE 6: Breakthrough USP 1 & 2 — Multimodal Indic & Seed Calibration
* **USP 1: Native Multimodal Ingestion for Hindi / Hinglish**
  * *The Trap:* Standard OCR (PaddleOCR/Tesseract) achieves only 45–65% accuracy on messy handwritten Devanagari; OCR errors cascade into hallucinated grading.
  * *Our Innovation:* End-to-end vision-language reasoning ingests raw handwritten strokes directly, understanding Hindi idioms, technical equations, and circuit schematics without brittle OCR intermediaries.
* **USP 2: Blind Seed-Script Calibration (First Time in Indian State Universities)**
  * *Mechanism:* Chief Examiners pre-score 5 benchmark scripts (Exemplar, Above Average, Average, Borderline, Poor).
  * *Execution:* Seed scripts are invisibly inserted into examiner batches.
  * *Drift Correction:* If an examiner marks a calibrated 10-mark question at 17/20 (exceeding ±15% tolerance), the system pauses marking and launches a rubric refresher.

---

### SLIDE 7: Breakthrough USP 3 & 4 — Cognitive Velocity & Question Forensics
* **USP 3: Cognitive Velocity Floor & Rubber-Stamp Detection**
  * *Velocity Floor:* Implements physiological reading speed floor: \(T_{min} = \frac{\text{Word Count}}{200} \times 60 + 5\text{s}\).
  * *Enforcement:* Submitting an evaluation for a 500-word answer in under 15 seconds triggers a **Speed Anomaly Lock**, redirecting the paper to a moderator.
  * *Entropy Check:* Evaluates the Shannon Entropy of awarded mark distributions. An examiner awarding identical 14/20 marks across 50 scripts exhibits \(H(X) < 1.0\), immediately flagging "rubber-stamping."
* **USP 4: Live Question Paper Psychometric Forensics**
  * *Item Discrimination:* Real-time computation of Point-Biserial Correlation (\(r_{pbis}\)) and Difficulty Indices across candidate cohorts.
  * *Proactive Moderation:* If a question demonstrates severe negative discrimination (top-performing candidates failing disproportionately), the CoE is alerted to ambiguous phrasing or syllabus mismatch *before* result publication, averting statewide student unrest.

---

### SLIDE 8: Breakthrough USP 5 — 1-Click RTI Defense Dossier
* **Legal Context:** MP High Court Division Bench (June 2026) mandated transparent digital evaluation protocols with verifiable examiner annotations.
* **The Capability:** Generates a tamper-evident, court-ready verification PDF in under 2 seconds.
* **Contents of Dossier:**
  1. High-resolution student script with anonymized fictitious identifier.
  2. Model marking scheme and analytic rubric criteria.
  3. Step-by-step awarded marks with exact quoted evidence from student text.
  4. Examiner dwell-time per page, timestamp log, and digital signature.
  5. SHA-256 cryptographic hash verifying document immutability.
* **Administrative Impact:** Reduces university RTI response handling from 45 days to instantaneous dispatch, terminating frivolous litigation.

---

### SLIDE 9: Technology Stack & Non-Invasive MPOnline Integration
* **Integration Philosophy:** *Zero Disturbance to MPOnline ERP.*
* **MPOnline Core:** ASP.NET Core / Java Spring Boot backend on Oracle Enterprise DB at MP State Data Centre (SDC) Bhopal.
* **PARIKSHAK-AI Bolt-On:** Operates as a stateless microservice communicating over encrypted mTLS REST APIs.
* **Data Flow:** Scanned booklet images accessed via short-lived, pre-signed HTTPS URLs; evaluated marks and audit logs returned as structured JSON payloads for automated tabulation.
* **Tech Stack:**
  * *Cognitive Engine:* Python 3.11, FastAPI, Multimodal Vision LLM (Gemini 2.0 Flash / Pro).
  * *Analytics & ML:* scikit-learn (Isolation Forest), SciPy (Shannon Entropy, K-S Tests).
  * *Frontend Workspace:* React 18, TypeScript, Tailwind CSS, HTML5 Canvas / Fabric.js (Stylus & Touch enabled).
  * *Storage & Ledger:* PostgreSQL 16 (JSONB Rubrics), Redis Cache, MinIO / S3 Encrypted Storage.

---

### SLIDE 10: Economics, Measurable Impact & Policy Alignment
* **Inference Cost:** **₹1.14 per 36-page booklet** (6 questions @ ₹0.19/call via multimodal token pricing) — vastly lower than administrative revaluation overhead.
* **Turnaround Reduction:** Results published in **15 to 30 days** (compared to current 3 to 14 months).
* **Grievance Mitigation:** Anticipated **60% to 70% decrease in revaluation requests**, saving students ₹18–₹27 Crore in distress fees annually.
* **National Policy Compliance:**
  * *NEP 2020 (Sections 4.34–4.37 & 23.2):* Outcome-based, competency-aligned evaluation with formative diagnostic reporting.
  * *DPDP Act 2023:* 100% data residency within India; strict role-based data minimization.
  * *MeghRaj GI Cloud Standards:* Ready for deployment on MeitY-empanelled GovCloud or MP SDC.

---

### SLIDE 11: Phased Implementation Roadmap
* **Phase 1: Hackathon Prototype (October 2026)**
  * Fully functional bilingual multimodal grading engine, speed violation detector, and RTI dossier generator.
* **Phase 2: Single-University Pilot (Q1 2027)**
  * Controlled 25,000-script pilot at DAVV Indore or BU Bhopal for professional semester exams (MBA / B.Tech).
  * CERT-In empanelled security VAPT and STQC compliance audit.
* **Phase 3: MPOnline State Integration (Q2–Q3 2027)**
  * Integration into MPOnline centralized exam portal across top 5 state universities (~50 Lakh scripts).
* **Phase 4: Full State Rollout (2028)**
  * Complete operational coverage across all 25 State Public Universities and 3.0+ Crore annual scripts.

---

### SLIDE 12: Why Team eMitra Deserves Selection
1. **100% Coverage of Challenge 03:** Direct, production-ready engineering for all 10 problem requirements.
2. **Built for MP, Not Silicon Valley:** Solves real regional crises (BU Bhopal vendor collapse, DAVV halt, Devanagari handwriting, ₹15 examiner remuneration).
3. **Legally Defensible & Human-Centric:** Keeps university professors in control while providing an impenetrable shield against RTI appeals and judicial disputes.
4. **Feasible & Economical:** Bolt-on API architecture costing just ₹1.14 per script, requiring zero downtime or overhaul of MPOnline's existing ERP investments.
