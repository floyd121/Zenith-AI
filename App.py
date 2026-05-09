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
   # --- THE INPUT SECTION ---
# 1. Voice Input
text = streamlit_mic_recorder(start_prompt="Click to Speak 🎤", stop_prompt="Stop Recording 🛑", key='STT')

# 2. Typing Input
st.divider()
user_input = st.text_input("Example: 'Notify me to check scones at 17:00'")
plan_button = st.button("Plan It")

# --- THE NOTIFICATION ENGINE ---
def send_ping(message):
    try:
        requests.post("https://ntfy.sh/floyd_zenith_alerts", 
            data=message.encode('utf-8'),
            headers={"Title": "ZENITH ALERT", "Priority": "high"}
        )
        st.toast("Signal sent to phone! 📱")
        st.balloons()
    except:
        st.error("Connection failed. Check your internet!")

# --- THE LOGIC (What happens when you speak or type) ---
active_text = text if text else (user_input if plan_button else None)

if active_text:
    # Trigger Notification
    if "notify" in active_text.lower() or "remind" in active_text.lower():
        send_ping(active_text)
    
    # Add to Table
    task_type = "Reminder ⏰" if "at" in active_text.lower() or ":" in active_text.lower() else "Task 📋"
    st.session_state.tasks.append({
        "Time": datetime.now().strftime("%H:%M"), 
        "Activity": active_text, 
        "Type": task_type
    })
    if plan_button:
        st.rerun()

# --- THE VISUAL SCHEDULE ---
st.subheader("Today's Blueprint")
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    st.table(df)
    if st.button("Clear My Day"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("Schedule clear. Use 'notify' to ping your phone!")

st.caption("Zenith AI MVP v1.0 | Connected to Mobile via ntfy"
