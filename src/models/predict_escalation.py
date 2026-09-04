from pathlib import Path
import joblib

MODEL_PATH = Path("artifacts/escalation_model.joblib")

def predict_with_probability(text: str):
    model = joblib.load(MODEL_PATH)
    prediction = int(model.predict([text])[0])
    probability = float(model.predict_proba([text])[0][1])
    return prediction, probability

def main():
    ticket = "Our production system is completely down"
    prediction, probability = predict_with_probability(ticket)
    print("Ticket:", ticket)
    print("Escalation:", prediction)
    print("Escalation probability:", round(probability, 3))

if __name__ == "__main__":
    main()