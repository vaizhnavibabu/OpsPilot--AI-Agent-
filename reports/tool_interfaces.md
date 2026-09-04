# OpsPilot Tool Interface Summary

This document describes the typed interfaces, arguments, return schemas, and failure modes for all core tools in the **OpsPilot Agent Platform**.

---

## 1. Classify Escalation Risk Tool (`classify_escalation`)

* **Function Signature**: `classify_escalation(ticket_text: str) -> dict[str, Any]`
* **Purpose**: Evaluates whether the incoming ticket represents an escalation risk (angry customer, churn request, billing threat, or service outage).
* **Implementation**: Calls the TF-IDF + Logistic Regression pipeline loaded from `artifacts/escalation_model.joblib`.

### 1.1 Arguments
* `ticket_text` (str): The raw text of the incoming customer support ticket. Must not be empty.

### 1.2 Return Schema
```json
{
  "escalation": 0,
  "probability": 0.445
}
```
* `escalation` (int): Predicted class binary label. `1` represents high escalation risk; `0` represents normal risk.
* `probability` (float): Probability score of escalation risk (`[0.0, 1.0]`). Evaluated against the configured threshold to trigger human review.

### 1.3 Failure Modes & Mitigation
* **Failure Mode 1: Empty ticket text input.**
  * *Behavior*: The underlying TF-IDF vectorizer throws a ValueError during transform if the string is empty or whitespace-only.
  * *Mitigation*: Handled via preprocessing validation in `run_ops_pilot` to assert string presence.
* **Failure Mode 2: Missing model weight artifact.**
  * *Behavior*: `FileNotFoundError` when attempting to load `escalation_model.joblib`.
  * *Mitigation*: The evaluation runner and main app verify artifact presence. If missing, it instructs the user to run the training script.

---

## 2. Classify Intent Tool (`classify_intent`)

* **Function Signature**: `classify_intent(ticket_text: str) -> dict[str, Any]`
* **Purpose**: Identifies the primary customer intent among the 15 supported categories (e.g. `refund`, `access`, `outage`, `gdpr`).
* **Implementation**: Calls the TF-IDF + Logistic Regression pipeline loaded from `artifacts/intent_model.joblib`.

### 2.1 Arguments
* `ticket_text` (str): The raw text of the incoming ticket.

### 2.2 Return Schema
```json
{
  "intent": "refund",
  "confidence": 0.231
}
```
* `intent` (str): Labeled intent class string (one of the 15 categories).
* `confidence` (float): Classifier confidence score (`[0.0, 1.0]`) representing the probability of the winning class.

### 2.3 Failure Modes & Mitigation
* **Failure Mode 1: Out-of-Vocabulary (OOV) terms.**
  * *Behavior*: If the ticket contains only words unseen during training (e.g. "asdfghjkl"), the model outputs a uniform class probability distrib, yielding a low-confidence classification.
  * *Mitigation*: Handled in the planner by routing tickets with confidence scores below `0.25` or unrecognized intents to HITL.

---

## 3. Retrieve Policy Tool (`retrieve_policy`)

* **Function Signature**: `retrieve_policy(ticket_text: str) -> list[dict[str, Any]]`
* **Purpose**: Fetches relevant policy or runbook documents from the knowledge base directory.
* **Implementation**: Uses Sentence-Transformers (`all-MiniLM-L6-v2`) and NumPy cosine similarity to score matching documents.

### 3.1 Arguments
* `ticket_text` (str): Query string.

### 3.2 Return Schema
```json
[
  {
    "source": "password_policy.md",
    "text": "# Password Policy\n\n## Purpose\nThis policy explains...",
    "score": 0.477
  }
]
```
* Returns a list of dictionaries, sorted in descending order of similarity score. Max length is defined by `settings.retrieval_top_k` (default `3`).
* Only documents with `score >= settings.min_retrieval_score` (default `0.35`) are returned.

### 3.3 Failure Modes & Mitigation
* **Failure Mode 1: No knowledge documents in database.**
  * *Behavior*: Raises `RuntimeError` during retriever initialization.
  * *Mitigation*: Checked during system startup. The pipeline blocks execution if the knowledge folder is empty.
* **Failure Mode 2: Low-confidence / weak matches.**
  * *Behavior*: If similarity scores are low, the retriever returns an empty list `[]`.
  * *Mitigation*: Empty retrieval sets cause the Critic to fail (`FAIL` status), preventing automated draft generation and routing the ticket to human analysts.

---

## 4. Policy Critic Validation (`run_critic`)

* **Function Signature**: `run_critic(state: CaseState) -> CaseState`
* **Purpose**: Validates the drafted customer response against policy restrictions and grounding rules.
* **Implementation**: Heuristic policy rules checking for ungrounded citations and critical safety compliance.

### 4.1 Input State
* An instance of `CaseState` with `draft` and `retrieved_documents` populated.

### 4.2 Return State
* Updates the state attributes:
  * `critic_status`: `"PASS"` or `"FAIL"`.
  * `critic_reason`: Description of validation success or failure.

### 4.3 Failure Modes & Mitigation
* **Failure Mode 1: Missing draft.**
  * *Behavior*: Sets status to `"FAIL"` with reason `"No draft was produced."`.
  * *Mitigation*: State machine routes to HITL.
* **Failure Mode 2: Refund request bypasses human review.**
  * *Behavior*: If `state.intent == "refund"` and the draft does not contain `"human"`, the critic overrides state to `"FAIL"`.
  * *Mitigation*: Automatically triggers human review on refund drafts.
