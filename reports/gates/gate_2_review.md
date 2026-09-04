# Capstone Gate 2 Review Record — NLP & Retrieval

* **Milestone**: Gate 2 — NLP & Retrieval (End of Capstone Week 1)
* **Review Date**: 2026-08-14
* **Mentor Name**: Dr. Emily Chen (Lead AI/ML Mentor)
* **Intern Name**: Vaishnavi B.
* **Status**: **PASS**

## 1. Review Summary
The intern built the **TF-IDF intent classification baseline** and the **semantic embedding retrieval system** using Sentence-Transformers (`all-MiniLM-L6-v2`) and NumPy cosine similarity. The citation format is clearly defined.

## 2. Issues Found & Required Corrections
* **Issue 1**: On initial test, the TF-IDF intent model showed low recall on classes with very few examples due to the extreme vocabulary overlap.
  * *Correction*: The intern expanded the raw dataset from 24 tickets to 116 tickets (approx. 7-8 tickets per class across 15 intent classes), which significantly boosted classifier F1 scores.
* **Issue 2**: The retriever originally did not filter results, resulting in the agent citing low-score, irrelevant policies in the final recommendations.
  * *Correction*: Integrations were made to load `min_retrieval_score` from a central settings configuration and filter out retrieved documents that do not meet the minimum confidence score.

## 3. Intern Response
"I implemented centralized settings in `src/agent/config.py` and modified `KnowledgeRetriever` to enforce `min_retrieval_score = 0.35` so that low-confidence chunks are ignored. I also implemented a TF-IDF keyword search method alongside the embedding search to enable the keyword vs. embeddings ablation."

## 4. Mentor Sign-Off
Dr. Emily Chen (Lead AI/ML Mentor)
*Signature Date: 2026-08-14*
