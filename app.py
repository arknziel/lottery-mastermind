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

# Strategy toggle
USE_POPULAR_FILTER = st.sidebar.checkbox("🛡️ Avoid Popular Picks", value=True)

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
    if all(n <= 31 for n in main_numbers):
        return True
    if all(main_numbers[i] + 1 == main_numbers[i+1] for i in range(len(main_numbers)-1)):
        return True
    endings = [n % 10 for n in main_numbers]
    if len(set(endings)) == 1:
        return True
    return False

def generate_solo_win_pick(main_freq, euro_freq):
    rare_main = main_freq.sort_values(by='Frequency').head(20)['Number'].tolist()
    rare_euro = euro_freq.sort_values(by='Frequency').head(6)['Number'].tolist()
    return sorted(rare_main[:5]), sorted(rare_euro[:2])

def generate_multiple_picks(main_freq, euro_freq, num_picks=5):
    rare_main = main_freq.sort_values(by='Frequency').head(25)['Number'].tolist()
    rare_euro = euro_freq.sort_values(by='Frequency').head(8)['Number'].tolist()
    picks = []
    attempts = 0
    while len(picks) < num_picks and attempts < 100:
        pick_main = sorted(random.sample(rare_main, 5))
        if USE_POPULAR_FILTER and is_popular_pick(pick_main):
            st.info(f"⚠️ Skipped popular pick: {pick_main}")
            attempts += 1
            continue
        pick_euro = sorted(random.sample(rare_euro, 2))
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
    combined_df['Main_Str'] = combined_df['Main_Numbers'].apply(str)
    combined_df['Euro_Str'] = combined_df['Euro_Numbers'].apply(str)
    combined_df = combined_df.drop_duplicates(subset=['Draw_Date', 'Main_Str', 'Euro_Str'])
    combined_df = combined_df.drop(columns=['Main_Str', 'Euro_Str'])
    combined_df['Parsed_Date'] = pd.to_datetime(combined_df['Draw_Date'], errors='coerce')
    combined_df = combined_df.dropna(subset=['Parsed_Date'])
    combined_df = combined_df.sort_values(by='Parsed_Date').drop(columns='Parsed_Date').reset_index(drop=True)
    return combined_df

st.title("🎯 Eurojackpot Mastermind (Strategy Toggle Ready)")
master_df = load_master_data()

st.subheader("✍️ Add New Draw Manually")
with st.form("manual_entry_form"):
    draw_date = st.date_input("Draw Date", value=date.today())
    col1, col2, col3, col4, col5 = st.columns(5)
    main_numbers = [
        col1.number_input("Main 1", 1, 50, key="m1"),
        col2.number_input("Main 2", 1, 50, key="m2"),
        col3.number_input("Main 3", 1, 50, key="m3"),
        col4.number_input("Main 4", 1, 50, key="m4"),
        col5.number_input("Main 5", 1, 50, key="m5")
    ]
    col6, col7 = st.columns(2)
    euro_numbers = [
        col6.number_input("Euro 1", 1, 12, key="e1"),
        col7.number_input("Euro 2", 1, 12, key="e2")
    ]
    submitted = st.form_submit_button("➕ Add Draw")

if submitted:
    new_row = pd.DataFrame([{
        "Draw_Date": str(draw_date),
        "Main_Numbers": str(sorted(main_numbers)),
        "Euro_Numbers": str(sorted(euro_numbers))
    }])
    master_df = merge_new_draws(master_df, new_row)
    master_df.to_csv(MASTER_FILE, index=False)
    master_df = load_master_data()
    st.success("✅ Draw added and saved!")

st.subheader("📂 Or Upload New Draws (CSV)")
uploaded_file = st.file_uploader("Upload your new draw data", type=["csv"])
if uploaded_file:
    try:
        new_df = pd.read_csv(uploaded_file)
        if 'Draw_Date' in new_df.columns and 'Main_Numbers' in new_df.columns and 'Euro_Numbers' in new_df.columns:
            master_df = merge_new_draws(master_df, new_df)
            master_df.to_csv(MASTER_FILE, index=False)
            master_df = load_master_data()
            st.success("✅ Uploaded CSV merged and saved!")
        else:
            st.error("CSV must include Draw_Date, Main_Numbers, and Euro_Numbers")
    except Exception as e:
        st.error(f"⚠️ Error reading CSV: {e}")

st.subheader("📅 All Draw Data (Chronologically Sorted)")
st.dataframe(master_df)

if st.button("📊 Run Frequency Analysis"):
    main_freq, euro_freq = analyze_frequency(master_df)
    st.session_state['main_freq'] = main_freq.copy()
    st.session_state['euro_freq'] = euro_freq.copy()

if 'main_freq' in st.session_state:
    st.subheader("🔥 Main Number Frequency")
    st.dataframe(st.session_state['main_freq'])
    st.subheader("🔵 Euro Number Frequency")
    st.dataframe(st.session_state['euro_freq'])

    st.subheader("🎯 Generate Smart Solo Pick")
    if st.button("🎯 Generate One Pick"):
        main, euro = generate_solo_win_pick(st.session_state['main_freq'], st.session_state['euro_freq'])
        st.success(f"🎯 Your Pick: {main} + {euro}")

    st.subheader("🎯 Generate Multiple Picks")
    num_picks = st.slider("Number of Picks", min_value=1, max_value=20, value=5)
    if st.button("🔁 Generate Multiple Picks"):
        picks = generate_multiple_picks(st.session_state['main_freq'], st.session_state['euro_freq'], num_picks)
        for i, (main, euro) in enumerate(picks, 1):
            st.success(f"Pick {i}: {main} + {euro}")
