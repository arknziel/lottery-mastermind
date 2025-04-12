import streamlit as st
import pandas as pd
import random
import re
import itertools
from collections import Counter
from datetime import date
import os

st.set_page_config(page_title="🎯 Lottery Mastermind", layout="centered")

# --- File paths ---
EURO_FILE = "eurojackpot_master_data.csv"
SUPER_FREQ_FILE = "superenalotto_number_frequencies.csv"

# --- Lottery Switcher ---
lottery = st.radio("🎯 Select Lottery:", ["Eurojackpot", "SuperEnalotto"])

# --- Helper Functions ---
def clean_draw_date_column(df):
    df['Draw_Date'] = df['Draw_Date'].apply(lambda x: re.sub(r"^[A-Za-zäöüÄÖÜ]{2,3}\.\s*", "", x.strip()))
    return df

def load_eurojackpot_data():
    if os.path.exists(EURO_FILE):
        df = pd.read_csv(EURO_FILE)
        df['Main_Numbers'] = df['Main_Numbers'].apply(eval)
        df['Euro_Numbers'] = df['Euro_Numbers'].apply(eval)
        return df
    return pd.DataFrame(columns=['Draw_Date', 'Main_Numbers', 'Euro_Numbers'])

def analyze_frequency(df):
    all_main = list(itertools.chain.from_iterable(df['Main_Numbers']))
    all_euro = list(itertools.chain.from_iterable(df['Euro_Numbers']))
    main_freq = pd.DataFrame(Counter(all_main).items(), columns=['Number', 'Frequency']).sort_values(by='Frequency', ascending=False)
    euro_freq = pd.DataFrame(Counter(all_euro).items(), columns=['Number', 'Frequency']).sort_values(by='Frequency', ascending=False)
    return main_freq, euro_freq

def get_heat_groups(freq_df):
    total = len(freq_df)
    hot = freq_df.head(int(total * 0.15))['Number'].tolist()
    warm = freq_df.iloc[int(total * 0.15):int(total * 0.5)]['Number'].tolist()
    cold = freq_df.tail(int(total * 0.3))['Number'].tolist()
    return hot, warm, cold
