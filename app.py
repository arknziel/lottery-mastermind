
# Prize Ladder number generation

def generate_prize_ladder_pick(draw_main_pool):
    import random
    pool = list(range(1, 51))
    repeat_pool = list(set(draw_main_pool)) if isinstance(draw_main_pool, list) else []

    tries = 0
    while tries < 100:
        repeat_count = random.choice([1, 2])
        if len(repeat_pool) < repeat_count:
            repeat_part = repeat_pool
        else:
            repeat_part = random.sample(repeat_pool, repeat_count)

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



# Ensure the function for Hermes-Hybrid pick is defined
import random
from datetime import datetime

# Hermes–Hybrid number generation
def generate_hermes_hybrid_pick(date):
    month = date.month
    weekday = date.weekday() + 1
    day = date.day

    # Simplified function logic based on earlier definitions
    combined_pool = list(range(1, 51))  # numbers 1-50 as a simple example
    selected_numbers = sorted(random.sample(combined_pool, 5))  # simple number selection
    euro = sorted(random.sample(range(1, 13), 2))  # Euro numbers 1-12
    return selected_numbers, euro

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

# --- 🏆 Best Combo Strategy (1 Hermes + 4 Prize Ladder) ---
st.markdown("---")
st.header("🏆 Best Combo Strategy (1 Hermes + 4 Prize Ladder)")
st.markdown("This section generates **5 smart picks per session**: **1 Hermes–Hybrid** + **4 Prize Ladder**.")

combo_sessions = st.slider("How many sessions to generate?", 1, 10, 1, key="best_combo_sessions")

if st.button("🎯 Generate Best Combo Picks", key="generate_best_combo_button"):
    import ast
    if isinstance(df.iloc[-1]['Main_Numbers'], str):
        draw_main_pool = ast.literal_eval(df.iloc[-1]['Main_Numbers'])
    else:
        draw_main_pool = df.iloc[-1]['Main_Numbers']

    for session in range(combo_sessions):
        st.subheader(f"🎟️ Session {session + 1}")
        # 1 Hermes Pick
        main, euro = generate_hermes_hybrid_pick(datetime.today())
        st.success(f"Hermes 🎯 Pick: {main} + {euro}")
        # 4 Prize Ladder Picks
        for j in range(4):
            main, euro = generate_prize_ladder_pick(draw_main_pool)
            st.info(f"Prize Ladder 📈 Pick {j + 1}: {main} + {euro}")


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
            "⚖️ Balanced", "🎯 Small Win Strategy", "🛡️ Minimum Prize Guaranteed",
            "🔱 Hermes Strategy"
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

            


            
            elif strategy == "🔱 Hermes Strategy":
                month = datetime.today().month
                weekday = datetime.today().weekday() + 1
                day = datetime.today().day

                section_map = {
                    1: list(range(1, 11)),
                    2: list(range(11, 21)),
                    3: list(range(21, 31)),
                    4: list(range(31, 41)),
                    5: list(range(41, 51)),
                }

                monthly_section_weights = {
                    1: 0.1,
                    2: 0.3 if month == 4 else 0.2,
                    3: 0.2,
                    4: 0.1,
                    5: 0.3 if month == 4 else 0.2,
                }

                selected_sections = [sec for sec, w in monthly_section_weights.items() if w >= 0.2]
                calendar_avoid = {day, month, weekday}
                cold_pool = [n for n in cold if 1 <= n <= 50]
                hermes_pool = []

                for sec in selected_sections:
                    nums = [n for n in section_map[sec] if n in cold_pool and n not in calendar_avoid]
                    hermes_pool.extend(nums)

                if len(hermes_pool) < 5:
                    hermes_pool = [n for sec in selected_sections for n in section_map[sec] if n in cold_pool]

                if len(hermes_pool) < 5:
                    hermes_pool = cold_pool

                main = []
                tries = 0
                enable_bias = st.checkbox("🎯 Enable Jackpot Bias (120–160 sum)", key=f"bias_{i}_{strategy}")
                while tries < 50:
                    if len(hermes_pool) >= 5:
                        candidate = sorted(random.sample(hermes_pool, 5))
                        if enable_bias:
                            if 120 <= sum(candidate) <= 160:
                                main = candidate
                                break
                        else:
                            main = candidate
                            break
                    tries += 1

                if not main:
                    main = sorted(random.sample(cold_pool, 5))
                euro = sorted(random.sample(euro_pool, 2))

                st.success(f"🎯 Pick {i+1}: {main} + {euro}")
                if st.button(f"✅ I Played This (Pick {i+1})", key=f"save_{i}_{strategy}"):
                    save_played_pick(main, euro, strategy)
                    st.info(f"Saved: {main} + {euro} under {strategy}")





