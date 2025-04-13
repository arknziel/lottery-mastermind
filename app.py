import streamlit as st
import pandas as pd
import random
import itertools
from collections import Counter, defaultdict
import os
import ast

st.set_page_config(page_title="🎯 Eurojackpot Mastermind", layout="centered")

EURO_FILE = "eurojackpot_master_data.csv"

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
            df["Main_Numbers"] = df["Main_Numbers"].apply(eval)
            df["Euro_Numbers"] = df["Euro_Numbers"].apply(eval)
            df["Numbers"] = df["Main_Numbers"] + df["Euro_Numbers"]
        else:
            df["Numbers"] = df["Numbers"].apply(eval)
        return df
    return None

# --- App Body ---
st.title("🎯 Eurojackpot Mastermind")

# Upload Section
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

        # Strategy Generator
        st.subheader("🎯 Strategy Generator")
        strategy = st.radio("Select a strategy:", [
            "🔥 Hot Only",
            "🟡 Warm Only",
            "❄️ Cold Only",
            "⚖️ Balanced",
            "🎯 Small Win Strategy",
            "🛡️ Minimum Prize Guaranteed"
        ])

        num_picks = st.slider("🔁 How many picks do you want?", 1, 10, 1)

        if st.button("♻️ Generate Picks"):
            for i in range(num_picks):
                if strategy == "🔥 Hot Only":
                    main = sorted(random.sample(hot, 5))
                    euro = sorted(random.sample(hot, 2))
                elif strategy == "🟡 Warm Only":
                    main = sorted(random.sample(warm, 5))
                    euro = sorted(random.sample(warm, 2))
                elif strategy == "❄️ Cold Only":
                    main = sorted(random.sample(cold, 5))
                    euro = sorted(random.sample(cold, 2))
                elif strategy == "⚖️ Balanced":
                    main = sorted(random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 1))
                    euro = sorted(random.sample(warm, 1) + random.sample(cold, 1))
                elif strategy == "🎯 Small Win Strategy":
                    main = sorted(random.sample(hot + warm, 3) + random.sample(hot + warm + cold, 2))
                    euro = sorted(random.sample(hot + warm, 1) + random.sample(hot + warm + cold, 1))
                elif strategy == "🛡️ Minimum Prize Guaranteed":
                    main = sorted(random.sample(hot + warm, 5))
                    euro = sorted(random.sample(hot + warm, 2))
                st.success(f"🎯 Pick Set {i+1}: {main} + {euro}")

              # --- Arknziel Solo Pick ---
        with st.expander("🔐 arknziel solo pick"):
            pw = st.text_input("Enter password", type="password")
            if pw == "arknziel":
                mode = st.radio("Select mode:", ["🔥 Smart Hot", "🕶️ Solo Stealth"])
                how_many = st.slider("How many arknziel picks?", 1, 10, 1)

                for i in range(how_many):
                    if mode == "🔥 Smart Hot":
                        main = sorted(random.sample(hot + warm, 5))
                        euro = sorted(random.sample(hot, 2))
                    elif mode == "🕶️ Solo Stealth":
                        cold_numbers = st.session_state["freq"].tail(30)['Number'].tolist()
                        rare_pool = [n for n in cold_numbers if n > 31]
                        if len(rare_pool) < 5:
                            rare_pool = cold_numbers
                        main = sorted(random.sample(rare_pool, 5))
                        euro = sorted(random.sample([n for n in range(5, 13)], 2))

                    st.success(f"arknziel 🎯 Pick {i+1}: {main} + {euro}")
            elif pw:
                st.error("❌ Incorrect password.")


else:
    st.info("ℹ️ Upload or add data below to get started.")

# --- Manual Entry Section ---
st.subheader("➕ Add Eurojackpot Draw")
with st.form("manual_entry"):
    draw_date = st.date_input("Draw Date")
    cols = st.columns(5)
    main = [col.number_input(f"Main {i+1}", 1, 50, key=f"m{i}") for i, col in enumerate(cols)]
    euro_cols = st.columns(2)
    euro = [col.number_input(f"Euro {i+1}", 1, 12, key=f"e{i}") for i, col in enumerate(euro_cols)]
    if st.form_submit_button("Add Draw"):
        new_row = pd.DataFrame([{"Draw_Date": str(draw_date), "Numbers": str(sorted(main + euro))}])
        if os.path.exists(EURO_FILE):
            old = pd.read_csv(EURO_FILE)
            updated = pd.concat([old, new_row], ignore_index=True)
        else:
            updated = new_row
        updated.to_csv(EURO_FILE, index=False)
        st.success("✅ Draw added successfully!")

