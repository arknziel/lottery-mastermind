
import streamlit as st
import pandas as pd
import random
import ast
import os
from datetime import datetime
from collections import Counter
import itertools

st.set_page_config(page_title="🎯 Eurojackpot Mastermind", layout="centered")

EURO_FILE = "eurojackpot_master_data.csv"
PLAYED_FILE = "played_picks.csv"

def load_data():
    if os.path.exists(EURO_FILE):
        df = pd.read_csv(EURO_FILE)
        if "Numbers" in df.columns:
            df["Numbers"] = df["Numbers"].apply(ast.literal_eval)
            df["Main_Numbers"] = df["Numbers"].apply(lambda x: x[:5])
            df["Euro_Numbers"] = df["Numbers"].apply(lambda x: x[5:])
        elif "Main_Numbers" in df.columns and "Euro_Numbers" in df.columns:
            df["Main_Numbers"] = df["Main_Numbers"].apply(ast.literal_eval)
            df["Euro_Numbers"] = df["Euro_Numbers"].apply(ast.literal_eval)
            df["Numbers"] = df["Main_Numbers"] + df["Euro_Numbers"]
        else:
            st.error("❌ CSV must contain 'Numbers' or both 'Main_Numbers' and 'Euro_Numbers'")
            return None
        return df
    return None

def analyze_frequency(df):
    all_main = list(itertools.chain.from_iterable(df['Main_Numbers']))
    all_euro = list(itertools.chain.from_iterable(df['Euro_Numbers']))
    main_freq = pd.Series(Counter(all_main)).sort_values(ascending=False)
    euro_freq = pd.Series(Counter(all_euro)).sort_values(ascending=False)
    return main_freq, euro_freq

def get_heat_groups(freq_series):
    total = len(freq_series)
    hot = freq_series.head(int(total * 0.15)).index.tolist()
    warm = freq_series.iloc[int(total * 0.15):int(total * 0.5)].index.tolist()
    cold = freq_series.tail(int(total * 0.3)).index.tolist()
    return hot, warm, cold

def save_played_pick(main, euro, strategy):
    pick_str = f"{sorted(main)} + {sorted(euro)}"
    today_str = datetime.today().strftime("%Y-%m-%d")
    new_row = pd.DataFrame([{
        "Date": today_str,
        "Main": str(sorted(main)),
        "Euro": str(sorted(euro)),
        "Strategy": strategy,
        "Pick": pick_str
    }])
    if os.path.exists(PLAYED_FILE):
        old = pd.read_csv(PLAYED_FILE)
        updated = pd.concat([old, new_row], ignore_index=True)
    else:
        updated = new_row
    updated.to_csv(PLAYED_FILE, index=False)

def generate_hermes_pick(monthly_weights):
    today = datetime.today()
    month = today.month
    avoid_nums = {today.day, today.month, today.weekday()}
    avoid_nums = {n for n in avoid_nums if 1 <= n <= 50}
    section_weights = monthly_weights.get(month, [1]*5)

    sections = [list(range(i*10+1, i*10+11)) for i in range(5)]
    selected_main = []
    available_sections = [i for i, w in enumerate(section_weights) for _ in range(w)]

    while len(selected_main) < 5:
        section = random.choice(available_sections)
        candidate = random.choice(sections[section])
        if candidate not in selected_main and candidate not in avoid_nums:
            selected_main.append(candidate)

    euro_pool = [i for i in range(1, 13) if i not in avoid_nums]
    euro = sorted(random.sample(euro_pool if len(euro_pool) >= 2 else list(range(1, 13)), 2))
    return sorted(selected_main), euro

# --- UI Starts ---
st.title("🎯 Eurojackpot Mastermind")

df = load_data()

if df is not None:
    main_freq, euro_freq = analyze_frequency(df)
    hot, warm, cold = get_heat_groups(main_freq)

    st.subheader("🔱 Hermes Strategy")
    st.markdown("**Hermes Strategy** combines:")
    st.markdown("- Calendar-aware filtering (day/month/weekday)")
    st.markdown("- Year-aware filtering")
    st.markdown("- Monthly section weighting")

    monthly_weights = {
        1: [2, 1, 1, 1, 1],
        2: [1, 1, 2, 1, 1],
        3: [1, 2, 1, 1, 1],
        4: [1, 1, 1, 2, 1],
        5: [1, 1, 1, 1, 2],
        6: [2, 1, 1, 1, 1],
        7: [1, 2, 1, 1, 1],
        8: [1, 1, 2, 1, 1],
        9: [1, 1, 1, 2, 1],
        10: [1, 1, 1, 1, 2],
        11: [2, 1, 1, 1, 1],
        12: [1, 2, 1, 1, 1],
    }

    how_many = st.slider("How many Hermes 🔱 picks?", 1, 10, 1)
    for i in range(how_many):
        main, euro = generate_hermes_pick(monthly_weights)
        st.success(f"🔱 Hermes Pick {i+1}: {main} + {euro}")
        if st.button(f"✅ I Played This (Hermes {i+1})", key=f"save_hermes_{i}"):
            save_played_pick(main, euro, "🔱 Hermes")
            st.info("Saved to your picks.")
else:
    st.warning("Please upload or load Eurojackpot data.")
