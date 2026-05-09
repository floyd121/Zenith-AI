import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import re
import threading
import time

# ── Page Setup ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Zenith AI", page_icon="🧠")
st.title("🧠 Zenith AI: Back to Basics")

NTFY_TOPIC = "floyd_zenith_alerts"

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "scheduled" not in st.session_state:
    st.session_state.scheduled = []

# ── Time Parser ───────────────────────────────────────────────────────────────
def parse_reminder_time(text: str):
    """
    Extract a target datetime from natural language.
    Supports: 9pm / 9:30pm / 21:00 / 9 am / at 9 etc.
    Returns a datetime object (today) or None.
    """
    pattern = r'\bat\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b'
    match = re.search(pattern, text.lower())
    if not match:
        return None

    hour   = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    ampm   = match.group(3)

    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None

    return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)


def send_ntfy(message: str, title: str = "⏰ Zenith Reminder", priority: str = "high"):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={"Title": title, "Priority": priority},
            timeout=10,
        )
    except Exception as e:
        print(f"ntfy error: {e}")


def schedule_reminder(target: datetime, message: str):
    """Fire ntfy notification at target time in a background daemon thread."""
    def _wait_and_send():
        delay = (target - datetime.now()).total_seconds()
        if delay > 0:
            time.sleep(delay)
        send_ntfy(message)

    threading.Thread(target=_wait_and_send, daemon=True).start()


# ── Voice Component ───────────────────────────────────────────────────────────
voice_html = """
<style>
  .mic-wrap { display:flex; flex-direction:column; align-items:center; gap:10px; margin:12px 0; }
  .mic-btn {
    width:64px; height:64px; border-radius:50%;
    border:2px solid #ccc; background:#fff;
    font-size:26px; cursor:pointer;
    display:flex; align-items:center; justify-content:center;
    transition:all 0.2s;
  }
  .mic-btn.listening { background:#fee2e2; border-color:#ef4444; animation:pulse 1.2s infinite; }
  @keyframes pulse {
    0%,100% { box-shadow:0 0 0 0 rgba(239,68,68,.35); }
    50%      { box-shadow:0 0 0 10px rgba(239,68,68,0); }
  }
  .mic-status { font-size:13px; color:#666; }
  .mic-status.active { color:#dc2626; font-weight:600; }
  .transcript {
    font-size:13px; color:#444; font-style:italic;
    background:#f9f9f9; border:1px solid #e5e7eb;
    border-radius:8px; padding:8px 12px; min-height:36px;
    width:100%; max-width:420px; text-align:center;
  }
</style>
<div class="mic-wrap">
  <button class="mic-btn" id="micBtn" onclick="toggleMic()" title="Tap to speak">🎙️</button>
  <span class="mic-status" id="micStatus">Tap to speak</span>
  <div class="transcript" id="transcript">Your words will appear here…</div>
</div>
<script>
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition, listening = false;
if (!SR) {
  document.getElementById('micStatus').textContent = '⚠️ Voice not supported — use Chrome/Edge';
  document.getElementById('micBtn').disabled = true;
  document.getElementById('micBtn').style.opacity = '0.4';
} else {
  recognition = new SR();
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

# ── UI ────────────────────────────────────────────────────────────────────────
st.subheader("🎙️ Voice Command")
st.info("Tap mic → speak → copy transcript → paste below → **Plan It**")
st.components.v1.html(voice_html, height=180)

st.subheader("⌨️ Plan your day:")
user_text = st.text_input(
    "Type or paste your command",
    placeholder="remind me to check my phone at 9pm"
)
plan_btn = st.button("Plan It")

if plan_btn and user_text:
    is_reminder = bool(re.search(r"\b(remind|reminder|notify|alert)\b", user_text, re.I))
    target_time = parse_reminder_time(user_text) if is_reminder else None

    if is_reminder and target_time:
        now = datetime.now()
        if target_time <= now:
            st.error(
                f"⚠️ {target_time.strftime('%I:%M %p')} has already passed today. "
                "Please set a future time."
            )
        else:
            schedule_reminder(target_time, user_text)
            time_str = target_time.strftime("%I:%M %p")
            st.success(f"⏰ Reminder scheduled for **{time_str}** — your phone will buzz then!")
            st.session_state.scheduled.append({
                "Scheduled For": time_str,
                "Message": user_text,
                "Status": "⏳ Pending"
            })
            st.session_state.tasks.append({
                "Time": now.strftime("%H:%M"),
                "Activity": user_text,
                "Type": f"⏰ Reminder @ {time_str}"
            })
            st.rerun()

    elif is_reminder and not target_time:
        # No time found → send immediately
        try:
            send_ntfy(user_text, title="📱 Zenith Alert", priority="default")
            st.balloons()
            st.toast("Ping sent to phone! 📱")
        except Exception:
            st.error("Notification failed.")
        st.session_state.tasks.append({
            "Time": datetime.now().strftime("%H:%M"),
            "Activity": user_text,
            "Type": "Reminder ⏰ (now)"
        })
        st.rerun()

    else:
        # Plain task — no notification
        st.session_state.tasks.append({
            "Time": datetime.now().strftime("%H:%M"),
            "Activity": user_text,
            "Type": "Task 📋"
        })
        st.rerun()

# ── Scheduled Reminders ───────────────────────────────────────────────────────
if st.session_state.scheduled:
    st.subheader("⏰ Scheduled Reminders")
    st.table(pd.DataFrame(st.session_state.scheduled))

# ── Task Blueprint ────────────────────────────────────────────────────────────
st.subheader("📋 Today's Blueprint")
if st.session_state.tasks:
    st.table(pd.DataFrame(st.session_state.tasks))
    if st.button("Clear Day"):
        st.session_state.tasks = []
        st.session_state.scheduled = []
        st.rerun()
else:
    st.info("Ready for your first command!")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🔔 Notifications via **ntfy.sh** · "
    "Install the free **ntfy app** on Android/iOS and subscribe to `floyd_zenith_alerts` · "
    "🎙️ Voice requires **Chrome** or **Edge**"
)
