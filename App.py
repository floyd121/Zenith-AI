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
import threading
import time
from datetime import datetime, timedelta

# --- THE SMART NOTIFICATION ENGINE ---
def delayed_notification(delay_seconds, message):
    """Waits for the timer to finish, then pings your phone"""
    time.sleep(delay_seconds)
    try:
        requests.post("https://ntfy.sh/floyd_zenith_alerts", 
            data=message.encode('utf-8'),
            headers={
                "Title": "Zenith AI Scheduled Reminder",
                "Priority": "high",
                "Tags": "alarm_clock,loudspeaker"
            }
        )
    except:
        pass

def handle_notification(user_text):
    """Calculates if the message should be sent now or later"""
    if "remind" in user_text.lower() or "notify" in user_text.lower():
        # Check for time (e.g., 'at 17:00' or 'at 5pm')
        # Default to immediate if no time found
        delay = 0
        
        # Simple logic: if you say 'at 5pm', we calculate the seconds until then
        # For now, let's trigger the immediate toast and balloons
        st.toast("Zenith is watching the clock for you! 🕒")
        st.balloons()
        
        # Start the background timer
        threading.Thread(target=delayed_notification, args=(0, user_text)).start()

if text:
    st.info(f"Command received: {text}")
    handle_notification(text)
    
    if "plan" in text.lower() or "add" in text.lower():
        task_type = "Reminder ⏰" if "at" in text.lower() else "Task 📋"
        st.session_state.tasks.append({"Time": datetime.now().strftime("%H:%M"), "Activity": text, "Type": task_type})

# --- MANUAL INPUT SECTION ---
st.divider()
user_input = st.text_input("Type your command (e.g., 'Notify me to check scones'):")
if st.button("Plan It"):
    if user_input:
        handle_notification(user_input)
        task_type = "Reminder ⏰" if "at" in user_input.lower() else "Task 📋"
        st.session_state.tasks.append({"Time": datetime.now().strftime("%H:%M"), "Activity": user_input, "Type": task_type})
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
    st.info("Your schedule is clear. Tell Zenith what to do!")
