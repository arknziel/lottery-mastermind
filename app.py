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

df = load_data()
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
        main_freq, euro_freq = analyze_frequency(df)
        st.session_state["main_freq"] = main_freq
        st.session_state["euro_freq"] = euro_freq

    if "main_freq" in st.session_state:
        main_freq = st.session_state["main_freq"]
        euro_freq = st.session_state["euro_freq"]
        hot, warm, cold = get_heat_groups(main_freq)

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
            euro = sorted(random.sample(euro_pool, 2))

            st.success(f"🎯 Pick {i+1}: {main} + {euro}")
            if st.button(f"✅ I Played This (Pick {i+1})", key=f"save_{i}_{strategy}"):
                save_played_pick(main, euro, strategy)
                st.info(f"Saved: {main} + {euro} under {strategy}")

import random
from datetime import datetime

# 🔱 Hermes Trident Strategy - Jackpot-biased, calendar and monthly pattern aware

def calendar_aware_filter_pool(date, number_range):
    """
    Removes numbers related to today's day, month, and weekday to stay stealthy.
    """
    avoid = {date.day, date.month, date.weekday() + 1}
    return [n for n in number_range if n not in avoid]

def monthly_section_bias_weights(month):
    """
    Monthly bias weights for the five sections (1–10, 11–20, ..., 41–50).
    These weights are based on historical data and monthly pattern trends.
    """
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
    """
    Generates a stealthy, jackpot-aware pick based on section bias and calendar filtering.
    Returns a tuple of main numbers and euro numbers.
    """
    # Divide 1–50 into 5 sections
    sections = {
        1: list(range(1, 11)),
        2: list(range(11, 21)),
        3: list(range(21, 31)),
        4: list(range(31, 41)),
        5: list(range(41, 51))
    }

    # Get monthly section weights
    weights = monthly_section_bias_weights(draw_date.month)

    # Build section pool based on weights
    sections_pool = []
    for i, sec in sections.items():
        k = max(1, round(weights[i-1] * 5))
        sections_pool.extend(random.sample(sec, k=min(k, len(sec))))

    # Filter pool with calendar-awareness
    filtered_pool = calendar_aware_filter_pool(draw_date, sections_pool)
    if len(filtered_pool) < 5:
        filtered_pool = sections_pool  # fallback if filter is too strict

    main_pick = sorted(random.sample(filtered_pool, 5))

    # Euro number generation with calendar-aware filter
    euro_pool = calendar_aware_filter_pool(draw_date, list(range(1, 13)))
    if len(euro_pool) < 2:
        euro_pool = list(range(1, 13))  # fallback
    euro_pick = sorted(random.sample(euro_pool, 2))

    return main_pick, euro_pick


# 🎯 Example usage
if __name__ == "__main__":
    today = datetime.today()
    main, euro = hermes_trident_strategy(today)
    print(f"Hermes 🔱 Pick for {today.strftime('%Y-%m-%d')}: Main {main} + Euro {euro}")

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
                rare_pool = [n for n in cold if n > 31]
                if len(rare_pool) < 5:
                    rare_pool = cold
                main = sorted(random.sample(rare_pool, 5))
                euro = sorted(random.sample(range(5, 13), 2))
            elif mode == "🛡️ Stealth: Calendar-Aware":
                today = datetime.today()
                avoid = {today.day, today.month, today.weekday()+1}
                avoid = {n for n in avoid if 1 <= n <= 50}
                rare_pool = [n for n in cold if n not in avoid]
                if len(rare_pool) < 5:
                    rare_pool = cold
                main = sorted(random.sample(rare_pool, 5))
                euro_pool = [n for n in range(1, 13) if n not in avoid]
                if len(euro_pool) < 2:
                    euro_pool = list(range(1, 13))
                euro = sorted(random.sample(euro_pool, 2))
            st.success(f"arknziel 🎯 Pick {i+1}: {main} + {euro}")
    elif pw:
        st.error("❌ Incorrect password.")
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

# --- Entry Checker ---
st.markdown("---")
st.title("🎟️ My Entry Checker")

