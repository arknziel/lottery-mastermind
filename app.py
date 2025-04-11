import streamlit as st
import pandas as pd
import itertools
from collections import Counter

st.set_page_config(page_title="Eurojackpot Mastermind", layout="centered")

def analyze_frequency(df):
    all_main = list(itertools.chain.from_iterable(df['Main_Numbers']))
    all_euro = list(itertools.chain.from_iterable(df['Euro_Numbers']))
    main_freq = pd.DataFrame(Counter(all_main).items(), columns=['Number', 'Frequency']).sort_values(by='Frequency', ascending=False)
    euro_freq = pd.DataFrame(Counter(all_euro).items(), columns=['Number', 'Frequency']).sort_values(by='Frequency', ascending=False)
    return main_freq, euro_freq

def generate_solo_win_pick(main_freq, euro_freq):
    rare_main = main_freq.sort_values(by='Frequency').head(20)['Number'].tolist()
    rare_euro = euro_freq.sort_values(by='Frequency').head(6)['Number'].tolist()
    return sorted(rare_main[:5]), sorted(rare_euro[:2])

# -- UI --
st.title("📊 Eurojackpot Mastermind (CSV Mode)")
uploaded_file = st.file_uploader("Upload your Eurojackpot CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        if 'Main_Numbers' in df.columns and 'Euro_Numbers' in df.columns:
            # Convert stringified lists to real lists (if needed)
            if isinstance(df['Main_Numbers'].iloc[0], str):
                df['Main_Numbers'] = df['Main_Numbers'].apply(eval)
                df['Euro_Numbers'] = df['Euro_Numbers'].apply(eval)

            st.success("✅ Data loaded successfully!")
            st.dataframe(df)

            if st.button("Run Frequency Analysis"):
                main_freq, euro_freq = analyze_frequency(df)
                st.session_state.main_freq = main_freq
                st.session_state.euro_freq = euro_freq

            if 'main_freq' in st.session_state:
                st.subheader("🔥 Main Number Frequency")
                st.dataframe(st.session_state.main_freq)
                st.subheader("🔵 Euro Number Frequency")
                st.dataframe(st.session_state.euro_freq)

                if st.button("🎯 Generate Smart Solo Pick"):
                    main, euro = generate_solo_win_pick(st.session_state.main_freq, st.session_state.euro_freq)
                    st.success(f"🎯 Your Mastermind Pick: {main} + {euro}")

        else:
            st.error("❌ CSV must include 'Main_Numbers' and 'Euro_Numbers' columns.")
    except Exception as e:
        st.error(f"⚠️ Something went wrong: {e}")
