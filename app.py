import streamlit as st
import pandas as pd
import random
import itertools
from collections import Counter
from datetime import datetime
import os
import ast

st.set_page_config(page_title="🎯 Eurojackpot Mastermind", layout="centered")

EURO_FILE = "eurojackpot_master_data.csv"
PLAYED_FILE = "played_picks.csv"

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

def safe_parse(x):
    try:
        return ast.literal_eval(x)
    except Exception:
        return []

def load_data():
    if os.path.exists(EURO_FILE):
        df = pd.read_csv(EURO_FILE)
        if "Numbers" not in df.columns and "Main_Numbers" in df.columns and "Euro_Numbers" in df.columns:
            df["Main_Numbers"] = df["Main_Numbers"].apply(ast.literal_eval)
            df["Euro_Numbers"] = df["Euro_Numbers"].apply(ast.literal_eval)
            df["Numbers"] = df["Main_Numbers"] + df["Euro_Numbers"]
        else:
            df["Numbers"] = df["Numbers"].astype(str).apply(safe_parse)
        return df
    return None

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

df = load_data()

# The rest of the app will be appended below


st.title("🎯 Eurojackpot Mastermind")

st.subheader("📤 Upload Eurojackpot CSV")
ej_file = st.file_uploader("Choose Eurojackpot CSV", type="csv", key="ej_upload")
if ej_file:
    uploaded_df = pd.read_csv(ej_file)
    uploaded_df.to_csv(EURO_FILE, index=False)
    st.success("✅ File uploaded and saved!")
    df = load_data()

if df is not None:
    if st.button("📊 Run Frequency Analysis"):
        freq = analyze_frequency(df)
        st.session_state["freq"] = freq

    if "freq" in st.session_state:
        hot, warm, cold = get_heat_groups(st.session_state["freq"])

        st.subheader("🔥 Heat Analyzer")
        st.write(f"🔥 Hot: {hot}")
        st.write(f"🟡 Warm: {warm}")
        st.write(f"❄️ Cold: {cold}")

        st.subheader("🎯 Strategy Generator")
        strategy = st.radio("Select a strategy:", [
            "🔥 Hot Only", "🟡 Warm Only", "❄️ Cold Only",
            "⚖️ Balanced", "🎯 Small Win Strategy", "🛡️ Minimum Prize Guaranteed"
        ])
        num_picks = st.slider("🔁 How many picks do you want?", 1, 10, 1)
        euro_pool = list(range(1, 13))

        for i in range(num_picks):
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

            st.success(f"🎯 Pick {i+1}: {main} + {euro}")
            if st.button(f"✅ I Played This (Pick {i+1})", key=f"save_{i}_{strategy}"):
                save_played_pick(main, euro, strategy)
                st.info(f"Saved: {main} + {euro} under {strategy}")

# --- Arknziel Solo Pick ---
with st.expander("🔐 arknziel solo pick"):
    pw = st.text_input("Enter password", type="password")
    if pw == "arknziel":
        mode = st.radio("Select mode:", [
            "🔥 Smart Hot",
            "🕶️ Stealth: Birthday-Free",
            "🛡️ Stealth: Calendar-Aware"
        ])
        how_many = st.slider("How many arknziel picks?", 1, 10, 1)

        for i in range(how_many):
            if mode == "🔥 Smart Hot":
                main = sorted(random.sample(hot + warm, 5))
                euro = sorted(random.sample(range(1, 13), 2))
            elif mode == "🕶️ Stealth: Birthday-Free":
                cold_numbers = st.session_state["freq"].tail(30)['Number'].tolist()
                rare_pool = [n for n in cold_numbers if n > 31]
                if len(rare_pool) < 5:
                    rare_pool = cold_numbers
                main = sorted(random.sample(rare_pool, 5))
                euro = sorted(random.sample(range(5, 13), 2))
            elif mode == "🛡️ Stealth: Calendar-Aware":
                today = datetime.today()
                avoid = set(range(today.day - 1, today.day + 2)) | set(range(today.month - 1, today.month + 2)) | set(range(today.weekday(), today.weekday() + 2))
                avoid = {n for n in avoid if 1 <= n <= 50}
                cold_numbers = st.session_state["freq"].tail(30)['Number'].tolist()
                rare_pool = [n for n in cold_numbers if n not in avoid]
                if len(rare_pool) < 5:
                    rare_pool = cold_numbers
                main = sorted(random.sample(rare_pool, 5))
                euro_pool = [n for n in range(1, 13) if n not in avoid]
                if len(euro_pool) < 2:
                    euro_pool = list(range(1, 13))
                euro = sorted(random.sample(euro_pool, 2))
            st.success(f"arknziel 🎯 Pick {i+1}: {main} + {euro}")
    elif pw:
        st.error("❌ Incorrect password.")
