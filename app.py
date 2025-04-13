import streamlit as st
import pandas as pd
import random
import itertools
from collections import Counter
import os

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

        if st.button("♻️ Generate Pick"):
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
            st.success(f"🎯 Your Pick: {main} + {euro}")

        # Arknziel Solo Pick
        with st.expander("🔐 arknziel solo pick"):
            pw = st.text_input("Enter password", type="password")
            if pw == "arknziel":
                pick = sorted(random.sample(hot + warm, 5))
                euro = sorted(random.sample(hot, 2))
                st.success(f"arknziel 🎯 {pick} + {euro}")
            elif pw:
                st.error("❌ Incorrect password.")
else:
    st.info("ℹ️ Upload or add data below to get started.")

# Manual Draw Entry
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
