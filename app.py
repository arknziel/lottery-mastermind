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

# --- Eurojackpot Section ---
if lottery == "Eurojackpot":
    st.title("🎯 Eurojackpot Mastermind")

    df = load_data(EURO_FILE)

    if df is None:
        st.warning("⚠️ No Eurojackpot data found. Please upload a CSV or add entries below.")
    else:
        if st.button("📊 Run Frequency Analysis"):
            freq = analyze_frequency(df)
            st.session_state["ej_freq"] = freq

        if "ej_freq" in st.session_state:
            hot, warm, cold = get_heat_groups(st.session_state["ej_freq"])

            st.subheader("🔥 Heat Analyzer")
            st.write(f"🔥 Hot: {hot}")
            st.write(f"🟡 Warm: {warm}")
            st.write(f"❄️ Cold: {cold}")

            strategy = st.radio("🎛️ Heat Strategy", ["🔥 Hot Only", "🟡 Warm Only", "❄️ Cold Only", "⚖️ Balanced"])
            if st.button("♻️ Generate Eurojackpot Pick"):
                if strategy == "🔥 Hot Only":
                    pick = sorted(random.sample(hot, 5))
                    euro = sorted(random.sample(hot, 2))
                elif strategy == "🟡 Warm Only":
                    pick = sorted(random.sample(warm, 5))
                    euro = sorted(random.sample(warm, 2))
                elif strategy == "❄️ Cold Only":
                    pick = sorted(random.sample(cold, 5))
                    euro = sorted(random.sample(cold, 2))
                else:
                    pick = sorted(random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 1))
                    euro = sorted(random.sample(warm, 1) + random.sample(cold, 1))
                st.success(f"🎯 Main: {pick} + Euro: {euro}")

    # --- Manual Entry for Eurojackpot ---
    st.subheader("➕ Add Eurojackpot Draw")
    with st.form("ej_manual_entry"):
        draw_date = st.date_input("Draw Date (Eurojackpot)")
        cols = st.columns(5)
        main_numbers = [col.number_input(f"Main {i+1}", 1, 50, key=f"ej_main_{i}") for i, col in enumerate(cols)]
        euro_cols = st.columns(2)
        euro_numbers = [col.number_input(f"Euro {i+1}", 1, 12, key=f"ej_euro_{i}") for i, col in enumerate(euro_cols)]
        if st.form_submit_button("Add Draw"):
            new_row = pd.DataFrame([{
                "Draw_Date": str(draw_date),
                "Numbers": str(sorted(main_numbers + euro_numbers))
            }])
            if os.path.exists(EURO_FILE):
                old = pd.read_csv(EURO_FILE)
                updated = pd.concat([old, new_row], ignore_index=True)
            else:
                updated = new_row
            updated.to_csv(EURO_FILE, index=False)
            st.success("✅ Eurojackpot draw added!")

# --- SuperEnalotto Section ---
elif lottery == "SuperEnalotto":
    st.title("🎯 SuperEnalotto Mastermind")

    df = load_data(SUPER_FILE)

    if df is None:
        st.warning("⚠️ No SuperEnalotto data found. Please upload a CSV or add entries below.")
    else:
        if st.button("📊 Run Frequency Analysis"):
            freq = analyze_frequency(df)
            st.session_state["se_freq"] = freq

        if "se_freq" in st.session_state:
            hot, warm, cold = get_heat_groups(st.session_state["se_freq"])

            st.subheader("🔥 Heat Analyzer")
            st.write(f"🔥 Hot: {hot}")
            st.write(f"🟡 Warm: {warm}")
            st.write(f"❄️ Cold: {cold}")

            strategy = st.radio("🎛️ Heat Strategy", ["🔥 Hot Only", "🟡 Warm Only", "❄️ Cold Only", "⚖️ Balanced"])
            if st.button("♻️ Generate SuperEnalotto Pick"):
                if strategy == "🔥 Hot Only":
                    pick = sorted(random.sample(hot, 6))
                elif strategy == "🟡 Warm Only":
                    pick = sorted(random.sample(warm, 6))
                elif strategy == "❄️ Cold Only":
                    pick = sorted(random.sample(cold, 6))
                else:
                    pick = sorted(random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 2))
                st.success(f"🎯 SuperEnalotto Pick: {pick}")

    # --- Manual Entry for SuperEnalotto ---
    st.subheader("➕ Add SuperEnalotto Draw")
    with st.form("se_manual_entry"):
        draw_date = st.date_input("Draw Date (SuperEnalotto)")
        cols = st.columns(6)
        numbers = [col.number_input(f"Number {i+1}", 1, 90, key=f"se_n{i}") for i, col in enumerate(cols)]
        if st.form_submit_button("Add Draw"):
            new_row = pd.DataFrame([{
                "Draw_Date": str(draw_date),
                "Numbers": str(sorted(numbers))
            }])
            if os.path.exists(SUPER_FILE):
                old = pd.read_csv(SUPER_FILE)
                updated = pd.concat([old, new_row], ignore_index=True)
            else:
                updated = new_row
            updated.to_csv(SUPER_FILE, index=False)
            st.success("✅ SuperEnalotto draw added!")
