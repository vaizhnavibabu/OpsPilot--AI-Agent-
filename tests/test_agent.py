import pytest
from src.agent.runtime import run_ops_pilot
from src.agent.state import CaseState
from src.retrieval.retriever import KnowledgeRetriever
from src.agent.config import settings


def test_retriever_initialization():
    """Test that the knowledge base retrieves correctly."""
    retriever = KnowledgeRetriever()
    assert len(retriever.documents) == 15
    
    # Search should return documents
    results = retriever.search("I forgot my password", top_k=1)
    assert len(results) > 0
    assert "password_policy.md" in [r["source"] for r in results]


def test_agent_low_risk_path():
    """Test that a standard access ticket routes to RECOMMEND."""
    # Temporarily set high risk threshold
    settings.escalation_threshold = 0.70
    
    state = run_ops_pilot(
        ticket_id="TEST-001",
        ticket_text="I forgot my password and need support resetting it.",
    )
    
    assert state.intent == "access"
    assert state.final_route == "RECOMMEND"
    assert state.hitl_required is False
    assert "password_policy.md" in [doc["source"] for doc in state.retrieved_documents]


def test_agent_high_risk_path():
    """Test that a refund request routes to HITL_REQUIRED."""
    state = run_ops_pilot(
        ticket_id="TEST-002",
        ticket_text="I want a refund for my subscription payment.",
    )
    
    assert state.intent == "refund"
    assert state.final_route == "HITL_REQUIRED"
    assert state.hitl_required is True
