import re

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agent.config import settings
from src.agent.state import CaseState


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    temperature=0,
)


critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a strict quality and safety critic for an
IT support ticketing system.

Evaluate the proposed support draft against the original ticket
and the retrieved company policies.

Return exactly one of:

PASS
FAIL: <short reason>

Rules:
- The draft must not invent facts.
- Monetary amounts must match the ticket exactly.
- Do not invent actions that have already happened.
- Do not claim an incident is resolved without evidence.
- Do not request passwords, API keys, or sensitive credentials.
- Refund requests must mention human review.
- Security issues must be handled cautiously.
- Production outages must not be falsely declared resolved.
- The draft should be consistent with the retrieved policies.
""",
        ),
        (
            "human",
            """Original ticket:
{ticket}

Detected intent:
{intent}

Escalation probability:
{escalation_probability}

Retrieved policies:
{policies}

Proposed draft:
{draft}

Critique the proposed draft.""",
        ),
    ]
)


def _extract_content(response) -> str:
    """Normalize Gemini/LangChain response content to plain text."""

    if isinstance(response.content, str):
        return response.content.strip()

    if isinstance(response.content, list):
        parts = []

        for block in response.content:
            if isinstance(block, dict):
                text = block.get("text")

                if text:
                    parts.append(text)

        return "\n".join(parts).strip()

    return str(response.content).strip()


def _extract_money_values(text: str) -> set[str]:
    return set(
        re.findall(
            r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?",
            text,
        )
    )


def run_critic(state: CaseState) -> CaseState:

    if not state.draft:
        state.critic_status = "FAIL"
        state.critic_reason = "No draft was produced."
        return state

    if not state.retrieved_documents:
        state.critic_status = "FAIL"
        state.critic_reason = "No supporting policy was retrieved."
        return state

    policies = "\n\n".join(
        [
            (
                f"Source: {document['source']}\n"
                f"Content:\n{document['text']}"
            )
            for document in state.retrieved_documents
        ]
    )

    chain = critic_prompt | llm

    response = chain.invoke(
        {
            "ticket": state.ticket_text,
            "intent": state.intent,
            "escalation_probability": state.escalation_probability,
            "policies": policies,
            "draft": state.draft,
        }
    )

    result = _extract_content(response)

    if result.upper().startswith("PASS"):
        state.critic_status = "PASS"
        state.critic_reason = result
    else:
        state.critic_status = "FAIL"

        if result.upper().startswith("FAIL:"):
            state.critic_reason = result[5:].strip()
        else:
            state.critic_reason = result

    # Deterministic factual check for monetary values.
    ticket_amounts = _extract_money_values(state.ticket_text)
    draft_amounts = _extract_money_values(state.draft)

    missing_amounts = ticket_amounts - draft_amounts

    if missing_amounts:
        state.critic_status = "FAIL"
        state.critic_reason = (
            "Draft changed or omitted monetary value(s): "
            + ", ".join(sorted(missing_amounts))
        )

    return state