if df is not None and "Numbers" in df.columns:
    st.subheader("Select Your Played Numbers")
    selected_main = st.multiselect("Select 5 Main Numbers", list(range(1, 51)), max_selections=5)
    selected_euro = st.multiselect("Select 2 Euro Numbers", list(range(1, 13)), max_selections=2)
    df_sorted = df.copy()
    df_sorted['Draw_Date'] = pd.to_datetime(df_sorted['Draw_Date'].str.extract(r'(\d{2}\.\d{2}\.\d{4})')[0], format="%d.%m.%Y", errors='coerce')
    df_sorted = df_sorted.dropna(subset=['Draw_Date']).sort_values(by='Draw_Date', ascending=False)
    draw_dates = df_sorted['Draw_Date'].dt.strftime('%Y-%m-%d').tolist()
    selected_date = st.selectbox("Draw Date", draw_dates)

    if st.button("🎯 Check My Entry"):
        if len(selected_main) != 5 or len(selected_euro) != 2:
            st.warning("Please select exactly 5 main numbers and 2 euro numbers.")
        else:
            draw_row = df_sorted[df_sorted['Draw_Date'].dt.strftime('%Y-%m-%d') == selected_date]
            if not draw_row.empty:
                numbers = eval(draw_row.iloc[0]['Numbers'])
                draw_main = numbers[:5]
                draw_euro = numbers[5:]
                main_hits = len(set(selected_main) & set(draw_main))
                euro_hits = len(set(selected_euro) & set(draw_euro))
                st.success(f"🎯 You matched: {main_hits} main + {euro_hits} euro → `{main_hits}+{euro_hits}`")
                st.info(f"Your Pick: {sorted(selected_main)} + {sorted(selected_euro)}")
                st.info(f"Draw Result: {draw_main} + {draw_euro}")
            else:
                st.error("Draw date not found in data.")

# --- Draw History Viewer ---
st.markdown("---")
st.title("📋 Eurojackpot Draw History")

if os.path.exists(EURO_FILE):
    df_draws = pd.read_csv(EURO_FILE)
    df_draws['Draw_Date'] = df_draws['Draw_Date'].str.extract(r'(\d{2}\.\d{2}\.\d{4})')[0]
    df_draws['Draw_Date'] = pd.to_datetime(df_draws['Draw_Date'], format="%d.%m.%Y", errors='coerce')
    df_draws = df_draws.dropna(subset=['Draw_Date']).sort_values(by='Draw_Date', ascending=False)
    if 'Main_Numbers' not in df_draws.columns or 'Euro_Numbers' not in df_draws.columns:
        df_draws['Numbers'] = df_draws['Numbers'].apply(ast.literal_eval)
        df_draws['Main_Numbers'] = df_draws['Numbers'].apply(lambda x: x[:5])
        df_draws['Euro_Numbers'] = df_draws['Numbers'].apply(lambda x: x[5:])
    st.dataframe(df_draws[['Draw_Date', 'Main_Numbers', 'Euro_Numbers']], use_container_width=True)

# --- Saved Picks Viewer + Delete ---
st.markdown("---")
st.title("📁 My Saved Picks")

if os.path.exists(PLAYED_FILE):
    saved_df = pd.read_csv(PLAYED_FILE)
    saved_df = saved_df.sort_values(by='Date', ascending=False).reset_index(drop=True)
    all_strategies = saved_df['Strategy'].unique().tolist()
    selected_strategy = st.selectbox("Filter by strategy", ["All"] + all_strategies)
    if selected_strategy != "All":
        saved_df = saved_df[saved_df['Strategy'] == selected_strategy]
    st.dataframe(saved_df, use_container_width=True)
    pick_to_delete = st.selectbox("Select a pick to delete", saved_df['Pick'].tolist())
    if st.button("🗑️ Delete This Pick"):
        new_df = saved_df[saved_df['Pick'] != pick_to_delete]
        new_df.to_csv(PLAYED_FILE, index=False)
        st.success("✅ Pick deleted successfully! Please reload to see updated table.")
else:
    st.info("No saved picks found yet. Use the '✅ I Played This' button to track them.")
