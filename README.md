# OpsPilot

## Project Name

**OpsPilot — AI-Powered Support Ticket Triage and Response System**

## Description

OpsPilot is an AI-assisted IT support ticket triage system that analyzes incoming support tickets, identifies their intent, estimates escalation risk, retrieves relevant company policies, generates a support response using Gemini through LangChain, critiques the generated response, and determines whether human intervention is required.

The project combines traditional machine-learning components with an LLM-based workflow to make support-ticket handling more consistent, explainable, and safer.

## Overview

OpsPilot follows a structured pipeline:

1. A support ticket is received.
2. The planner analyzes the ticket.
3. A machine-learning model predicts the ticket intent.
4. A machine-learning model estimates escalation probability.
5. Relevant company policies are retrieved from the knowledge base.
6. LangChain sends the ticket context and policies to Gemini 2.5 Flash.
7. Gemini generates a draft support response.
8. A LangChain/Gemini critic reviews the draft for policy and safety problems.
9. A deterministic Human-in-the-Loop (HITL) policy decides whether human review is required.
10. OpsPilot produces a final route and execution trace.

This design separates prediction, retrieval, generation, evaluation, and routing instead of relying on a single LLM call.

## Features

- **Ticket intent classification**
  - Identifies the likely category or intent of a support ticket.
  - Produces an intent confidence score.

- **Escalation prediction**
  - Estimates the probability that a ticket requires escalation.
  - Supports threshold-based routing.

- **Policy retrieval**
  - Searches the internal knowledge base for relevant policies.
  - Supports semantic retrieval and keyword-based retrieval.

- **LLM-powered response drafting**
  - Uses LangChain with Google Gemini 2.5 Flash.
  - Generates concise and professional responses.
  - Grounds responses in the ticket and retrieved policies.

- **LLM-powered response critic**
  - Uses Gemini 2.5 Flash to review generated drafts.
  - Checks for unsafe, unsupported, or policy-inconsistent responses.
  - Includes deterministic validation for important factual details such as monetary amounts.

- **Human-in-the-Loop routing**
  - Routes high-risk tickets to human review.
  - Can trigger review based on escalation probability, sensitive intents, or critic failure.

- **Execution tracing**
  - Records major pipeline steps and routing decisions.
  - Makes the workflow easier to debug and demonstrate.

- **CLI interface**
  - Tickets can be submitted directly from PowerShell or another terminal.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application language |
| uv | Python environment and dependency management |
| LangChain | LLM orchestration and prompt pipelines |
| LangChain Google GenAI | Gemini integration |
| Google Gemini 2.5 Flash | Response generation and critique |
| Google AI Studio | Gemini API access and API key |
| scikit-learn / ML components | Intent and escalation prediction |
| Sentence Transformers / embeddings | Semantic policy retrieval |
| python-dotenv | Environment variable management |
| PowerShell / CLI | Local application execution |

## Project Structure

```text
OpsPilot/
│
├── src/
│   ├── agent/
│   │   ├── state.py
│   │   ├── tools.py
│   │   ├── planner.py
│   │   ├── drafter.py
│   │   ├── critic.py
│   │   ├── hitl.py
│   │   ├── runtime.py
│   │   ├── config.py
│   │   └── schemas.py
│   │
│   ├── models/
│   │   ├── predict_intent.py
│   │   ├── predict_escalation.py
│   │   └── ...
│   │
│   ├── retrieval/
│   │   ├── retriever.py
│   │   └── ...
│   │
│   └── app/
│       └── main.py
│
├── data/
├── artifacts/
├── notebooks/
├── reports/
├── traces/
├── tests/
│
├── .env
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── uv.lock
└── README.md
```

### Important modules

- `state.py` — Defines the shared `CaseState` object used throughout the workflow.
- `tools.py` — Exposes classification and policy-retrieval functions to the agent pipeline.
- `planner.py` — Runs intent classification, escalation prediction, and policy retrieval.
- `drafter.py` — Creates the support response using LangChain and Gemini.
- `critic.py` — Reviews the generated response.
- `hitl.py` — Applies human-review routing rules.
- `runtime.py` — Connects the complete OpsPilot workflow.
- `main.py` — Provides the command-line interface.

## Prerequisites

Before running OpsPilot, install:

- Python 3.10 or compatible version
- `uv`
- A Google AI Studio API key
- Internet access for Gemini API requests
- Access to the project's knowledge-base and model artifacts

Verify Python:

```powershell
python --version
```

