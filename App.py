import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from streamlit_mic_recorder import streamlit_mic_recorder

st.set_page_config(page_title="Zenith AI", page_icon="🧠")
st.title("🧠 Zenith AI")

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- INPUT SECTION ---
st.subheader("What's the plan?")
voice_data = streamlit_mic_recorder(start_prompt="Record 🎤", stop_prompt="Stop 🛑", key='STT')

st.divider()
user_text = st.text_input("Type here:")
plan_it = st.button("Plan It")

# --- LOGIC ---
final_msg = None
if voice_data and voice_data.get('text'):
    final_msg = voice_data['text']
elif plan_it and user_text:
    final_msg = user_text

if final_msg:
    if "notify" in final_msg.lower() or "remind" in final_msg.lower():
        try:
            requests.post("https://ntfy.sh/floyd_zenith_alerts", data=final_msg.encode('utf-8'))
            st.balloons()
            st.toast("Sent to phone! 📱")
        except:
            st.error("Failed to reach phone.")

    st.session_state.tasks.append({
        "Time": datetime.now().strftime("%H:%M"), 
        "Activity": final_msg, 
        "Type": "Reminder ⏰" if "notify" in final_msg.lower() else "Task 📋"
    })
    if plan_it:
        st.rerun()

# --- TABLE ---
if st.session_state.tasks:
    st.table(pd.DataFrame(st.session_state.tasks))
    if st.button("Clear Day"):
        st.session_state.tasks = []
        st.rerun()
