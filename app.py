# --- EUROJACKPOT SECTION ---
if lottery == "Eurojackpot":
    st.title("🎯 Eurojackpot Mastermind")

    df = load_eurojackpot_data()

    if st.button("📊 Run Frequency Analysis"):
        main_freq, euro_freq = analyze_frequency(df)
        st.session_state["main_freq"] = main_freq
        st.session_state["euro_freq"] = euro_freq

    if "main_freq" in st.session_state:
        hot_main, warm_main, cold_main = get_heat_groups(st.session_state["main_freq"])
        hot_euro, warm_euro, cold_euro = get_heat_groups(st.session_state["euro_freq"])

        st.subheader("🔥 Heat Analyzer")
        st.write(f"Main 🔥: {hot_main}")
        st.write(f"Main 🟡: {warm_main}")
        st.write(f"Main ❄️: {cold_main}")
        st.write(f"Euro 🔥: {hot_euro}")
        st.write(f"Euro 🟡: {warm_euro}")
        st.write(f"Euro ❄️: {cold_euro}")

        heat_strategy = st.radio("🎛️ Heat Strategy Generator", ["🔥 Hot Only", "🟡 Warm Only", "❄️ Cold Only", "⚖️ Balanced"])
        if st.button("♻️ Generate Eurojackpot Pick"):
            if heat_strategy == "🔥 Hot Only":
                main = sorted(random.sample(hot_main, 5))
                euro = sorted(random.sample(hot_euro, 2))
            elif heat_strategy == "🟡 Warm Only":
                main = sorted(random.sample(warm_main, 5))
                euro = sorted(random.sample(warm_euro, 2))
            elif heat_strategy == "❄️ Cold Only":
                main = sorted(random.sample(cold_main, 5))
                euro = sorted(random.sample(cold_euro, 2))
            else:
                main = sorted(random.sample(hot_main, 2) + random.sample(warm_main, 2) + random.sample(cold_main, 1))
                euro = sorted(random.sample(hot_euro, 1) + random.sample(warm_euro, 1))
            st.success(f"🎯 Your Pick: {main} + {euro}")

# --- SUPERENALOTTO SECTION ---
elif lottery == "SuperEnalotto":
    st.title("🎯 SuperEnalotto Smart Picks")

    if os.path.exists(SUPER_FREQ_FILE):
        df = pd.read_csv(SUPER_FREQ_FILE)
        st.subheader("📊 Number Frequencies")
        st.dataframe(df)

        # Heat Groups
        hot, warm, cold = get_heat_groups(df)

        st.subheader("🔥 Heat Analyzer")
        st.write(f"🔥 Hot Numbers: {hot}")
        st.write(f"🟡 Warm Numbers: {warm}")
        st.write(f"❄️ Cold Numbers: {cold}")

        strategy = st.radio("🎛️ SuperEnalotto Strategy", ["🔥 Hot Only", "🟡 Warm Only", "❄️ Cold Only", "⚖️ Balanced"])
        if st.button("♻️ Generate SuperEnalotto Pick"):
            if strategy == "🔥 Hot Only":
                pick = sorted(random.sample(hot, 6))
            elif strategy == "🟡 Warm Only":
                pick = sorted(random.sample(warm, 6))
            elif strategy == "❄️ Cold Only":
                pick = sorted(random.sample(cold, 6))
            else:
                pick = sorted(random.sample(hot, 2) + random.sample(warm, 2) + random.sample(cold, 2))
            st.success(f"🎯 Your Pick: {pick}")
    else:
        st.warning("⚠️ No SuperEnalotto frequency file found.")
