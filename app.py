import os
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import itertools

st.set_page_config(page_title="Eurojackpot Mastermind", layout="centered")

@st.cache_data
def fetch_latest_draws():
    url = "https://www.euro-jackpot.net/results"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    draw_data = []
    results = soup.select('div.result')

    for result in results[:10]:
        try:
            date_elem = result.select_one('.date')
            balls = result.select('.balls .ball')
            euros = result.select('.balls .euro')

            if not date_elem or len(balls) < 5 or len(euros) < 2:
                continue

            date_text = date_elem.text.strip()
            main_numbers = [int(b.text.strip()) for b in balls[:5]]
            euro_numbers = [int(e.text.strip()) for e in euros[:2]]

            draw_data.append({
                'Draw_Date': date_text,
                'Main_Numbers': sorted(main_numbers),
                'Euro_Numbers': sorted(euro_numbers)
            })
        except Exception as e:
            print("Skipping row:", e)
            continue

    return pd.DataFrame(draw_data)

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

# Load data
st.title("🎯 Eurojackpot Mastermind")
df_draws = fetch_latest_draws()
st.subheader("🗓️ Latest Draws")
st.dataframe(df_draws)

# Buttons + session state init
if 'main_freq' not in st.session_state:
    st.session_state.main_freq = None
    st.session_state.euro_freq = None
    st.session_state.pick_main = None
    st.session_state.pick_euro = None

if st.button("Run Frequency Analysis", key="run_analysis"):
    main_freq, euro_freq = analyze_frequency(df_draws)
    st.session_state.main_freq = main_freq
    st.session_state.euro_freq = euro_freq

if st.session_state.main_freq is not None:
    st.subheader("🔥 Main Number Frequency")
    st.dataframe(st.session_state.main_freq)
    st.subheader("🔵 Euro Number Frequency")
    st.dataframe(st.session_state.euro_freq)

if st.button("🎯 Generate Smart Solo Pick", key="solo_pick"):
    if st.session_state.main_freq is None:
        st.warning("Run frequency analysis first!")
    else:
        main, euro = generate_solo_win_pick(st.session_state.main_freq, st.session_state.euro_freq)
        st.session_state.pick_main = main
        st.session_state.pick_euro = euro

if st.session_state.pick_main is not None:
    st.success(f"🎯 Your Mastermind Pick: {st.session_state.pick_main} + {st.session_state.pick_euro}")
