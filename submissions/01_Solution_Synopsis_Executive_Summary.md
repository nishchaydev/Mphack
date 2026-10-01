# DOCUMENT 1: SOLUTION SYNOPSIS / EXECUTIVE SUMMARY

**Project Title:** PARIKSHAK-AI (परीक्षक-AI) — Cognitive Copilot & Fairness Architecture for On-Screen Marking  
**Challenge:** Challenge 03: AI-Driven Examination & On-Screen Marking Transformation  
**Organized by:** MPOnline Limited & Department of Higher Education, Government of Madhya Pradesh  
**Team Name:** eMitra (Technical Track)  
**Submission Date:** October 2026  

---

### 1. Executive Context & The Madhya Pradesh Examination Crisis
Higher education across Madhya Pradesh constitutes one of India's largest state academic ecosystems, enrolling over **28.0 Lakh students** across **2,610+ affiliated colleges** and **~94 universities** (AISHE Data). Each semester, this apparatus processes between **1.4 Crore and 1.7 Crore handwritten answer sheets** (~3.0+ Crore annually). 

Despite pilot On-Screen Marking (OSM) initiatives, the evaluation system faces recurring administrative crises:
- **Catastrophic Quality Failures:** At **Barkatullah University (BU), Bhopal**, discrepancies were suspected in around **30% of results** processed by an outsourced agency: students who sat the exam were marked absent, given zero marks or shown subjects they never took, and nearly **10,000 complaints** followed. At **Devi Ahilya Vishwavidyalaya (DAVV), Indore**, only about **43% of ~7,200 B.Ed candidates passed** a first-semester exam, and allegations of faulty evaluation forced an expert re-evaluation of answer sheets.
- **The "3-Minute Valuation" Reality:** Between 15,000 and 25,000 empanelled faculty examiners are paid a meager **₹12 to ₹20 per answer booklet**. Mandated to evaluate 40–50 scripts of 36 pages each within a 4-hour window, examiners spend barely **180–300 seconds per booklet**, resulting in superficial "glance-checking", severe cognitive fatigue, and arbitrary marking.
- **Result Paralysis & The Revaluation Toll:** Delays range from **3 to 14 months**, forcing final-year students to forfeit campus placement offers, UPSC/MPPSC recruitment cut-offs, and postgraduate admissions. Concurrently, universities collect an estimated **₹30 to ₹45 Crore annually** in non-refundable revaluation fees from distressed students protesting flawed grading.

---

### 2. The Solution: PARIKSHAK-AI (परीक्षक-AI)
**PARIKSHAK-AI** is an enterprise-grade **Human-in-the-Loop (HITL) Cognitive Copilot** specifically engineered to augment MPOnline’s established examination ecosystem. Rather than attempting to replace human faculty—which violates statutory university ordinances and UGC norms—PARIKSHAK-AI serves as a transparent cognitive assistant that pre-reads, rubrics-aligns, and calibrates every script while preserving final decision authority with human examiners.

```
Scanned Booklets (MPOnline SDC)
        │
        ▼
[ Multimodal Vision & Rubric Engine ] ──► Pre-scores criteria & extracts textual evidence
        │
        ▼
[ Examiner Copilot Workspace ]        ──► Stylus annotation, 1-click Accept / Modify / Override
        │
        ├──► [ Integrity Sentinel ]     (Blind Seed Injection, Dwell-Time Floor, Entropy Check)
        ├──► [ Question Forensics ]     (Item Discrimination & Ambiguity Flags)
        └──► [ Legal Audit Engine ]     (1-Click Cryptographic RTI Defense Dossier)
```

---

### 3. Five Transformative Innovations

1. **Native Indic Multimodal Ingestion (Devanagari + Hinglish):**  
   An estimated 60%+ of MP state university students (BA, B.Com, B.Sc, B.Ed, LLB streams) write in Hindi. Traditional OCR pipelines fail because segmentation errors cascade into grading errors. PARIKSHAK-AI uses end-to-end multimodal vision to evaluate handwritten Hindi, English, and technical drawings directly against analytic rubrics without brittle OCR dependencies.

2. **Blind Seed-Script Calibration (Cambridge / IB Quality Standard):**  
   To eliminate inter-rater variance, Chief Examiners pre-score 5 "Anchor Scripts" across performance bands. These are invisibly interspersed into examiner queues. If an examiner’s mark drifts more than 15% of the maximum marks from the Chief Examiner’s mark, the CoE is alerted and the examiner’s next scripts are silently routed to the Head Examiner before erroneous marks propagate.

3. **Cognitive Velocity & Dwell-Time Sentinel:**  
   Sets a reading floor for each answer from its length, equations and diagrams (\(T_{min} = (N_{words}/200 + 0.5\,N_{eq} + 0.75\,N_{diag}) \times 60 + 10\text{s}\)). A rushed submission first gets a soft prompt, then the examiner must check at least one rubric criterion; repeated speed-checking is silently routed for a second reading. The examiner is never locked out.

4. **Live Question Paper Psychometric Forensics:**  
   Computes item-analysis statistics (difficulty and point-biserial discrimination) across the student cohort as marks arrive. If Question 3(b) produces an 85% failure rate among top-quartile students, it is immediately flagged as ambiguous or out-of-syllabus, enabling the Controller of Examinations (CoE) to issue standard moderation before results publish.

5. **1-Click RTI Cryptographic Justification Dossier:**  
   Following the June 2026 MP High Court judgment that upheld digital evaluation and recommended stylus-based marking, PARIKSHAK-AI generates an instant tamper-evident PDF showing the student's answer with the examiner's annotations, the model key, the evidence behind every mark, examiner timestamps, and a signed SHA-256 Merkle root that supports a certificate under Section 63 of the Bharatiya Sakshya Adhiniyam 2023.

---

### 4. Feasibility, Cloud Sovereignty & Economics
- **Non-Invasive Integration:** Seamlessly integrates with MPOnline's existing ASP.NET / Oracle examination portal via secure REST APIs and pre-signed storage URLs without altering core ERP modules.
- **Affordable Unit Economics:** AI inference costs an estimated **₹0.5–₹3 per booklet** at current Gemini Flash-Lite/Flash list prices, a fraction of current revaluation overhead. Our proof of concept logs the real token count and cost of every call.
- **Compliance by Design:** Aligned with **NEP 2020 (Sections 4.34–4.37)** and designed for the **DPDP Act 2023** and **MeghRaj / MP State Data Centre** requirements; in production, inference runs on a model hosted in the State Data Centre or an India-region cloud.
- **Working Proof of Concept:** The examiner workspace, AI pre-read of Hindi/English answers, reading-time check, blind seed scripts and signed audit dossier already run (repository: https://github.com/nishchaydev/Mphack).
