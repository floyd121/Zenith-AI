import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_mic_recorder import mic_recorder, speech_to_text

# --- APP CONFIG ---
st.set_page_config(page_title="Zenith AI Planner", page_icon="🤖")
st.title("🤖 Zenith AI: Your Day, Planned.")

# --- SESSION STATE (The App's Memory) ---
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- INPUT SECTION ---
st.subheader("What's on your mind?")
st.write("Say a command (e.g., 'Plan for Monday')")

# This button records AND transcribes
text = speech_to_text(
    language='en',
    start_prompt="Click to Speak 🎤",
    stop_prompt="Stop Recording 🛑",
    key='STT'
)
# THE SIMPLEST NOTIFICATION CODE
if text or user_input:
    cmd = text if text else user_input
    if "notify" in cmd.lower() or "remind" in cmd.lower():
        # This part talks to your phone
        try:
            requests.post("https://ntfy.sh/floyd_zenith_alerts", 
                data=cmd.encode('utf-8'),
                headers={"Title": "ZENITH ALERT", "Priority": "high"}
            )
            st.success("Signal sent to phone! 📱")
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")

    # This part adds it to your laptop table
    st.session_state.tasks.append({
        "Time": datetime.now().strftime("%H:%M"), 
        "Activity": cmd, 
        "Type": "Reminder ⏰"
    })
