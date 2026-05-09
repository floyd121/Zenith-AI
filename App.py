import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_mic_recorder import streamlit_mic_recorder
import requests

st.set_page_config(page_title="Zenith AI", page_icon="🧠")
st.title("🧠 Zenith AI")

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- INPUT SECTION ---
st.subheader("What's the plan?")
text = streamlit_mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop 🛑", key='STT')

st.divider()
user_input = st.text_input("Or type here:")
plan_it = st.button("Plan It")

# --- LOGIC SECTION ---
active_cmd = text if text else (user_input if plan_it else None)

if active_cmd:
    # Send notification if magic words are used
    if "notify" in active_cmd.lower() or "remind" in active_cmd.lower():
        try:
            requests.post("https://ntfy.sh/floyd_zenith_alerts", data=active_cmd.encode('utf-8'))
            st.balloons()
            st.toast("Ping sent to phone! 📱")
        except:
            pass
    
    # Add to table
    st.session_state.tasks.append({
        "Time": datetime.now().strftime("%H:%M"), 
        "Activity": active_cmd, 
        "Type": "Reminder ⏰" if "notify" in active_cmd.lower() else "Task 📋"
    })
    if plan_it:
        st.rerun()

# --- TABLE SECTION ---
if st.session_state.tasks:
    st.table(pd.DataFrame(st.session_state.tasks))
    if st.button("Clear Day"):
        st.session_state.tasks = []
        st.rerun()
