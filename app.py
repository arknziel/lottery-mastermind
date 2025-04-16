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

# --- Helpers ---
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

def load_data():
    if os.path.exists(EURO_FILE):
        df = pd.read_csv(EURO_FILE)
        if "Numbers" not in df.columns and "Main_Numbers" in df.columns and "Euro_Numbers" in df.columns:
            df["Main_Numbers"] = df["Main_Numbers"].apply(ast.literal_eval)
            df["Euro_Numbers"] = df["Euro_Numbers"].apply(ast.literal_eval)
            df["Numbers"] = df["Main_Numbers"] + df["Euro_Numbers"]
        else:
            df["Numbers"] = df["Numbers"].apply(ast.literal_eval)
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

# --- Load Data ---
df = load_data()

# --- App Body ---
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
                day = today.day
                month = today.month
                weekday = today.weekday()
                avoid = set(range(day - 1, day + 2)) | set(range(month - 1, month + 2)) | set(range(weekday, weekday + 2))
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

# --- My Entry Checker ---
st.markdown("---")
st.title("🎟️ My Entry Checker")

if df is not None and "Numbers" in df.columns:
    st.subheader("Select Your Played Numbers")
    main_pool = list(range(1, 51))
    euro_pool = list(range(1, 13))
    selected_main = st.multiselect("Select 5 Main Numbers", main_pool, max_selections=5)
    selected_euro = st.multiselect("Select 2 Euro Numbers", euro_pool, max_selections=2)

    st.subheader("Select the Draw Date to Compare")
    df_sorted = df.copy()
    df_sorted['Draw_Date'] = df_sorted['Draw_Date'].str.replace(r"^[A-Za-zäöüÄÖÜ]{2,3}\.\s*", "", regex=True)
    df_sorted['Draw_Date'] = pd.to_datetime(df_sorted['Draw_Date'], format="%d.%m.%Y", errors='coerce')
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

# --------- Manual Entry Form ---------
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

# --------- Optional CSV Upload ---------
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

# --------- Data View & Tools ---------
st.subheader("📅 All Draw Data (Chronologically Sorted)")
st.dataframe(master_df)

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

# --- View & Manage Saved Picks ---
st.markdown("---")
st.title("📁 My Saved Picks")

if os.path.exists(PLAYED_FILE):
    saved_df = pd.read_csv(PLAYED_FILE)
    saved_df = saved_df.sort_values(by='Date', ascending=False).reset_index(drop=True)

    # 🎯 Filter by strategy
    all_strategies = saved_df['Strategy'].unique().tolist()
    selected_strategy = st.selectbox("Filter by strategy", ["All"] + all_strategies)

    if selected_strategy != "All":
        saved_df = saved_df[saved_df['Strategy'] == selected_strategy]

    st.dataframe(saved_df, use_container_width=True)

    # 🗑️ Deletion
    pick_to_delete = st.selectbox("Select a pick to delete", saved_df['Pick'].tolist())
    if st.button("🗑️ Delete This Pick"):
        new_df = saved_df[saved_df['Pick'] != pick_to_delete]
        new_df.to_csv(PLAYED_FILE, index=False)
        st.success("✅ Pick deleted successfully! Please reload to see updated table.")
else:
    st.info("No saved picks found yet. Use the '✅ I Played This' button to track them.")
