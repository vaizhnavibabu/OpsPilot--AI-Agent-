# Capstone Gate 1 Review Record — Data & ML

* **Milestone**: Gate 1 — Data & ML (End of Capstone Week 1, early)
* **Review Date**: 2026-08-14
* **Mentor Name**: Dr. Emily Chen (Lead AI/ML Mentor)
* **Intern Name**: Vaishnavi B.
* **Status**: **PASS**

## 1. Review Summary
The intern completed the Exploratory Data Analysis (EDA) and built the initial **escalation risk classification model**. The EDA properly examined dataset balance, missing values, duplicates, and checked for any data leakage.

## 2. Issues Found & Required Corrections
* **Issue 1**: Imbalance in the synthetic escalation labels (majority are non-escalated, Class 0). Naive accuracy reports could be highly misleading.
  * *Correction*: The intern implemented stratified splits (`stratify=y`) and added precision/recall/F1 reporting rather than pure accuracy.
* **Issue 2**: Risk of data leakage in customer support records (e.g. using post-resolution fields such as "time_closed" or "satisfaction_rating" in training).
  * *Correction*: Checked and verified that `tickets.csv` features only contain raw ticket text ingested *before* routing. No post-resolution features are present.

## 3. Intern Response
"I have updated the training script `src/models/escalation.py` to use a stratified split and output a complete scikit-learn classification report. I also verified the data pipeline to confirm no leakage fields are used."

## 4. Mentor Sign-Off
Dr. Emily Chen (Lead AI/ML Mentor)
*Signature Date: 2026-08-14*
