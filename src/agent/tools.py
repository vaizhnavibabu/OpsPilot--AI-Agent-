from src.models.predict_escalation import (
    predict_with_probability,
)
from src.models.predict_intent import predict_intent
from src.retrieval.retriever import KnowledgeRetriever


retriever = KnowledgeRetriever()


def classify_escalation(ticket_text: str):
    prediction, probability = predict_with_probability(
        ticket_text
    )

    return {
        "escalation": prediction,
        "probability": probability,
    }


def classify_intent(ticket_text: str):
    intent, confidence = predict_intent(ticket_text)

    return {
        "intent": intent,
        "confidence": confidence,
    }


def retrieve_policy(ticket_text: str):
    return retriever.search(ticket_text)