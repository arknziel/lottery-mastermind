import streamlit as st
import pandas as pd
import random
import itertools
from collections import Counter
import os

st.set_page_config(page_title="🎯 Lottery Mastermind", layout="centered")

# --- File paths ---
EURO_FILE = "eurojackpot_master_data.csv"
SUPER_FREQ_FILE = "superenalotto_number_frequencies.csv"

# --- Lottery Selector ---
lottery = st.radio("🎯 Select Lottery:", ["Eurojackpot", "SuperEnalotto"])

# --- Shared Functions ---
def analyze_frequency_from_draws(df):
    all_numbers = list(itertools.chain.from_iterable(df['Numbers']))
    return pd.DataFrame(Counter(all_numbers).items(), columns=['Number', 'Frequency']).sort_values(by='Frequency', ascending=False)

def analyze_frequency_from_table(df):
    return df.sort_values(by='Frequency', ascending=False)

def get_heat_groups(freq_df):
    total = len(freq_df)
    hot = freq_df.head(int(total * 0.15))['Number'].tolist()
    warm = freq_df.iloc[int(total * 0.15):int(total * 0.5)]['Number'].tolist()
    cold = freq_df.tail(int(total * 0.3))['Number'].tolist()
    return hot, warm, cold

if lottery == "Eurojackpot":
    st.title("🎯 Eurojackpot Mastermind")

    # Upload
    st.subheader("📤 Upload Eurojackpot CSV")
    ej_file = st.file_uploader("Choose Eurojackpot CSV", type="csv", key="ej_upload")
    if ej_file:
        uploaded_df = pd.read_csv(ej_file)
        uploaded_df.to_csv(EURO_FILE, index=False)
        st.success("✅ Uploaded and saved!")

    # Load
    def load_euro_data():
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

    df = load_euro_data()

    if df is not None:
        if st.button("📊 Analyze Frequency"):
            freq = analyze_frequency_from_draws(df)
            st.session_state["ej_freq"] = freq

        if "ej_freq" in st.session_state:
            hot, warm, cold = get_heat_groups(st.session_state["ej_freq"])

            st.subheader("🔥 Heat Groups")
            st.write(f"🔥 Hot: {hot}")
            st.write(f"🟡 Warm: {warm}")
            st.write(f"❄️ Cold: {cold}")

            strategy = st.radio("🎛️ Pick Strategy", ["🔥 Hot", "🟡 Warm", "❄️ Cold", "⚖️ Balanced"])
            if st.button("♻️ Generate Pick"):
                if strategy == "🔥 Hot":
                    pick = sorted(random.sample(hot, 5))
                    euro = sorted(random.sample(hot, 2))
                elif strategy == "🟡 Warm":
                    pick = sorted(random.sample(warm, 5))
                    euro = sorted(random.sample(warm, 2))
                elif strategy == "❄️ Cold":
                    pick = sorted(random.sample(cold, 5))
                    euro = sorted(random.sample(cold, 2))
                else:
                    pick = sorted(random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 1))
                    euro = sorted(random.sample(warm, 1) + random.sample(cold, 1))
                st.success(f"🎯 Main: {pick} + Euro: {euro}")

            # 🔐 Arknziel Solo Pick
            with st.expander("🔐 Generate arknziel pick"):
                pw = st.text_input("Enter password", type="password")
                if pw == "arknziel":
                    pick = sorted(random.sample(hot + warm, 5))
                    euro = sorted(random.sample(hot, 2))
                    st.success(f"arknziel 🎯 {pick} + {euro}")
                elif pw:
                    st.error("❌ Wrong password")

    # Manual Entry
    st.subheader("➕ Add Eurojackpot Draw")
    with st.form("ej_manual"):
        draw_date = st.date_input("Draw Date")
        cols = st.columns(5)
        main = [col.number_input(f"Main {i+1}", 1, 50, key=f"ej_main{i}") for i, col in enumerate(cols)]
        euro = [col.number_input(f"Euro {i+1}", 1, 12, key=f"ej_euro{i}") for i in range(2)]
        if st.form_submit_button("Add"):
            new = pd.DataFrame([{"Draw_Date": draw_date, "Numbers": str(sorted(main + euro))}])
            if os.path.exists(EURO_FILE):
                old = pd.read_csv(EURO_FILE)
                new = pd.concat([old, new], ignore_index=True)
            new.to_csv(EURO_FILE, index=False)
            st.success("✅ Draw added.")

elif lottery == "SuperEnalotto":
    st.title("🎯 SuperEnalotto (Frequency Mode)")

    # Upload
    st.subheader("📤 Upload SuperEnalotto Frequency CSV")
    freq_file = st.file_uploader("Choose SuperEnalotto frequency CSV", type="csv", key="se_upload")
    if freq_file:
        df_freq = pd.read_csv(freq_file)
        df_freq.to_csv(SUPER_FREQ_FILE, index=False)
        st.success("✅ Frequency file saved!")

    # Load
    if os.path.exists(SUPER_FREQ_FILE):
        df = pd.read_csv(SUPER_FREQ_FILE)
        st.session_state["se_freq"] = df.sort_values(by="Frequency", ascending=False)

    if "se_freq" in st.session_state:
        freq = st.session_state["se_freq"]
        hot, warm, cold = get_heat_groups(freq)

        st.subheader("🔥 Heat Analyzer")
        st.write(f"🔥 Hot: {hot}")
        st.write(f"🟡 Warm: {warm}")
        st.write(f"❄️ Cold: {cold}")

        strategy = st.radio("🎛️ Pick Strategy", ["🔥 Hot", "🟡 Warm", "❄️ Cold", "⚖️ Balanced"])
        if st.button("♻️ Generate SuperEnalotto Pick"):
            if strategy == "🔥 Hot":
                pick = sorted(random.sample(hot, 6))
            elif strategy == "🟡 Warm":
                pick = sorted(random.sample(warm, 6))
            elif strategy == "❄️ Cold":
                pick = sorted(random.sample(cold, 6))
            else:
                pick = sorted(random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 2))
            st.success(f"🎯 SuperEnalotto Pick: {pick}")

        # 🔐 Arknziel Solo Pick for SuperEnalotto
        with st.expander("🔐 Generate arknziel pick"):
            pw = st.text_input("Enter password for SuperEnalotto", type="password")
            if pw == "arknziel":
                pick = sorted(random.sample(hot + warm, 6))
                st.success(f"arknziel 🎯 {pick}")
            elif pw:
                st.error("❌ Wrong password")
    else:
        st.info("ℹ️ Please upload SuperEnalotto frequency CSV.")
