import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# Page Setup
st.set_page_config(page_title="Zenith AI", page_icon="🧠")
st.title("🧠 Zenith AI: Back to Basics")

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Input Section
st.subheader("Plan your day:")
user_text = st.text_input("Type your command (e.g., 'notify check scones')")
plan_btn = st.button("Plan It")

if plan_btn and user_text:
    # 1. Send to Phone
    if "notify" in user_text.lower() or "remind" in user_text.lower():
        try:
            # Pinging your ntfy topic
            requests.post("https://ntfy.sh/floyd_zenith_alerts", 
                          data=user_text.encode('utf-8'))
            st.balloons()
            st.toast("Ping sent to phone! 📱")
        except:
            st.error("Notification failed.")

    # 2. Add to Table
    st.session_state.tasks.append({
        "Time": datetime.now().strftime("%H:%M"), 
        "Activity": user_text, 
        "Type": "Reminder ⏰" if "notify" in user_text.lower() else "Task 📋"
    })
    st.rerun()

# Display Table
st.subheader("Today's Blueprint")
if st.session_state.tasks:
    st.table(pd.DataFrame(st.session_state.tasks))
    if st.button("Clear Day"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("Ready for your first command!")
