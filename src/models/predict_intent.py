from pathlib import Path
import joblib

MODEL_PATH = Path("artifacts/intent_model.joblib")

def predict_intent(text: str):
    model = joblib.load(MODEL_PATH)
    intent = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0]
    confidence = float(max(probabilities))
    return intent, confidence

def main():
    ticket = "I forgot my password"
    intent, confidence = predict_intent(ticket)
    print("Ticket:", ticket)
    print("Intent:", intent)
    print("Confidence:", round(confidence, 3))

if __name__ == "__main__":
    main()