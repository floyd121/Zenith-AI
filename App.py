import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_mic_recorder import streamlit_mic_recorder
import requests
import re
import threading
import time

# --- APP CONFIG ---
st.set_page_config(page_title="Zenith AI", page_icon="🧠")
st.title("🧠 Zenith AI: Your Day, Planned.")

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- 1. THE NOTIFICATION ENGINE ---
def send_ping(message):
    """Sends the actual signal to your phone via ntfy"""
    try:
        requests.post("https://ntfy.sh/floyd_zenith_alerts", 
            data=message.encode('utf-8'),
            headers={"Title": "ZENITH ALERT", "Priority": "high", "Tags": "alarm_clock"}
        )
    except:
        pass

def handle_logic(raw_text):
    if raw_text:
        # Check for Notification Trigger
        if "notify" in raw_text.lower() or "remind" in raw_text.lower():
            # Look for 24h time like 17:00
            time_match = re.search(r'(\d{1,2}):(\d{2})', raw_text)
            
            if time_match:
                target_h, target_m = map(int, time_match.groups())
                now = datetime.now()
                target_time = now.replace(hour=target_h, minute=target_m, second=0)
                if target_time < now:
                    target_time += timedelta(days=1)
                
                wait_seconds = (target_time - now).total_seconds()
                st.success(f"Clock set for {target_h}:{target_m:02d} 🕒")
                threading.Thread(target=lambda: (time.sleep(max(0, wait_seconds)), send_ping(raw_text))).start()
            else:
                send_ping(raw_text)
                st.toast("Sent to phone! 📱")
                st.balloons()

        # Add to the visual table
        st.session_state.tasks.append({
            "Time": datetime.now().strftime("%H:%M"), 
            "Activity": raw_text, 
            "Type": "Reminder ⏰" if "notify" in raw_text.lower() else "Task 📋"
        })

# --- 2. THE INPUTS ---
st.subheader("What's on your mind?")
# Voice Input
text = streamlit_mic_recorder(start_prompt="Click to Speak 🎤", stop_prompt="Stop Recording 🛑", key='STT')

# Typing Input
st.divider()
user_input = st.text_input("Type here (e.g., 'Notify me at 17:00')")
if st.button("Plan It"):
    if user_input:
        handle_logic(user_input)
        st.rerun()

if text:
    handle_logic(text)

# --- 3. THE VISUAL SCHEDULE ---
st.subheader("Today's Blueprint")
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    st.table(df)
    if st.button("Clear My Day"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("Schedule clear. Use 'notify' to ping your phone!")

st.caption("Zenith AI MVP v1.0 | Floyd's Personal Assistant")
