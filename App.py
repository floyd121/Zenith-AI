import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from streamlit_mic_recorder import streamlit_mic_recorder

# 1. Page Setup
st.set_page_config(page_title="Zenith AI", page_icon="🧠")
st.title("🧠 Zenith AI")

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# 2. Input Section
st.subheader("What's the plan?")
voice_data = streamlit_mic_recorder(start_prompt="Record 🎤", stop_prompt="Stop 🛑", key='STT')

st.divider()
user_text = st.text_input("Or type your command here:")
plan_it = st.button("Plan It")

# 3. The Logic
final_msg = None
# Check voice first
if voice_data and voice_data.get('text'):
    final_msg = voice_data['text']
# Then check the text box
elif plan_it and user_text:
    final_msg = user_text

if final_msg:
    # If you say 'notify', send it to the phone immediately
    if "notify" in final_msg.lower() or "remind" in final_msg.lower():
        try:
            requests.post("https://ntfy.sh/floyd_zenith_alerts", data=final_msg.encode('utf-8'))
            st.balloons()
            st.toast("Sent to phone! 📱")
        except:
            st.error("Failed to reach your phone. Check internet!")

    # Add to your Blueprint table
    st.session_state.tasks.append({
        "Time": datetime.now().strftime("%H:%M"), 
        "Activity": final_msg, 
        "Type": "Reminder ⏰" if "notify" in final_msg.lower() else "Task 📋"
    })
    if plan_it:
        st.rerun()

# 4. Display the Table
if st.session_state.tasks:
    st.table(pd.DataFrame(st.session_state.tasks))
    if st.button("Clear Day"):
        st.session_state.tasks = []
        st.rerun()
    
