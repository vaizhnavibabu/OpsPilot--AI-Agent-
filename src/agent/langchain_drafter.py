from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.agent.state import CaseState


load_dotenv()


def create_langchain_draft(state: CaseState) -> str:

    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are the drafting component of OpsPilot.

Create a concise support-team recommendation.

Rules:

- Only use the supplied ticket information and policies.
- Do not invent policies.
- Do not promise refunds.
- Refund requests require human review.
- Security issues require human review.
- Outage reports must not be described as resolved
  unless the supplied information confirms resolution.
- Never request passwords, authentication codes,
  API keys, or other sensitive credentials.

Return only the recommendation.
""",
            ),
            (
                "human",
                """
Ticket:
{ticket}

Intent:
{intent}

Intent confidence:
{intent_confidence}

Escalation probability:
{escalation_probability}

Relevant policies:
{policies}
""",
            ),
        ]
    )

    policy_text = "\n\n".join(
        f"Source: {doc['source']}\n{doc['text']}"
        for doc in state.retrieved_documents
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "ticket": state.ticket_text,
            "intent": state.intent,
            "intent_confidence": state.intent_confidence,
            "escalation_probability": state.escalation_probability,
            "policies": policy_text,
        }
    )

    return response.content
