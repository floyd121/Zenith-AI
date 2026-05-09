import streamlit as st
import pandas as pd
from datetime import datetime
from strenlit_mic_recorder importmic_recorder

# --- APP CONFIG ---
st.set_page_config(page_title="Zenith AI Planner", page_icon="🤖")
st.title("🤖 Zenith AI: Your Day, Planned.")

# --- SESSION STATE (The App's Memory) ---
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- INPUT SECTION ---
st.subheader("What's on your mind?")
user_input = st.text_input("Example: 'Remind me to call Mom at 5pm' or 'I need to finish my essay today'")

if st.button("Plan It"):
    if user_input:
        # Simple AI Logic: In a full version, we connect this to Gemini's API
        task_type = "Reminder ⏰" if "at" in user_input.lower() or ":" in user_input else "Task 📝"
        st.session_state.tasks.append({"Time": datetime.now().strftime("%H:%M"), "Activity": user_input, "Type": task_type})
        st.success("Got it! I've added that to your timeline.")

# --- THE VISUAL SCHEDULE ---
st.divider()
st.subheader("Today's Blueprint")

if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    st.table(df) # This creates a clean list for the user
    
    if st.button("Clear My Day"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("Your schedule is clear. Tell Zenith what you need to do!")

# --- FOOTER ---
st.caption("Zenith AI MVP v1.0 | Voice-to-Action enabled via Mobile Browser")
