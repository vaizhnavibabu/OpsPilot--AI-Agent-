from src.agent.state import CaseState


from src.agent.config import settings


def apply_hitl_policy(state: CaseState) -> CaseState:

    if (
        state.escalation_probability is not None
        and state.escalation_probability >= settings.escalation_threshold
    ):
        state.hitl_required = True
        state.final_route = "HITL_REQUIRED"
        return state

    if state.intent in {
        "refund",
        "security",
        "outage",
    }:
        state.hitl_required = True
        state.final_route = "HITL_REQUIRED"
        return state

    if state.critic_status != "PASS":
        state.hitl_required = True
        state.final_route = "HITL_REQUIRED"
        return state

    state.hitl_required = False
    state.final_route = "RECOMMEND"

    return state