# --- Strategy Hit Tracker ---
st.markdown("---")
st.title("📊 Strategy Hit Tracker")

df = load_data()

if df is not None and "Numbers" in df.columns:
    st.subheader("🎯 Compare Strategies to Real Draws")

    num_draws = st.slider("How many past draws to test against?", 10, 100, 20, step=10)
    num_sims = st.slider("How many picks to simulate per strategy?", 5, 50, 10, step=5)

    recent_draws = df.tail(num_draws)
    past_draws = []
for _, row in recent_draws.iterrows():
    try:
        numbers = ast.literal_eval(row['Numbers'])
        if isinstance(numbers, list) and len(numbers) >= 7:
            past_draws.append((numbers[:5], numbers[5:]))
    except Exception:
        continue

    strategies = {
        "🔥 Hot Only": lambda hot, warm, cold: (random.sample(hot, 5), random.sample(hot, 2)),
        "🟡 Warm Only": lambda hot, warm, cold: (random.sample(warm, 5), random.sample(warm, 2)),
        "❄️ Cold Only": lambda hot, warm, cold: (random.sample(cold, 5), random.sample(cold, 2)),
        "⚖️ Balanced": lambda hot, warm, cold: (
            random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 1),
            random.sample(warm, 1) + random.sample(cold, 1)
        ),
        "🎯 Small Win Strategy": lambda hot, warm, cold: (
            random.sample(hot + warm, 3) + random.sample(hot + warm + cold, 2),
            random.sample(hot + warm, 1) + random.sample(hot + warm + cold, 1)
        ),
        "🛡️ Minimum Prize Guaranteed": lambda hot, warm, cold: (
            random.sample(hot + warm, 5),
            random.sample(hot + warm, 2)
        ),
    }

    if "freq" not in st.session_state:
        st.warning("Please run the Frequency Analysis first.")
    else:
        hot, warm, cold = get_heat_groups(st.session_state["freq"])
        hit_results = defaultdict(Counter)

        for strat_name, pick_func in strategies.items():
            for _ in range(num_sims):
                pick_main, pick_euro = pick_func(hot, warm, cold)
                for real_main, real_euro in past_draws:
                    main_hits = len(set(pick_main) & set(real_main))
                    euro_hits = len(set(pick_euro) & set(real_euro))
                    key = f"{main_hits}+{euro_hits}"
                    hit_results[strat_name][key] += 1

        st.subheader("📋 Strategy Hit Summary")
        all_keys = sorted({k for counts in hit_results.values() for k in counts})
        df_summary = pd.DataFrame(index=strategies.keys(), columns=all_keys).fillna(0)

        for strat, counts in hit_results.items():
            for match_type, count in counts.items():
                df_summary.loc[strat, match_type] = count

        st.dataframe(df_summary.astype(int))

# --- Draw History Viewer ---
st.markdown("---")
st.title("📋 Eurojackpot Draw History")

df = load_data()

if df is not None:
    df_display = df.copy()

    # Remove weekday prefixes like "Fr. ", "Tu. ", etc.
    df_display['Draw_Date'] = df_display['Draw_Date'].str.replace(r"^[A-Za-zäöüÄÖÜ]{2,3}\.\s*", "", regex=True)

    # Convert to datetime and sort
    df_display['Draw_Date'] = pd.to_datetime(df_display['Draw_Date'], format="%d.%m.%Y", errors='coerce')
    df_display = df_display.dropna(subset=['Draw_Date'])
    df_display = df_display.sort_values(by='Draw_Date', ascending=False)

    st.dataframe(
        df_display[['Draw_Date', 'Main_Numbers', 'Euro_Numbers']].reset_index(drop=True),
        use_container_width=True
    )
else:
    st.info("ℹ️ No draw data available. Please upload or enter draws to see history.")