# --- Best Combo Strategy (Hermes + Prize Ladder) Button Fix ---
st.markdown("---")
st.header("🏆 Best Combo Strategy (Hermes + Prize Ladder)")
st.markdown("This section generates 5 smart picks per session: **2 Hermes–Hybrid** + **3 Prize Ladder**.")

num_sessions = st.slider("How many sessions to generate?", 1, 10, 1, key="combo_sessions_unique")

# The button to trigger the strategy generation
if st.button("🎯 Generate Best Combo Picks", key="generate_combo_picks_button"):
    for session in range(num_sessions):
        st.subheader(f"🎟️ Session {session + 1}")
        for i in range(2):  # Hermes
            main, euro = generate_hermes_hybrid_pick(datetime.today())
            st.success(f"Hermes 🎯 Pick {i + 1}: {main} + {euro}")
        for i in range(3):  # Prize Ladder
            main, euro = generate_prize_ladder_pick(df.iloc[-1]['Main_Numbers'])
            st.info(f"Prize Ladder 📈 Pick {i + 3 + 1}: {main} + {euro}")


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

# --- Draw History Viewer ---
st.markdown("---")
st.title("📋 Eurojackpot Draw History")

if os.path.exists(EURO_FILE):
    df_draws = pd.read_csv(EURO_FILE)
    df_draws['Draw_Date'] = df_draws['Draw_Date'].str.replace(r"^[A-Za-zäöüÄÖÜ]{2,3}\.\s*", "", regex=True)
    df_draws['Draw_Date'] = pd.to_datetime(df_draws['Draw_Date'], format="%d.%m.%Y", errors='coerce')
    df_draws = df_draws.dropna(subset=['Draw_Date']).sort_values(by='Draw_Date', ascending=False)
    if 'Main_Numbers' not in df_draws.columns or 'Euro_Numbers' not in df_draws.columns:
        df_draws['Numbers'] = df_draws['Numbers'].apply(ast.literal_eval)
        df_draws['Main_Numbers'] = df_draws['Numbers'].apply(lambda x: x[:5])
        df_draws['Euro_Numbers'] = df_draws['Numbers'].apply(lambda x: x[5:])
    st.dataframe(df_draws[['Draw_Date', 'Main_Numbers', 'Euro_Numbers']].reset_index(drop=True), use_container_width=True)

# --- Saved Picks Table with Filter and Delete ---
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


# --- Best Combo Strategy (Hermes + Prize Ladder) ---
st.markdown("---")
st.header("🏆 Best Combo Strategy (Hermes + Prize Ladder)")
st.markdown("This section generates 5 smart picks per session: **2 Hermes–Hybrid** + **3 Prize Ladder**.")

num_sessions = st.slider("How many sessions to generate?", 1, 10, 1, key="combo_sessions")

if st.button("🎯 Generate Best Combo Picks"):
    for session in range(num_sessions):
        st.subheader(f"🎟️ Session {session + 1}")
        for i in range(2):  # Hermes
            main, euro = generate_hermes_hybrid_pick(datetime.today())
            st.success(f"Hermes 🎯 Pick {i + 1}: {main} + {euro}")
        for i in range(3):  # Prize Ladder
            main, euro = generate_prize_ladder_pick(df.iloc[-1]['Main_Numbers'])
            st.info(f"Prize Ladder 📈 Pick {i + 3 + 1}: {main} + {euro}")
