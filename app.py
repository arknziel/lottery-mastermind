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

def is_popular_pick(main_numbers):
    return (
        all(n <= 31 for n in main_numbers) or
        all(main_numbers[i] + 1 == main_numbers[i+1] for i in range(len(main_numbers)-1)) or
        len(set(n % 10 for n in main_numbers)) == 1
    )

def generate_solo_win_pick(main_freq, euro_freq):
    rare_main = main_freq.sort_values(by='Frequency').head(20)['Number'].tolist()
    rare_euro = euro_freq.sort_values(by='Frequency').head(6)['Number'].tolist()
    return sorted(rare_main[:5]), sorted(rare_euro[:2])

def generate_small_win_strategy_pick(main_freq, euro_freq):
    main_numbers = sorted(random.sample(main_freq.head(10)['Number'].tolist(), 3) +
                          random.sample(main_freq.iloc[10:25]['Number'].tolist(), 2))
    euro_numbers = sorted(random.sample(euro_freq.head(3)['Number'].tolist(), 1) +
                          random.sample(euro_freq.iloc[3:8]['Number'].tolist(), 1))
    return main_numbers, euro_numbers

def generate_minimum_prize_picks(main_freq, euro_freq):
    main_numbers = sorted(random.sample(main_freq.head(12)['Number'].tolist(), 3) +
                          random.sample(main_freq.iloc[12:25]['Number'].tolist(), 2))
    euro_numbers = sorted(random.sample(euro_freq.head(4)['Number'].tolist(), 1) +
                          random.sample(euro_freq.iloc[4:8]['Number'].tolist(), 1))
    return main_numbers, euro_numbers

def generate_multiple_picks(main_freq, euro_freq, num_picks=5, strategy_mode="Rare Focus", avoid_popular=True):
    picks = []
    attempts = 0

    while len(picks) < num_picks and attempts < 100:
        if strategy_mode == "Small Win Strategy":
            pick_main, pick_euro = generate_small_win_strategy_pick(main_freq, euro_freq)
        elif strategy_mode == "Minimum Prize Guaranteed":
            pick_main, pick_euro = generate_minimum_prize_picks(main_freq, euro_freq)
        else:
            rare_main = main_freq.tail(25)['Number'].tolist()
            rare_euro = euro_freq.tail(8)['Number'].tolist()
            pick_main = sorted(random.sample(rare_main, 5))
            pick_euro = sorted(random.sample(rare_euro, 2))

        if avoid_popular and is_popular_pick(pick_main):
            attempts += 1
            continue

        picks.append((pick_main, pick_euro))
        attempts += 1

    return picks

def load_master_data():
    if os.path.exists(MASTER_FILE):
        df = pd.read_csv(MASTER_FILE)
        df = clean_draw_date_column(df)
        df['Main_Numbers'] = df['Main_Numbers'].apply(eval)
        df['Euro_Numbers'] = df['Euro_Numbers'].apply(eval)
        return df
    return pd.DataFrame(columns=['Draw_Date', 'Main_Numbers', 'Euro_Numbers'])

def merge_new_draws(master_df, new_df):
    new_df = clean_draw_date_column(new_df)
    new_df['Main_Numbers'] = new_df['Main_Numbers'].apply(eval)
    new_df['Euro_Numbers'] = new_df['Euro_Numbers'].apply(eval)
    combined_df = pd.concat([master_df, new_df], ignore_index=True)
    combined_df.drop_duplicates(subset=['Draw_Date', 'Main_Numbers', 'Euro_Numbers'], inplace=True)
    combined_df['Parsed_Date'] = pd.to_datetime(combined_df['Draw_Date'], errors='coerce')
    combined_df.dropna(subset=['Parsed_Date'], inplace=True)
    combined_df.sort_values(by='Parsed_Date', inplace=True)
    return combined_df.drop(columns='Parsed_Date').reset_index(drop=True)

# App UI
st.title("🎯 Eurojackpot Mastermind")

# Manual Entry
st.subheader("✍️ Add New Draw Manually")
with st.form("manual_entry_form"):
    draw_date = st.date_input("Draw Date", date.today())
    cols_main = st.columns(5)
    main_numbers = [col.number_input(f"Main {i+1}", 1, 50) for i, col in enumerate(cols_main)]
    cols_euro = st.columns(2)
    euro_numbers = [col.number_input(f"Euro {i+1}", 1, 12) for i, col in enumerate(cols_euro)]
    if st.form_submit_button("➕ Add Draw"):
        new_draw = pd.DataFrame([{
            "Draw_Date": str(draw_date),
            "Main_Numbers": str(sorted(main_numbers)),
            "Euro_Numbers": str(sorted(euro_numbers))
        }])
        master_df = merge_new_draws(load_master_data(), new_draw)
        master_df.to_csv(MASTER_FILE, index=False)
        st.success("✅ Draw added!")

# CSV Upload
st.subheader("📂 Upload Draws (CSV)")
uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    new_df = pd.read_csv(uploaded_file)
    master_df = merge_new_draws(load_master_data(), new_df)
    master_df.to_csv(MASTER_FILE, index=False)
    st.success("✅ CSV data merged!")

master_df = load_master_data()
st.subheader("📅 Draw History")
st.dataframe(master_df)

# Analysis & Strategies
if st.button("📊 Run Frequency Analysis"):
    main_freq, euro_freq = analyze_frequency(master_df)
    st.session_state.update({'main_freq': main_freq, 'euro_freq': euro_freq})

if 'main_freq' in st.session_state:
    st.subheader("🔐 arknziel")
    password = st.text_input("Enter password to unlock this tool", type="password")
    if password == "eurosecret":
        if st.button("🔐 Generate arknziel Pick"):
            main, euro = generate_solo_win_pick(st.session_state['main_freq'], st.session_state['euro_freq'])
            st.success(f"🎯 Your Pick: {main} + {euro}")
    elif password:
        st.warning("❌ Incorrect password. Try again.")

    strategy_mode = st.radio("🎯 Pick Strategy:", ["Rare Focus", "Small Win Strategy", "Minimum Prize Guaranteed"])
    avoid_popular = st.checkbox("🛡️ Avoid Popular Picks", value=True)
    num_picks = st.slider("Number of Picks", 1, 20, 5)

    if st.button("🔁 Generate Multiple Picks"):
        picks = generate_multiple_picks(st.session_state['main_freq'], st.session_state['euro_freq'],
                                        num_picks, strategy_mode, avoid_popular)
        for i, (main, euro) in enumerate(picks, 1):
            st.success(f"Pick {i}: {main} + {euro}")
