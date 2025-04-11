import streamlit as st
import pandas as pd
import itertools
from collections import Counter
import os

st.set_page_config(page_title="Eurojackpot Mastermind (Merge Mode)", layout="centered")

MASTER_FILE = "eurojackpot_master_data.csv"

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

def load_master_data():
    if os.path.exists(MASTER_FILE):
        df = pd.read_csv(MASTER_FILE)
        df['Main_Numbers'] = df['Main_Numbers'].apply(eval)
        df['Euro_Numbers'] = df['Euro_Numbers'].apply(eval)
        return df
    return pd.DataFrame(columns=['Draw_Date', 'Main_Numbers', 'Euro_Numbers'])

def merge_new_draws(master_df, new_df):
    new_df['Main_Numbers'] = new_df['Main_Numbers'].apply(eval)
    new_df['Euro_Numbers'] = new_df['Euro_Numbers'].apply(eval)
    combined_df = pd.concat([master_df, new_df], ignore_index=True)
    combined_df.drop_duplicates(subset=['Draw_Date', 'Main_Numbers', 'Euro_Numbers'], inplace=True)
    combined_df = combined_df.sort_values(by='Draw_Date').reset_index(drop=True)
    return combined_df

st.title("📊 Eurojackpot Mastermind (Merge Mode)")
master_df = load_master_data()

uploaded_file = st.file_uploader("Upload NEW draws CSV (same format as before)", type=["csv"])

if uploaded_file:
    try:
        new_df = pd.read_csv(uploaded_file)
        if 'Draw_Date' in new_df.columns and 'Main_Numbers' in new_df.columns and 'Euro_Numbers' in new_df.columns:
            master_df = merge_new_draws(master_df, new_df)
            st.success("✅ New data merged successfully!")
            st.dataframe(master_df)

            # Save updated master file
            master_df.to_csv(MASTER_FILE, index=False)

            if st.button("Run Frequency Analysis"):
                main_freq, euro_freq = analyze_frequency(master_df)
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
            st.error("❌ CSV must include 'Draw_Date', 'Main_Numbers', and 'Euro_Numbers' columns.")
    except Exception as e:
        st.error(f"⚠️ Something went wrong: {e}")
else:
    st.info("⬆️ Upload your new draw data to update the system.")
    st.dataframe(master_df)
    if st.button("Run Frequency Analysis"):
        main_freq, euro_freq = analyze_frequency(master_df)
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
