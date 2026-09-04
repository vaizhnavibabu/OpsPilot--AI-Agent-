from dataclasses import dataclass, field
from typing import Any


@dataclass
class CaseState:
    ticket_id: str
    ticket_text: str

    intent: str | None = None
    intent_confidence: float | None = None

    escalation: int | None = None
    escalation_probability: float | None = None

    retrieved_documents: list[dict[str, Any]] = field(
        default_factory=list
    )

    draft: str | None = None

    critic_status: str | None = None
    critic_reason: str | None = None

    hitl_required: bool = False

    final_route: str | None = None

    trace: list[dict[str, Any]] = field(
        default_factory=list
    )