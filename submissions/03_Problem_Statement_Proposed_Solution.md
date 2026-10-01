# DOCUMENT 3: PROBLEM STATEMENT & PROPOSED SOLUTION

**Project Name:** PARIKSHAK-AI (परीक्षक-AI)  
**Challenge:** Challenge 03 — AI-Driven Examination & On-Screen Marking Transformation  
**Track:** Technical Track | **Team Name:** eMitra  

---

## 1. Comprehensive Problem Statement: The Examination Crisis in Madhya Pradesh

Higher education in Madhya Pradesh represents one of India’s most expansive state university frameworks. According to AISHE data, the state accommodates over **28.0 Lakh enrolled students** across **2,610+ affiliated colleges** and **~94 universities** (25 State Public Universities, 55 State Private Universities, 2 Central Universities, and specialized institutes). 

Every academic year entails two primary examination cycles (Odd Semesters: Nov–Jan; Even Semesters: May–July), producing an overwhelming aggregate of **3.0 to 3.4 Crore handwritten answer booklets** (averaging 32 to 40 pages per booklet).

### The Structural Vulnerabilities of the Current Examination Lifecycle

#### A. The Collapse of Outsourced Manual & Vendor Workflows (The BU Bhopal Debacle)
In August–September 2026, Barkatullah University (BU), Bhopal experienced an administrative catastrophe when its outsourced examination evaluation and result-processing vendor (Infinity Certification Services) released results marred by an estimated **30% error rate**. Over 10,000 formal student grievances overwhelmed the university:
- Enrolled students who physically sat for the exams and signed invigilation rolls were arbitrarily marked **"ABSENT" (Fail)** because vendor databases decoupled paper attendance sheets from scanned award lists.
- Tens of thousands of marks were corrupted through data-entry truncations—evaluators awarding 45 or 52 found their entries keyed in as single-digit scores (4 or 5).
- At Vikram University, Ujjain, data misalignment awarded an MBA candidate an absurd score of **1604 out of 1600**, completely undermining institutional credibility.

#### B. The Severe Operational Economics of Faculty Valuation
State universities empanel between **15,000 and 25,000 college and university teachers** per evaluation window. Under ordinances such as DAVV Ordinance No. 5 and RGPV statutory guidelines:
- Evaluator compensation is pegged at an austere **₹12 to ₹18 per booklet** for undergraduate humanities/commerce and **₹20 to ₹25 per booklet** for engineering and professional courses.
- An examiner spending 4–5 hours evaluating 40 answer books earns approximately ₹600 to ₹800—often paid after 6 to 12 months of bureaucratic delays.
- A standard booklet contains 32 to 36 pages of complex handwritten prose, mathematical derivations, or architectural schematics. Evaluators are pressured to clear daily quotas of 40 to 60 books within a 3 to 4 hour evaluation center shift.
- **The Mathematical Impossibility:** Evaluating a 36-page script in 180 to 240 seconds allows barely **5 to 7 seconds per page**. Evaluators cannot cognitively read the script. They resort to **"glance-checking"**—evaluating based on penmanship, paragraph length, and apparent neatness. By 3:00 PM, evaluator cognitive fatigue leads to severe central-tendency bias (assigning uniform passing scores of 12–15 out of 20 to every candidate).

#### C. Systemic Result Backlogs & Career Disruption
University ordinances mandate result declarations within 30 to 45 days of the final examination. In reality, examination branches at BU Bhopal, Jiwaji University Gwalior, RDVV Jabalpur, and APSU Rewa report result backlogs spanning **3 to 14 months**. 
- Final-year students miss corporate onboarding cut-offs at IT services and core manufacturing firms (which strictly mandate zero active backlogs at joining).
- Candidates are barred from state public service examinations (MPPSC State Services) or national tests (UPSC, Banking, GATE) due to unavailable provisional degree certificates.

#### D. The Predatory Revaluation Industry
Because first-tier valuation is plagued by glance-checking and transcription blunders, an estimated **6% to 10% of candidates apply for revaluation and challenge evaluation**. Universities in MP charge between **₹500 and ₹1,500 per subject** for revaluation and copy inspection. Across 7 major state universities (DAVV, BU, RGPV, Jiwaji, Vikram, RDVV, APSU), an estimated **6 Lakh to 9 Lakh revaluation requests** are processed annually, generating **₹30 to ₹45 Crore in non-refundable fee revenue**. Students frequently see failing grades ("F", 14/70) jump to outstanding grades ("A", 58/70) upon paying revaluation fees—irrefutable evidence of arbitrary first-tier evaluation.

#### E. Security Paralysis Post-CBSE OSM 2026 Controversy
The national CBSE On-Screen Marking controversy in 2026—where security researcher Nisarga Adhikary uncovered critical Broken Object Level Authorization (BOLA/IDOR) vulnerabilities, exposed cloud storage buckets, and missing authentication controls—sent shockwaves through MP's higher education leadership. In September 2026, **DAVV Indore officially halted its planned digital evaluation rollout** for MBA courses, citing concerns over vendor security, booklet spine-unbinding tampering, and lack of verifiable audit trails.

---

## 2. The Proposed Solution: PARIKSHAK-AI (परीक्षक-AI)