Verify uv:

```powershell
uv --version
```

## Installation

### 1. Clone or open the project

```powershell
cd C:\Users\dhana\Desktop\OpsPilot
```

### 2. Create/synchronize the uv environment

If the project already contains `pyproject.toml` and `uv.lock`:

```powershell
uv sync
```

### 3. Activate the environment if desired

```powershell
.\.venv\Scripts\Activate.ps1
```

Activation is optional when using `uv run`.

### 4. Verify dependencies

```powershell
uv run python -c "import langchain; import langchain_google_genai; print('Dependencies OK')"
```

## Configuration

Create a `.env` file in the project root:

```text
GOOGLE_API_KEY=your_google_ai_studio_api_key
```

The application loads the environment variables using `python-dotenv`.

### Gemini configuration

The LangChain Gemini configuration should use:

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)
```

The same model can be used for both the drafting and critic stages.

### Security

Never commit `.env` to Git.

Your `.gitignore` should contain at least:

```text
.env
.venv/
__pycache__/
*.pyc
```

Never place the API key directly in Python source code, README files, screenshots, or reports.

## Usage

OpsPilot can be executed from the command line.

### Basic ticket

```powershell
uv run python -m src.app.main --ticket 'I was charged $49.99 for a service I did not intend to purchase. Please help me understand this charge.' --ticket-id TEST-010
```

Using single quotes in PowerShell is recommended when the ticket contains `$`, because double-quoted PowerShell strings can interpret `$` as variable expansion.

### Example: refund request

```powershell
uv run python -m src.app.main --ticket 'I was charged twice for my subscription and I want a refund for the duplicate payment.' --ticket-id TEST-002
```

### Example: production outage

```powershell
uv run python -m src.app.main --ticket 'Our production API is completely down and customers cannot access the service. This started about 20 minutes ago.' --ticket-id TEST-003
```

### Example output

```text
============================================================
OPSPILOT RESULT
============================================================
Ticket: ...
Intent: payment_failure
Intent confidence: 0.XXX
Escalation probability: 0.XXX

Retrieved policies:
- service_credit_policy.md (score=0.XXX)

Draft:
...

Critic: PASS
Critic reason: ...

HITL required: False
Final route: RECOMMEND

