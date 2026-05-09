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
if text:
    st.info(f"Command received: {text}")
    
    # 1. Trigger Notification/Balloons
    if "remind" in text.lower() or "notify" in text.lower():
        st.toast(f"New Reminder: {text}", icon='🔔')
        st.success("Notification active!")
        st.balloons()
    
    # 2. Automatically add to the "Blueprint" Table
    if "plan" in text.lower() or "add" in text.lower():
        task_type = "Reminder ⏰" if "at" in text.lower() else "Task 📋"
        st.session_state.tasks.append({
            "Time": datetime.now().strftime("%H:%M"), 
            "Activity": text, 
            "Type": task_type
        })
        st.success("Added to your Blueprint!")

# --- MANUAL INPUT SECTION ---
st.write("---")
user_input = st.text_input("Or type your plan here:")
if st.button("Plan It"):
    if user_input:
        task_type = "Reminder ⏰" if "at" in user_input.lower() else "Task 📋"
        st.session_state.tasks.append({
            "Time": datetime.now().strftime("%H:%M"), 
            "Activity": user_input, 
            "Type": task_type
        })
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
    st.info("Your schedule is clear. Tell Zenith what you need to do!")

st.caption("Zenith AI MVP v1.0 | Voice-to-Action enabled")
