import streamlit as st
import pandas as pd
import random
import ast
import os
from datetime import datetime
from collections import Counter
import itertools


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



# --- Hermes 🔱 Strategy Helpers ---
def calendar_aware_filter_pool(date, number_range):
    avoid = {date.day, date.month, date.weekday() + 1}
    return [n for n in number_range if n not in avoid]

def monthly_section_bias_weights(month):
    monthly_weights = {
        1: [0.12, 0.14, 0.24, 0.22, 0.28],
        2: [0.10, 0.15, 0.25, 0.25, 0.25],
        3: [0.08, 0.17, 0.27, 0.23, 0.25],
        4: [0.09, 0.16, 0.26, 0.24, 0.25],
        5: [0.11, 0.15, 0.25, 0.23, 0.26],
        6: [0.13, 0.16, 0.23, 0.23, 0.25],
        7: [0.14, 0.14, 0.24, 0.23, 0.25],
        8: [0.12, 0.15, 0.25, 0.23, 0.25],
        9: [0.11, 0.16, 0.24, 0.23, 0.26],
        10: [0.10, 0.16, 0.24, 0.23, 0.27],
        11: [0.09, 0.17, 0.24, 0.24, 0.26],
        12: [0.10, 0.15, 0.25, 0.25, 0.25],
    }
    return monthly_weights.get(month, [0.2, 0.2, 0.2, 0.2, 0.2])

def hermes_trident_strategy(draw_date):
    sections = {
        1: list(range(1, 11)),
        2: list(range(11, 21)),
        3: list(range(21, 31)),
        4: list(range(31, 41)),
        5: list(range(41, 51))
    }
    weights = monthly_section_bias_weights(draw_date.month)
    sections_pool = []
    for i, sec in sections.items():
        k = max(1, round(weights[i-1] * 5))
        sections_pool.extend(random.sample(sec, k=min(k, len(sec))))
    filtered_pool = calendar_aware_filter_pool(draw_date, sections_pool)
    if len(filtered_pool) < 5:
        filtered_pool = sections_pool
    main_pick = sorted(random.sample(filtered_pool, 5))
    euro_pool = calendar_aware_filter_pool(draw_date, list(range(1, 13)))
    if len(euro_pool) < 2:
        euro_pool = list(range(1, 13))
    euro_pick = sorted(random.sample(euro_pool, 2))
    return main_pick, euro_pick

# --- UI for Hermes 🔱 Strategy ---
st.markdown("---")
st.header("🔱 Hermes Strategy (Monthly Calendar Hybrid)")

if st.button("🎯 Generate Hermes 🔱 Pick"):
    today = datetime.today()
    h_main, h_euro = hermes_trident_strategy(today)
    st.success(f"Hermes 🔱 Pick: Main {h_main} + Euro {h_euro}")
    if st.button("✅ I Played This (Hermes 🔱)", key="hermes_save"):
        save_played_pick(h_main, h_euro, "Hermes 🔱")
        st.info("✅ Saved to your played picks.")


import streamlit as st
import pandas as pd
import random
import ast
import os
from datetime import datetime
from collections import Counter
import itertools
st.set_page_config(page_title="🎯 Eurojackpot Mastermind", layout="centered")

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


# --- All Strategy Picker Section ---
st.markdown("---")
st.header("🎯 Strategy Generator")

if "freq" in st.session_state:
    hot, warm, cold = get_heat_groups(st.session_state["freq"])
    strategy = st.radio("Select a strategy:", [
        "🔥 Hot Only", "🟡 Warm Only", "❄️ Cold Only",
        "⚖️ Balanced", "🎯 Small Win Strategy", "🛡️ Minimum Prize Guaranteed",
        "🔱 Hermes Strategy (Monthly Calendar Hybrid)"
    ])
    num_picks = st.slider("🔁 How many picks do you want?", 1, 10, 1)

    euro_pool = list(range(1, 13))
    for i in range(num_picks):
        today = datetime.today()

        if strategy == "🔥 Hot Only":
            main = sorted(random.sample(hot, 5))
            euro = sorted(random.sample(euro_pool, 2))
        elif strategy == "🟡 Warm Only":
            main = sorted(random.sample(warm, 5))
            euro = sorted(random.sample(euro_pool, 2))
        elif strategy == "❄️ Cold Only":
            main = sorted(random.sample(cold, 5))
            euro = sorted(random.sample(euro_pool, 2))
        elif strategy == "⚖️ Balanced":
            main = sorted(random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 1))
            euro = sorted(random.sample(euro_pool, 2))
        elif strategy == "🎯 Small Win Strategy":
            main = sorted(random.sample(hot + warm, 3) + random.sample(hot + warm + cold, 2))
            euro = sorted(random.sample(euro_pool, 2))
        elif strategy == "🛡️ Minimum Prize Guaranteed":
            main = sorted(random.sample(hot + warm, 5))
            euro = sorted(random.sample(euro_pool, 2))
        elif strategy == "🔱 Hermes Strategy (Monthly Calendar Hybrid)":
            main, euro = hermes_trident_strategy(today)

        st.success(f"{strategy} Pick {i+1}: {main} + {euro}")
        if st.button(f"✅ I Played This (Pick {i+1})", key=f"save_{i}_{strategy}"):
            save_played_pick(main, euro, strategy)
            st.info(f"Saved: {main} + {euro} under {strategy}")
