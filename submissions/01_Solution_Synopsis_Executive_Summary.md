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
- **Catastrophic Quality Failures:** In August–September 2026, an outsourced result-processing vendor at **Barkatullah University (BU), Bhopal** produced an estimated **30% error rate**, marking attended students absent and truncating scores. At **Devi Ahilya Vishwavidyalaya (DAVV), Indore**, 3,800 out of 4,000 B.Ed students were mistakenly failed in a single cycle. At **Vikram University, Ujjain**, errors resulted in an MBA student awarded 1604 marks out of 1600.
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
        ├──► [ Question Forensics ]     (Real-time IRT Item Discrimination & Ambiguity Flags)
        └──► [ Legal Audit Engine ]     (1-Click Cryptographic RTI Defense Dossier)
```

---

### 3. Five Transformative Innovations

1. **Native Indic Multimodal Ingestion (Devanagari + Hinglish):**  
   An estimated 60%+ of MP state university students (BA, B.Com, B.Sc, B.Ed, LLB streams) write in Hindi. Traditional OCR pipelines fail because segmentation errors cascade into grading errors. PARIKSHAK-AI uses end-to-end multimodal vision to evaluate handwritten Hindi, English, and technical drawings directly against analytic rubrics without brittle OCR dependencies.

2. **Blind Seed-Script Calibration (Cambridge / IB Quality Standard):**  
   To eliminate inter-rater variance, Chief Examiners pre-score 5 "Anchor Scripts" across performance bands. These are invisibly interspersed into examiner queues. If an examiner’s score drifts beyond ±15% of the gold standard, the system temporarily halts evaluation and provides rubric recalibration before erroneous marks propagate.

3. **Cognitive Velocity & Dwell-Time Sentinel:**  
   Enforces a biological reading floor based on page word count (\(T_{min} = \frac{\text{Word Count}}{200} \times 60 + 5\text{s}\)). If an examiner attempts to submit marks for an essay in under 15 seconds, a velocity anomaly triggers, locking submission and routing the script for peer moderation.

4. **Live Question Paper Psychometric Forensics:**  
   Computes Item Response Theory (IRT) point-biserial correlations in real time across the student cohort. If Question 3(b) produces an 85% failure rate among top-quartile students, it is immediately flagged as ambiguous or out-of-syllabus, enabling the Controller of Examinations (CoE) to issue standard moderation before results publish.

5. **1-Click RTI Cryptographic Justification Dossier:**  
   In compliance with the June 2026 MP High Court ruling mandating transparent digital evaluation auditability, PARIKSHAK-AI generates an instant court-defensible PDF showing the student's answer, model key, point-by-point rubric deduction evidence, examiner timestamps, and SHA-256 tamper-evident hash.

---

### 4. Feasibility, Cloud Sovereignty & Economics
- **Non-Invasive Integration:** Seamlessly integrates with MPOnline's existing ASP.NET / Oracle examination portal via secure REST APIs and pre-signed storage URLs without altering core ERP modules.
- **Affordable Unit Economics:** At **₹1.14 per 36-page booklet**, the AI inference cost is a fraction of current revaluation processing overhead.
- **Strict Compliance:** Fully aligned with **NEP 2020 (Sections 4.34–4.37)**, **DPDP Act 2023** (local data residency), and **MeghRaj / MP State Data Centre** security mandates.
