import os
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter
import itertools

st.set_page_config(page_title="Eurojackpot Mastermind", layout="centered")

@st.cache_data
def fetch_latest_draws():
    url = "https://www.euro-jackpot.net/results"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    draw_data = []
    results = soup.select('div.results li')

    for result in results[:10]:  # last 10 draws
        date_text = result.select_one('.date').text.strip()
        numbers = [int(n.text.strip()) for n in result.select('.balls .ball')]
        euro_numbers = [int(n.text.strip()) for n in result.select('.euro')]

        draw_data.append({
            'Draw_Date': date_text,
            'Main_Numbers': sorted(numbers[:5]),
            'Euro_Numbers': sorted(euro_numbers[:2])
        })
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
    selected_main = sorted(rare_main[:5])
    selected_euro = sorted(rare_euro[:2])
    return selected_main, selected_euro

# App Layout
st.title("🎯 Eurojackpot Mastermind")
df_draws = fetch_latest_draws()
st.subheader("🗓️ Latest Draws")
st.dataframe(df_draws)

if st.button("Run Frequency Analysis"):
    main_freq, euro_freq = analyze_frequency(df_draws)
    st.subheader("🔥 Main Number Frequency")
    st.dataframe(main_freq)
    st.subheader("🔵 Euro Number Frequency")
    st.dataframe(euro_freq)

if st.button("🎯 Generate Smart Solo Pick"):
    main_freq, euro_freq = analyze_frequency(df_draws)
    pick_main, pick_euro = generate_solo_win_pick(main_freq, euro_freq)
    st.success(f"Your Mastermind Pick: {pick_main} + {pick_euro}")