Trace:
- ticket_received
- planning_and_tools
- langchain_draft
- critic
- routing
```

## Testing

OpsPilot should be tested using tickets that cover different routing scenarios.

Recommended test categories:

| Test | Scenario | Expected behavior |
|---|---|---|
| TEST-002 | Duplicate payment/refund | Draft should mention appropriate review |
| TEST-003 | Production outage | High-risk handling and possible HITL |
| TEST-010 | Unrecognized charge | Accurate monetary amount and safe response |
| TEST-014 | Suspicious account activity | Security-aware handling |
| TEST-015 | Credential exposure | Cautious/security handling |
| TEST-019 | Ambiguous ticket | Avoid unsupported assumptions |
| TEST-020 | Combined outage/security issue | High-risk routing |

Run a test with:

```powershell
uv run python -m src.app.main --ticket 'YOUR TICKET TEXT' --ticket-id TEST-XXX
```

### What to validate

For each test, verify:

- Intent is reasonable.
- Intent confidence is recorded.
- Escalation probability is recorded.
- Relevant policies are retrieved.
- Draft does not invent policies or actions.
- Monetary amounts remain exactly as provided.
- Security-sensitive tickets are handled cautiously.
- Critic returns an appropriate result.
- HITL is triggered for high-risk cases.
- Final routing is consistent with the policy.
- Trace contains the expected workflow stages.

## Deployment

OpsPilot can be deployed as a Python application after local validation.

A basic deployment process is:

1. Provision a Python-compatible runtime.
2. Install `uv` or use another supported Python dependency workflow.
3. Copy the project source and required model/knowledge artifacts.
4. Configure `GOOGLE_API_KEY` as a secure environment variable.
5. Install dependencies with:

```powershell
uv sync
```

6. Run the application:

```powershell
uv run python -m src.app.main --ticket 'Example support ticket' --ticket-id PROD-001
```

For production deployment, API keys should be stored in the platform's secret-management system rather than in a committed `.env` file.

A future production version could expose OpsPilot through a REST API or web interface instead of only the CLI.

## Troubleshooting

### 1. Gemini model not found

Error:

```text
GoogleModelNotFoundError
404 NOT_FOUND
```

Verify that the configured model is:

```text
gemini-2.5-flash
```

Also verify that the Google AI Studio API key/project has access to the model.

### 2. Missing Google API key

If Gemini reports missing credentials, verify `.env`:

```text
GOOGLE_API_KEY=your_key_here
```

Restart the terminal if environment variables were configured outside the current process.

### 3. `$49.99` becomes `.99` in PowerShell

Use single quotes:

```powershell
--ticket 'I was charged $49.99 for a service.'
```

Avoid:

```powershell
--ticket "I was charged $49.99 for a service."
```

because PowerShell can interpret `$49` as variable expansion.

### 4. Hugging Face authentication warning

A message such as:

```text
You are sending unauthenticated requests to the HF Hub.
```

usually indicates that the Hugging Face Hub request is unauthenticated. If the embedding model loads successfully, this warning does not necessarily mean that OpsPilot has failed.

For higher download limits and improved reliability, configure a Hugging Face token when appropriate.

### 5. Gemini AFC warning

A message mentioning:

```text
Direct use of automatic function calling (AFC) ...
```

is a library/API warning. If the Gemini call completes successfully, it is not necessarily the cause of an application failure. If it becomes an error after dependency upgrades, check the installed `langchain-google-genai` and Google GenAI package versions.

### 6. Gemini response content is not a string

Some Gemini/LangChain responses can expose structured content. If the application expects a string, normalize the response content before storing it in `state.draft`.

### 7. Retrieval returns no documents

Check:

- Knowledge-base files exist.
- Embedding model loads successfully.
- Retrieval paths are correct.
- Ticket text is meaningful enough for semantic search.

## Future Improvements

Potential future improvements include:

1. **LangSmith integration**
   - Add tracing for LangChain runs.
   - Monitor latency and token usage.
   - Evaluate draft and critic quality across test datasets.

2. **Better evaluation**
   - Add automated accuracy metrics for intent classification.
   - Measure escalation prediction performance.
   - Evaluate retrieval relevance.
   - Measure response safety and factual consistency.

3. **Improved HITL workflow**
   - Add an actual human-review queue.
   - Allow reviewers to approve, edit, or reject drafts.
   - Record human feedback for future evaluation.

4. **Structured LLM outputs**
   - Use structured schemas for critic results and draft metadata.
   - Reduce parsing errors.

5. **Production API**
   - Expose OpsPilot through FastAPI.
   - Add authentication and request validation.
   - Support integration with ticketing systems.

6. **Observability**
   - Add LangSmith tracing.
   - Add application metrics and error monitoring.
   - Track model latency and retrieval performance.

7. **Knowledge-base improvements**
   - Add more policies.
   - Improve document chunking and metadata.
   - Add document versioning.

8. **Model improvements**
   - Compare Gemini model versions.
   - Improve intent and escalation classifiers.
   - Add confidence calibration.

9. **Security**
   - Add secret management.
   - Redact sensitive information from logs.
   - Add stronger prompt-injection defenses.

## Contributing

Contributions are welcome.

Recommended workflow:

1. Create a feature branch.
2. Make the change.
3. Add or update tests.
4. Run the relevant test cases.
5. Verify that no secrets are committed.
6. Update documentation when behavior changes.
7. Submit a pull request.

Before committing:

```powershell
git status
```

Check that `.env`, API keys, and other secrets are not included.

## License

This project can be distributed under the license selected by the project owner.

If no license has been selected yet, do not claim a specific open-source license. Add an appropriate `LICENSE` file and update this section once the licensing decision has been made.

---

## Project Explanation — Quick Presentation Version

If you need to explain OpsPilot in an interview, viva, or project presentation:

> **OpsPilot is an AI-assisted support-ticket triage system that combines traditional machine learning, semantic policy retrieval, and LangChain-based Gemini reasoning. It first predicts ticket intent and escalation probability, retrieves relevant company policies, then uses Gemini 2.5 Flash to draft and critique a response. Finally, a deterministic HITL policy decides whether the ticket can be recommended for normal handling or requires human review.**

### One-line architecture

```text
Ticket → ML Planner → Policy Retrieval → Gemini Draft → Gemini Critic → HITL → Final Route
```

### Why this architecture?

The key design decision is that the LLM is **not responsible for everything**.

- ML handles classification and risk estimation.
- Retrieval provides company-specific knowledge.
- Gemini handles natural-language generation and critique.
- Deterministic rules control the final safety/routing decision.

This makes the system easier to evaluate, debug, and control than a single unrestricted LLM call.

