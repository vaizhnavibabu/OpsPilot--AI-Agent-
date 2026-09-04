from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from src.agent.config import settings
from src.agent.state import CaseState


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    temperature=0,
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an IT support ticket drafting assistant.

Your job is to draft a concise and safe support response
using ONLY the information provided in the ticket and
retrieved company policies.

Rules:
- Do not invent policies.
- Do not claim an incident is resolved unless the policy
  information supports that conclusion.
- Do not request passwords, API keys, or other sensitive
  authentication information.
- Refund requests must mention human review.
- Security issues must be handled cautiously.
- Production outages must not be falsely declared resolved.
- Never change, invent, or approximate factual details from
  the ticket.
- Monetary amounts must be reproduced exactly as provided.
- Do not invent actions that have already been taken.
- Do not say that a ticket was forwarded to a team unless the
  provided information explicitly says that it was forwarded.
- Keep the response professional and concise.
""",
        ),
        (
            "human",
            """Ticket:
{ticket}

Detected intent:
{intent}

Escalation probability:
{escalation_probability}

Retrieved policies:
{policies}

Draft a support response for this ticket.""",
        ),
    ]
)


def create_draft(state: CaseState) -> CaseState:

    policies = "\n\n".join(
        [
            (
                f"Source: {document['source']}\n"
                f"Content:\n{document['text']}"
            )
            for document in state.retrieved_documents
        ]
    )

    if not policies:
        policies = "No supporting policy was retrieved."

    chain = prompt | llm

    response = chain.invoke(
        {
            "ticket": state.ticket_text,
            "intent": state.intent,
            "escalation_probability": state.escalation_probability,
            "policies": policies,
        }
    )

    
    if isinstance(response.content, str):
        state.draft = response.content.strip()
    else:
        state.draft = "\n".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict) and block.get("text")
        ).strip()

    return state