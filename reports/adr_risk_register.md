# Architectural Decision Record (ADR), Risk Register & Data Contract

This document outlines the design decisions, risk mitigations, and data constraints for the **OpsPilot Agent Platform** version 1.0.

---

## 1. Architectural Decision Record (ADR)
### Title: Retrieval-Augmented Generation (RAG) + Multi-Agent Orchestration vs. LLM Fine-Tuning for Policy Compliance

* **Date**: 2026-08-14
* **Status**: **APPROVED**
* **Deciders**: Vaishnavi B. (Intern), Dr. Emily Chen (Mentor)

### 1.1 Context
We need a support ticket triage and recommendation system that drafts customer responses according to dynamic company policies (e.g. refund rules, outage runbooks, access recovery). The system must be explainable, safe, and easily updated as corporate policies evolve.

### 1.2 Alternatives Considered
1. **Option 1: Fine-Tuning an LLM**: Fine-tune a pre-trained LLM directly on historical tickets and policy documents.
2. **Option 2: Tools + RAG with State Machine Orchestration**: Keep policies in a vector search index (RAG), use classification models for planning (signals), draft using retrieved documents, and validate via a policy critic.

### 1.3 Decision & Rationale
We chose **Option 2 (Tools + RAG with State Machine Orchestration)** for the following reasons:
* **Explainability (Citations)**: RAG provides explicit citations (e.g., citing `password_policy.md` and the specific allowed/restricted sections). This is critical for support leads auditing the copilot. Fine-tuned models cannot cite sources reliably.
* **Instant Policy Updates**: When a refund policy changes, we can simply edit the text in `refund_policy.md` and the system is updated instantly. Fine-tuning requires re-training, which is expensive and slow.
* **Hard Guardrails (Safety Critic)**: With RAG, we can feed the retrieved text and the draft into a separate deterministic/critic step to verify grounding. A fine-tuned model merges knowledge and generation, making it difficult to prevent hallucinated policies.
* **Cost and Complexity**: Re-training models requires GPUs and extensive ML pipelines. RAG runs efficiently on CPU using scikit-learn and Sentence-Transformers, aligning perfectly with the resource constraints of this project.

### 1.4 Consequences
* We must maintain an index of policy documents and update embeddings whenever a document changes.
* We must handle cases of "weak retrieval" where no relevant documents are found by refusing to answer or routing to human agents.

---

## 2. Risk Register
We have identified the following operational and technical risks:

| Risk ID | Risk Description | Severity | Probability | Mitigation Strategy | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R-001** | **Autonomous Damage**: Agent issues refunds or deletes accounts autonomously. | Critical | Low | **Hard Guardrail**: No autonomous write actions are implemented. Any high-risk intent (`refund`, `security`, `outage`) defaults to `HITL_REQUIRED` routing. | Active |
| **R-002** | **Hallucination**: Agent drafts responses inventing non-existent support policies. | High | Medium | **Policy Critic**: A critic runs after the drafter. If `state.retrieved_documents` is empty, or the draft fails checks, the critic fails and routes the ticket to a human. | Active |
| **R-003** | **Data Leakage**: Train/test split contains post-resolution leakage fields. | High | Low | **Data Contract Enforced**: Only raw, ingestion-time text and pre-labeled columns (`text`, `intent`, `escalation`) are allowed in `tickets.csv`. Post-resolution fields are banned. | Verified |
| **R-004** | **Class Imbalance**: Imbalanced training set causing high false-negative rate on escalation risk. | Medium | High | **Metric Evaluation**: Evaluate the escalation classifier using F1-score and Recall instead of accuracy. Lower the classification threshold to `0.30` to guarantee high safety. | Active |

---

## 3. Data Contract Note

### 3.1 Dataset Columns (`data/raw/tickets.csv`)
* `ticket_id`: Unique identifier (string).
* `text`: Raw text of the incoming customer support ticket (string).
* `intent`: Labeled intent category (string, 15 distinct classes).
* `escalation`: Labeled escalation risk flag (integer: `1` for high-risk, `0` for normal).

### 3.2 Forbidden Data Leakage Fields
To prevent data leakage, the following fields are strictly prohibited from training and serving datasets:
* `resolution_time` (recorded post-resolution)
* `customer_feedback_rating` (recorded post-resolution)
* `escalated_by_agent` (post-resolution action)
* `ticket_status` (changes during lifecycle)
* `assigned_agent_id` (determined post-triage)

### 3.3 Train vs. Serve Parity
The raw text in `tickets.csv` represents customer messages in their raw form at the moment of ingestion. No preprocessing (like manual cleaning or summarization) is performed prior to model scoring to ensure training data perfectly matches the text structure received in production.
