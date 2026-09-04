from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/raw/tickets.csv")

def main():
    df = pd.read_csv(DATA_PATH)

    print("=" * 60)
    print("DATASET SHAPE")
    print("=" * 60)
    print(df.shape)

    print("\n" + "=" * 60)
    print("COLUMNS")
    print("=" * 60)
    print(df.columns.tolist())

    print("\n" + "=" * 60)
    print("MISSING VALUES")
    print("=" * 60)
    print(df.isnull().sum())

    print("\n" + "=" * 60)
    print("INTENT DISTRIBUTION")
    print("=" * 60)
    print(df["intent"].value_counts())

    print("\n" + "=" * 60)
    print("ESCALATION DISTRIBUTION")
    print("=" * 60)
    print(df["escalation"].value_counts())

    print("\n" + "=" * 60)
    print("DUPLICATE ROWS")
    print("=" * 60)
    print(df.duplicated().sum())

if __name__ == "__main__":
    main()