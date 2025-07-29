# utils/load_data.py
import pandas as pd

def load_backlog(file):
    return pd.read_csv(file)

def format_backlog_as_text(df):
    return "\n".join(df.astype(str).agg(", ".join, axis=1))