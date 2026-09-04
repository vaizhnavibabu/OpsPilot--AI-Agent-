import os
from pydantic import BaseModel

class AgentSettings(BaseModel):
    escalation_threshold: float = 0.70
    retrieval_top_k: int = 3
    min_retrieval_score: float = 0.35
    max_agent_steps: int = 5
    gemini_model: str = "gemini-3.5-flash-lite"

    @classmethod
    def load(cls):
        return cls(
            escalation_threshold=float(os.environ.get("OPSPILOT_ESCALATION_THRESHOLD", 0.70)),
            retrieval_top_k=int(os.environ.get("OPSPILOT_RETRIEVAL_TOP_K", 3)),
            min_retrieval_score=float(os.environ.get("OPSPILOT_MIN_RETRIEVAL_SCORE", 0.35)),
            max_agent_steps=int(os.environ.get("OPSPILOT_MAX_AGENT_STEPS", 5)),
            gemini_model=os.environ.get("OPSPILOT_GEMINI_MODEL", "gemini-3.5-flash-lite"),
        )

settings = AgentSettings.load()
