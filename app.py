import streamlit as st
import pandas as pd
import random
import itertools
from collections import Counter
from datetime import datetime
import os
import ast

# --- App Configuration ---
st.set_page_config(page_title="🎯 Eurojackpot Mastermind", layout="centered")

EURO_FILE = "eurojackpot_master_data.csv"
PLAYED_FILE = "played_picks.csv"

# --- Safe Parser ---
def safe_parse(x):
    try:
        return ast.literal_eval(str(x))
    except Exception:
        return []

# --- Robust Data Loader ---
def load_data():
    if os.path.exists(EURO_FILE):
        df = pd.read_csv(EURO_FILE)

        if "Numbers" not in df.columns and "Main_Numbers" in df.columns and "Euro_Numbers" in df.columns:
            df["Main_Numbers"] = df["Main_Numbers"].astype(str).apply(safe_parse)
            df["Euro_Numbers"] = df["Euro_Numbers"].astype(str).apply(safe_parse)
            df["Numbers"] = df["Main_Numbers"] + df["Euro_Numbers"]

        elif "Numbers" in df.columns:
            df["Numbers"] = df["Numbers"].astype(str).apply(safe_parse)
            if "Main_Numbers" not in df.columns or "Euro_Numbers" not in df.columns:
                df["Main_Numbers"] = df["Numbers"].apply(lambda x: x[:5])
                df["Euro_Numbers"] = df["Numbers"].apply(lambda x: x[5:])

        else:
            df["Numbers"] = [[] for _ in range(len(df))]
            df["Main_Numbers"] = [[] for _ in range(len(df))]
            df["Euro_Numbers"] = [[] for _ in range(len(df))]

        return df

    return None

# --- Frequency Analysis ---
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

# --- Prize Ladder number generation ---
def generate_prize_ladder_pick(draw_main_pool):
    pool = list(range(1, 51))
    repeat_pool = list(set(draw_main_pool)) if isinstance(draw_main_pool, list) else []

    tries = 0
    while tries < 100:
        repeat_count = random.choice([1, 2])
        repeat_part = random.sample(repeat_pool, min(len(repeat_pool), repeat_count))

        remaining_pool = [n for n in pool if n not in repeat_part]
        needed = 5 - len(repeat_part)

        if len(remaining_pool) < needed:
            tries += 1
            continue

        full_candidate = repeat_part + random.sample(remaining_pool, needed)
        full_candidate = sorted(full_candidate)
        total_sum = sum(full_candidate)
        even_count = sum(1 for n in full_candidate if n % 2 == 0)

        if 100 <= total_sum <= 140 and 2 <= even_count <= 3:
            return full_candidate, sorted(random.sample(range(1, 13), 2))

        tries += 1

    return sorted(random.sample(pool, 5)), sorted(random.sample(range(1, 13), 2))

# --- Hermes–Hybrid number generation ---
def generate_hermes_hybrid_pick(date):
    month = date.month
    weekday = date.weekday() + 1
    day = date.day

    combined_pool = list(range(1, 51))
    selected_numbers = sorted(random.sample(combined_pool, 5))
    euro = sorted(random.sample(range(1, 13), 2))
    return selected_numbers, euro

# --- Played Pick Saver ---
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

# --- Load existing data ---
df = load_data()

# --- Streamlit App UI ---
st.title("🎯 Eurojackpot Mastermind")

# --- Best Combo Strategy ---
st.markdown("---")
st.header("🏆 Best Combo Strategy (1 Hermes + 4 Prize Ladder)")
combo_sessions = st.slider("How many sessions to generate?", 1, 10, 1, key="best_combo_sessions")
if st.button("🎯 Generate Best Combo Picks", key="generate_best_combo_button"):
    if df is not None and not df.empty:
        draw_main_pool = df.iloc[-1]['Main_Numbers']
        for session in range(combo_sessions):
            st.subheader(f"🎟️ Session {session + 1}")
            main, euro = generate_hermes_hybrid_pick(datetime.today())
            st.success(f"Hermes 🎯 Pick: {main} + {euro}")
            for j in range(4):
                main, euro = generate_prize_ladder_pick(draw_main_pool)
                st.info(f"Prize Ladder 📈 Pick {j + 1}: {main} + {euro}")

# --- CSV Upload ---
st.subheader("📤 Upload Eurojackpot CSV")
ej_file = st.file_uploader("Choose Eurojackpot CSV", type="csv", key="ej_upload")
if ej_file:
    uploaded_df = pd.read_csv(ej_file)
    uploaded_df.to_csv(EURO_FILE, index=False)
    st.success("✅ File uploaded and saved!")
    df = load_data()

# --- Frequency Analysis ---
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
            "⚖️ Balanced", "🎯 Small Win Strategy", "🛡️ Minimum Prize Guaranteed",
            "🔱 Hermes Strategy"
        ])
        num_picks = st.slider("🔁 How many picks do you want?", 1, 10, 1)
        euro_pool = list(range(1, 13))

        for i in range(num_picks):
            if strategy == "🔥 Hot Only":
                main = sorted(random.sample(hot, 5))
            elif strategy == "🟡 Warm Only":
                main = sorted(random.sample(warm, 5))
            elif strategy == "❄️ Cold Only":
                main = sorted(random.sample(cold, 5))
            elif strategy == "⚖️ Balanced":
                main = sorted(random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 1))
            elif strategy == "🎯 Small Win Strategy":
                main = sorted(random.sample(hot + warm, 3) + random.sample(hot + warm + cold, 2))
            elif strategy == "🛡️ Minimum Prize Guaranteed":
                main = sorted(random.sample(hot + warm, 5))
            else:
                main = sorted(random.sample(cold, 5))  # Default fallback

            euro = sorted(random.sample(euro_pool, 2))
            st.success(f"🎯 Pick {i+1}: {main} + {euro}")
            if st.button(f"✅ I Played This (Pick {i+1})", key=f"save_{i}_{strategy}"):
                save_played_pick(main, euro, strategy)
                st.info(f"Saved: {main} + {euro} under {strategy}")

# --- Manual Draw Entry ---
st.markdown("---")
st.title("➕ Add Latest Eurojackpot Draw")
with st.form("manual_draw_entry"):
    draw_date = st.date_input("Draw Date")
    cols = st.columns(5)
    main_numbers = [col.number_input(f"Main {i+1}", 1, 50, key=f"main_{i}") for i, col in enumerate(cols)]
    euro_cols = st.columns(2)
    euro_numbers = [col.number_input(f"Euro {i+1}", 1, 12, key=f"euro_{i}") for i, col in enumerate(euro_cols)]
    if st.form_submit_button("➕ Add Draw"):
        new_row = pd.DataFrame([{
            "Draw_Date": draw_date.strftime("%d.%m.%Y"),
            "Main_Numbers": str(sorted(main_numbers)),
            "Euro_Numbers": str(sorted(euro_numbers)),
            "Numbers": str(sorted(main_numbers + euro_numbers))
        }])
        if os.path.exists(EURO_FILE):
            existing = pd.read_csv(EURO_FILE)
            updated = pd.concat([existing, new_row], ignore_index=True)
        else:
            updated = new_row
        updated.to_csv(EURO_FILE, index=False)
        st.success("✅ Draw added successfully!")
