import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from streamlit_mic_recorder import streamlit_mic_recorder

# Set up page
st.set_page_config(page_title="Zenith AI", page_icon="🧠")
st.title("🧠 Zenith AI")

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- INPUTS ---
st.subheader("What is the plan?")
# Capture voice input
voice_val = streamlit_mic_recorder(start_prompt="Record 🎤", stop_prompt="Stop 🛑", key='STT')

st.divider()
user_text = st.text_input("Or type here:")
btn = st.button("Plan It")

# --- LOGIC ---
# Determine which input to use
final_msg = None
if voice_val:
    final_msg = voice_val['text']
elif btn and user_text:
    final_msg = user_text

if final_msg:
    # Handle Notification
    if "notify" in final_msg.lower() or "remind" in final_msg.lower():
        try:
            requests.post("https://ntfy.sh/floyd_zenith_alerts", data=final_msg.encode('utf-8'))
            st.balloons()
            st.toast("Ping sent to phone! 📱")
        except:
            st.error("Notification failed to send.")

    # Add to Blueprint
    st.session_state.tasks.append({
        "Time": datetime.now().strftime("%H:%M"), 
        "Activity": final_msg, 
        "Type": "Reminder ⏰" if "notify" in final_msg.lower() else "Task 📋"
    })
    
    # Rerun to show update if button was clicked
    if btn:
        st.rerun()

# --- DISPLAY ---
if st.session_state.tasks:
    st.table(pd.DataFrame(st.session_state.tasks))
    if st.button("Clear Day"):
        st.session_state.tasks = []
        st.rerun()
