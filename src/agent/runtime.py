from src.agent.critic import run_critic
from src.agent.hitl import apply_hitl_policy
from src.agent.drafter import create_draft
from src.agent.planner import run_planner
from src.agent.state import CaseState


def run_ops_pilot(
    ticket_id: str,
    ticket_text: str,
    disable_critic: bool = False,
    disable_retrieval: bool = False,
    use_keyword_search: bool = False,
) -> CaseState:

    state = CaseState(
        ticket_id=ticket_id,
        ticket_text=ticket_text,
    )

    state.trace.append(
        {
            "step": "ticket_received",
            "status": "completed",
        }
    )

    # Existing deterministic ML + retrieval pipeline
    state = run_planner(
        state,
        disable_retrieval=disable_retrieval,
        use_keyword_search=use_keyword_search,
    )

    state.trace.append(
        {
            "step": "planning_and_tools",
            "intent": state.intent,
            "escalation": state.escalation,
        }
    )

    # LangChain + Gemini drafting layer
    state = create_draft(state)

    state.trace.append(
        {
            "step": "langchain_draft",
            "status": "completed",
        }
    )

    # Existing deterministic critic
    if disable_critic:
        state.critic_status = "PASS"
        state.critic_reason = (
            "Critic disabled for evaluation ablation."
        )
    else:
        state = run_critic(state)

    state.trace.append(
        {
            "step": "critic",
            "status": state.critic_status,
        }
    )

    # Existing deterministic HITL policy
    state = apply_hitl_policy(state)

    state.trace.append(
        {
            "step": "routing",
            "route": state.final_route,
        }
    )

    return state