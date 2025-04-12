import streamlit as st
import pandas as pd
import random
import re
import itertools
from collections import Counter
import os

st.set_page_config(page_title="🎯 Lottery Mastermind", layout="centered")

# --- File paths ---
EURO_FILE = "eurojackpot_master_data.csv"
SUPER_FILE = "superenalotto_master_data.csv"

# --- Lottery Selector ---
lottery = st.radio("🎯 Select Lottery:", ["Eurojackpot", "SuperEnalotto"])

# --- Shared Helpers ---
def clean_draw_date_column(df):
    df['Draw_Date'] = df['Draw_Date'].apply(lambda x: re.sub(r"^[A-Za-zäöüÄÖÜ]{2,3}\.\s*", "", x.strip()))
    return df

def analyze_frequency(df):
    all_numbers = list(itertools.chain.from_iterable(df['Numbers']))
    freq = pd.DataFrame(Counter(all_numbers).items(), columns=['Number', 'Frequency']).sort_values(by='Frequency', ascending=False)
    return freq

def get_heat_groups(freq_df):
    total = len(freq_df)
    hot = freq_df.head(int(total * 0.15))['Number'].tolist()
    warm = freq_df.iloc[int(total * 0.15):int(total * 0.5)]['Number'].tolist()
    cold = freq_df.tail(int(total * 0.3))['Number'].tolist()
    return hot, warm, cold

def load_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Numbers'] = df['Numbers'].apply(eval)
        return df
    return None
