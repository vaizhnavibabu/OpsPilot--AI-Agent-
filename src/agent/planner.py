from src.agent.state import CaseState
from src.agent.tools import (
    classify_escalation,
    classify_intent,
    retrieve_policy,
)


def run_planner(
    state: CaseState,
    disable_retrieval: bool = False,
    use_keyword_search: bool = False,
) -> CaseState:

    escalation_result = classify_escalation(
        state.ticket_text
    )

    state.escalation = escalation_result["escalation"]
    state.escalation_probability = (
        escalation_result["probability"]
    )

    intent_result = classify_intent(
        state.ticket_text
    )

    state.intent = intent_result["intent"]
    state.intent_confidence = intent_result["confidence"]

    if disable_retrieval:
        state.retrieved_documents = []
    elif use_keyword_search:
        from src.agent.tools import retriever
        state.retrieved_documents = retriever.search_keyword(
            state.ticket_text
        )
    else:
        state.retrieved_documents = retrieve_policy(
            state.ticket_text
        )

    return state