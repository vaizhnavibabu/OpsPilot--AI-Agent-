from typing import Literal

from pydantic import BaseModel, Field


class TicketTriageResult(BaseModel):
    intent: str = Field(
        description="The classified support ticket intent"
    )

    intent_confidence: float = Field(
        description="Confidence of the intent classifier"
    )

    escalation: int = Field(
        description="Escalation prediction: 0 or 1"
    )

    escalation_probability: float = Field(
        description="Probability that the ticket requires escalation"
    )

    policy_sources: list[str] = Field(
        description="Relevant policy documents"
    )

    draft: str = Field(
        description="Policy-grounded recommendation for the support team"
    )

    critic_status: Literal["PASS", "FAIL"] = Field(
        description="Whether the recommendation passed safety checks"
    )

    critic_reason: str = Field(
        description="Reason for the critic result"
    )

    hitl_required: bool = Field(
        description="Whether human review is required"
    )

    final_route: Literal["RECOMMEND", "HITL_REQUIRED"] = Field(
        description="Final ticket routing decision"
    )