**PARIKSHAK-AI** is a cloud-native, Human-in-the-Loop (HITL) Cognitive Evaluation Platform specifically engineered to plug into MPOnline’s state examination portal. It addresses the crisis not by attempting to replace university professors, but by providing an intelligent cognitive assistant that shields examiners from burnout, standardizes grading rubrics, prevents speed-checking anomalies, and produces ironclad legal documentation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PARIKSHAK-AI CORE WORKFLOW                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ Step 1: Scan & Anonymize ]                                               │
│  Industrial Scanner → MP SDC Secure Ingestion → Fictitious Code Mapping     │
│                                                                             │
│  [ Step 2: Cognitive Pre-Evaluation ]                                       │
│  Multimodal Vision Model (Gemini Flash) ingests raw scan + marking rubric.  │
│  Extracts student textual/diagrammatic evidence; pre-populates marks.       │
│                                                                             │
│  [ Step 3: Examiner Interactive Evaluation ]                                │
│  Faculty logs in via 2FA; views scan alongside AI rubric suggestions.       │
│  Annotates using digital stylus/touchpad; 1-click Accept / Modify / Override│
│                                                                             │
│  [ Step 4: Autonomous Quality Assurance ]                                   │
│  • Blind Seed Script Injection (Calibrates examiner consistency)            │
│  • Dwell-Time Velocity Sentinel (Blocks <15s speed-checking)                │
│  • Shannon Entropy Monitor (Flags uniform rubber-stamp grading)             │
│                                                                             │
│  [ Step 5: Psychometric Forensics & Tabulation ]                            │
│  • Live Item Response Theory (IRT) question ambiguity detection             │
│  • Direct API push to MPOnline Tabulation Register                          │
│  • 1-Click Cryptographic RTI Justification Dossier Generation               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Direct Mapping to Challenge 03 Requirements

The table below demonstrates how PARIKSHAK-AI directly satisfies every single feature specified in the MPOnline Idea Hackathon Challenge 03 mandate:

| # | Challenge 03 Requirement | Current Gap in MP Universities | PARIKSHAK-AI Solution & Technical Approach |
|---|-------------------------|--------------------------------|--------------------------------------------|
| 1 | **AI-assisted answer evaluation support** | Manual glance-checking in 180s; no marking guidance. | Decomposed Analytic Rubric Engine provides question-by-question scoring recommendations with quoted textual justifications. |
| 2 | **Automated detection of unchecked answers / marking anomalies** | Unchecked pages cause thousands of failing grades annually. | Computer vision page traversal detector verifies all question blocks are assessed; enforces mandatory blank-page watermarking. |
| 3 | **Examiner performance analytics** | Zero visibility into evaluator pacing or fatigue. | Real-time telemetry tracking: scripts evaluated per hour, variance from cohort average, dwell-time distribution across booklet pages. |
| 4 | **Smart moderation workflows** | Arbitrary 5% manual sampling by Head Examiners. | **Blind Seed-Script Injection:** Invisibly inserts pre-calibrated anchor scripts; flags evaluator drift if deviation exceeds ±15%. |
| 5 | **Handwriting recognition assistance** | 60%+ Hindi scripts illegible to standard OCR engines. | End-to-end multimodal vision reasoning processes cursive Devanagari, English, and Hinglish directly from raw imagery. |
| 6 | **AI-generated evaluation summaries** | Marksheets display single numbers with zero diagnostic feedback. | Synthesizes individual student diagnostic reports mapping strengths and conceptual misconceptions aligned with NEP 2020 OBE rubrics. |
| 7 | **Real-time evaluation dashboards** | Controllers of Examination (CoEs) rely on weekly phone calls. | Live State Command Center displays subject-wise completion rates, bottleneck alerts, examiner speed heatmaps, and projected result dates. |
| 8 | **Malpractice / unusual scoring pattern detection** | Unscrupulous examiners award identical passing marks (14/20). | **Shannon Entropy Engine:** Computes score dispersion entropy (\(H(X) < 1.5\)); Isolation Forest flags outlier examiner cohorts. |
| 9 | **Faster result processing** | Manual transcription from paper award lists takes 2–4 months. | Zero-touch API ingestion into MPOnline database immediately upon final examiner submission; instant auto-totalling. |
| 10| **Mobile-enabled examiner interface** | Evaluators bound to obsolete desktop PCs in crowded halls. | Responsive Progressive Web App (PWA) with native stylus and touch support, fully compliant with June 2026 MP High Court guidelines. |

---

## 4. Key Differentiators: Why This Solves the Ground Problem

1. **Non-Invasive Architecture:** We do not propose replacing MPOnline's existing investment in ASP.NET / Oracle ERP. PARIKSHAK-AI acts as a stateless intelligence microservice that ingests scanned images and outputs validated marks.
2. **Respect for Legal Realities:** Indian higher education law requires degree conferral to rest upon human academic judgment. By maintaining strict Human-in-the-Loop workflows, our solution avoids litigation while cutting cognitive fatigue by 60%.
3. **Economical Viability:** At ₹1.14 per evaluated booklet, the system pays for itself multiple times over by eliminating paper logistics, valuation center allowances, and revaluation administrative burdens.
