from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/raw/tickets.csv")

def load_tickets() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)

def main():
    df = load_tickets()

    print("Number of tickets:", len(df))
    print()
    print(df.head())

if __name__ == "__main__":
    main()