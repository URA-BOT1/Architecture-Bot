import pandas as pd


def read_excel(path: str) -> str:
    df = pd.read_excel(path)
    return df.to_csv(index=False)
