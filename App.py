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
import re

# --- THE SMART NOTIFICATION ENGINE ---
def send_ping(message):
    """Sends the actual signal to your phone"""
    try:
        requests.post("https://ntfy.sh/floyd_zenith_alerts", 
            data=message.encode('utf-8'),
            headers={"Title": "Zenith AI: Time to Act!", "Priority": "high", "Tags": "alarm_clock,loudspeaker"}
        )
    except: pass

def schedule_notification(user_text):
    """Calculates if it should send now or wait for a specific time"""
    user_text = user_text.lower()
    if "notify" in user_text or "remind" in user_text:
        # Check for 24h time like '17:00'
        time_match = re.search(r'(\d{1,2}):(\d{2})', user_text)
        
        if time_match:
            target_h, target_m = map(int, time_match.groups())
            now = datetime.now()
            target_time = now.replace(hour=target_h, minute=target_m, second=0)
            
            # If time already passed today, assume it's for tomorrow
            if target_time < now:
                target_time += timedelta(days=1)
            
            wait_seconds = (target_time - now).total_seconds()
            
            st.success(f"Clock set! I'll ping your phone at {target_h}:{target_m:02d}")
            threading.Thread(target=lambda: (time.sleep(wait_seconds), send_ping(user_text))).start()
        else:
            # No time found? Send it immediately
            send_ping(user_text)
            st.toast("Sent to phone! 📱")
            st.balloons()

if text:
    st.info(f"Command received: {text}")
    schedule_notification(text)
    task_type = "Reminder ⏰" if "at" in text.lower() or ":" in text.lower() else "Task 📋"
    st.session_state.tasks.append({"Time": datetime.now().strftime("%H:%M"), "Activity": text, "Type": task_type})

# --- MANUAL INPUT SECTION ---
st.divider()
user_input = st.text_input("Example: 'Notify me to check scones at 17:00'")
if st.button("Plan It"):
    if user_input:
        schedule_notification(user_input)
        task_type = "Reminder ⏰" if "at" in user_input.lower() or ":" in user_input.lower() else "Task 📋"
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
    st.info("Schedule clear. Use 'notify' + a time (e.g. 17:00) to ping your phone!")
