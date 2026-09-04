from langchain_core.tools import tool

from src.agent.tools import (
    classify_escalation,
    classify_intent,
    retrieve_policy,
)


@tool
def classify_ticket_intent(ticket_text: str) -> dict:
    """
    Classify the support ticket into an intent category.

    Use this tool whenever you need to determine what the
    customer is asking about.
    """
    return classify_intent(ticket_text)


@tool
def classify_ticket_escalation(ticket_text: str) -> dict:
    """
    Determine whether the support ticket has escalation risk.

    Returns the escalation prediction and probability.
    """
    return classify_escalation(ticket_text)


@tool
def search_support_policy(ticket_text: str) -> list[dict]:
    """
    Search OpsPilot's existing support knowledge base.

    Returns the most relevant support policies and their
    similarity scores.
    """
    return retrieve_policy(ticket_text)

