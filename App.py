import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# Page Setup
st.set_page_config(page_title="Zenith AI", page_icon="🧠")
st.title("🧠 Zenith AI: Back to Basics")

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# ── Voice Command Component ──────────────────────────────────────────────────
voice_html = """
<style>
  .mic-wrap { display: flex; flex-direction: column; align-items: center; gap: 10px; margin: 12px 0; }
  .mic-btn {
    width: 64px; height: 64px; border-radius: 50%;
    border: 2px solid #ccc; background: #fff;
    font-size: 26px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
  }
  .mic-btn.listening { background: #fee2e2; border-color: #ef4444; animation: pulse 1.2s infinite; }
  @keyframes pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.35); }
    50%      { box-shadow: 0 0 0 10px rgba(239,68,68,0); }
  }
  .mic-status { font-size: 13px; color: #666; }
  .mic-status.active { color: #dc2626; font-weight: 600; }
  .transcript { font-size: 13px; color: #444; font-style: italic;
    background: #f9f9f9; border: 1px solid #e5e7eb;
    border-radius: 8px; padding: 8px 12px; min-height: 36px;
    width: 100%; max-width: 420px; text-align: center; }
</style>

<div class="mic-wrap">
  <button class="mic-btn" id="micBtn" onclick="toggleMic()" title="Tap to speak">🎙️</button>
  <span class="mic-status" id="micStatus">Tap to speak</span>
  <div class="transcript" id="transcript">Your words will appear here…</div>
</div>

<script>
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition, listening = false;

if (!SpeechRecognition) {
  document.getElementById('micStatus').textContent = '⚠️ Voice not supported — use Chrome/Edge';
  document.getElementById('micBtn').disabled = true;
  document.getElementById('micBtn').style.opacity = '0.4';
} else {
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'en-ZA';

  recognition.onstart = () => {
    listening = true;
    document.getElementById('micBtn').classList.add('listening');
    document.getElementById('micBtn').textContent = '⏹️';
    document.getElementById('micStatus').textContent = 'Listening… speak now';
    document.getElementById('micStatus').classList.add('active');
    document.getElementById('transcript').textContent = '…';
  };

  recognition.onresult = (e) => {
    let interim = '', final = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      e.results[i].isFinal ? final += t : interim += t;
    }
    document.getElementById('transcript').textContent = final || interim;
    if (final) {
      // Push final transcript to Streamlit via query param trick
      const url = new URL(window.parent.location.href);
      url.searchParams.set('voice_cmd', final);
      window.parent.history.replaceState({}, '', url);
    }
  };

  recognition.onerror = (e) => {
    document.getElementById('micStatus').textContent = 'Error: ' + e.error;
    stopListening();
  };

  recognition.onend = stopListening;

  function stopListening() {
    listening = false;
    document.getElementById('micBtn').classList.remove('listening');
    document.getElementById('micBtn').textContent = '🎙️';
    document.getElementById('micStatus').textContent = 'Tap to speak';
    document.getElementById('micStatus').classList.remove('active');
  }
}

function toggleMic() {
  if (!recognition) return;
  listening ? recognition.stop() : recognition.start();
}
</script>
"""

st.subheader("🎙️ Voice Command")
st.info("Tap the mic, say your command, and it will fill the text box below.")
st.components.v1.html(voice_html, height=180)

# ── Text Input Section ───────────────────────────────────────────────────────
st.subheader("⌨️ Plan your day:")
user_text = st.text_input(
    "Type your command (e.g., 'notify check scones') — or use the mic above",
    placeholder="notify check scones…"
)
plan_btn = st.button("Plan It")

if plan_btn and user_text:
    # 1. Send notification if keyword found
    if "notify" in user_text.lower() or "remind" in user_text.lower():
        try:
            requests.post(
                "https://ntfy.sh/floyd_zenith_alerts",
                data=user_text.encode("utf-8")
            )
            st.balloons()
            st.toast("Ping sent to phone! 📱")
        except Exception:
            st.error("Notification failed.")

    # 2. Add to task table
    st.session_state.tasks.append({
        "Time": datetime.now().strftime("%H:%M"),
        "Activity": user_text,
        "Type": "Reminder ⏰" if "notify" in user_text.lower() else "Task 📋"
    })
    st.rerun()

# ── Task Table ───────────────────────────────────────────────────────────────
st.subheader("📋 Today's Blueprint")
if st.session_state.tasks:
    st.table(pd.DataFrame(st.session_state.tasks))
    if st.button("Clear Day"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("Ready for your first command!")

# ── Footer note ──────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🎙️ Voice input works in **Chrome** and **Edge**. "
    "After speaking, copy the transcript and paste it into the text box, then hit **Plan It**."
)
