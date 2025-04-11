import streamlit as st
import pandas as pd
import itertools
from collections import Counter
import os
from datetime import date
import random
import re

st.set_page_config(page_title="Eurojackpot Mastermind", layout="centered")

MASTER_FILE = "eurojackpot_master_data.csv"

def clean_draw_date_column(df):
    df['Draw_Date'] = df['Draw_Date'].apply(lambda x: re.sub(r"^[A-Za-zäöüÄÖÜ]{2,3}\.\s*", "", x.strip()))
    return df

def analyze_frequency(df):
    all_main = list(itertools.chain.from_iterable(df['Main_Numbers']))
    all_euro = list(itertools.chain.from_iterable(df['Euro_Numbers']))
    main_freq = pd.DataFrame(Counter(all_main).items(), columns=['Number', 'Frequency']).sort_values(by='Frequency', ascending=False)
    euro_freq = pd.DataFrame(Counter(all_euro).items(), columns=['Number', 'Frequency']).sort_values(by='Frequency', ascending=False)
    return main_freq, euro_freq

def get_number_recency_groups(df, column, hot_range=5, warm_range=15, cold_gap=20):
    recent_draws = df.copy().sort_values(by='Draw_Date', ascending=False).reset_index(drop=True)
    number_positions = {}
    for i, row in recent_draws.iterrows():
        numbers = row[column]
        for number in numbers:
            if number not in number_positions:
                number_positions[number] = i
    hot = [n for n, idx in number_positions.items() if idx < hot_range]
    warm = [n for n, idx in number_positions.items() if hot_range <= idx < warm_range]
    cold = [n for n, idx in number_positions.items() if idx >= cold_gap]
    return sorted(hot), sorted(warm), sorted(cold)

def generate_heat_strategy_pick(main_groups, euro_groups, mode):
    hot, warm, cold = main_groups
    e_hot, e_warm, e_cold = euro_groups
    if mode == "🔥 Hot Only":
        main_numbers = sorted(random.sample(hot, 5))
        euro_numbers = sorted(random.sample(e_hot, 2))
    elif mode == "🟡 Warm Only":
        main_numbers = sorted(random.sample(warm, 5))
        euro_numbers = sorted(random.sample(e_warm, 2))
    elif mode == "❄️ Cold Only":
        main_numbers = sorted(random.sample(cold, 5))
        euro_numbers = sorted(random.sample(e_cold, 2))
    else:
        main_pool = random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 1)
        euro_pool = random.sample(e_hot, 1) + random.sample(e_warm, 1)
        main_numbers = sorted(main_pool)
        euro_numbers = sorted(euro_pool)
    return main_numbers, euro_numbers

def load_master_data():
    if os.path.exists(MASTER_FILE):
        df = pd.read_csv(MASTER_FILE)
        df = clean_draw_date_column(df)
        df['Main_Numbers'] = df['Main_Numbers'].apply(eval)
        df['Euro_Numbers'] = df['Euro_Numbers'].apply(eval)
        return df
    return pd.DataFrame(columns=['Draw_Date', 'Main_Numbers', 'Euro_Numbers'])

# --- MAIN APP START ---

st.title("🎯 Eurojackpot Mastermind")

master_df = load_master_data()

if st.button("📊 Run Frequency Analysis"):
    main_freq, euro_freq = analyze_frequency(master_df)
    st.session_state.update({'main_freq': main_freq, 'euro_freq': euro_freq})
    st.session_state['main_recency'] = get_number_recency_groups(master_df, 'Main_Numbers')
    st.session_state['euro_recency'] = get_number_recency_groups(master_df, 'Euro_Numbers')

if 'main_recency' in st.session_state:
    st.subheader("🔥 Hot / 🟡 Warm / ❄️ Cold Numbers")
    hot, warm, cold = st.session_state['main_recency']
    e_hot, e_warm, e_cold = st.session_state['euro_recency']
    st.markdown("### 🎯 Main Numbers")
    st.write(f"🔥 Hot: {hot}")
    st.write(f"🟡 Warm: {warm}")
    st.write(f"❄️ Cold: {cold}")
    st.markdown("### 🔵 Euro Numbers")
    st.write(f"🔥 Hot: {e_hot}")
    st.write(f"🟡 Warm: {e_warm}")
    st.write(f"❄️ Cold: {e_cold}")
    st.subheader("🎛️ Heat Strategy Generator")
    heat_mode = st.radio("Choose your strategy:", ["🔥 Hot Only", "🟡 Warm Only", "❄️ Cold Only", "⚖️ Balanced Mix"])
    if st.button("♻️ Generate Pick from Heat Strategy"):
        pick_main, pick_euro = generate_heat_strategy_pick(
            st.session_state['main_recency'],
            st.session_state['euro_recency'],
            heat_mode
        )
        st.success(f"🎯 Heat-Based Pick: {pick_main} + {pick_euro}")
