import streamlit as st
import pandas as pd
import random
import time
from fuzzywuzzy import fuzz

# 1. Page Config
st.set_page_config(page_title="Aviation Oral Master", page_icon="✈️")

# --- Fixed Image via URL (v10.6.3) ---
# No more 'image_0.png' file needed. We'll use a reliable internet image.
st.image("https://images.unsplash.com/photo-1474302770737-173ee21bab6c?q=80&w=1000&auto=format&fit=crop", 
         caption="Vintage Propeller Aircraft", 
         use_container_width=True)

# Custom UI Design
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; font-size: 1.2em; border-radius: 15px; margin-bottom: 10px; background-color: #1A5276; color: white; font-weight: bold; }
    .audio-btn>button { background-color: #E67E22 !important; border: 2px solid white; }
    .q-box { background-color: #f4f6f7; padding: 25px; border-radius: 15px; border-left: 10px solid #27ae60; color: #1c2833; margin-bottom: 25px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    h1, h3 { color: #154360; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Strong Voice Function (Audio Engine)
def speak(text):
    js_code = f"""
    <script>
    (function() {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{text.replace('"', '').replace("'", "")}");
        msg.lang = 'en-US';
        msg.rate = 0.85;
        window.speechSynthesis.speak(msg);
    }})();
    </script>
    """
    st.components.v1.html(js_code, height=0)

def wake_up_audio():
    js_wake = "<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance('Audio ready'));</script>"
    st.components.v1.html(js_wake, height=0)

# 3. Session State
if 'state' not in st.session_state:
    st.session_state.update({'state': 'MENU', 'pool': [], 'idx': 0, 'wrongs': []})

# --- PAGE: MAIN MENU ---
if st.session_state.state == 'MENU':
    st.markdown("<h1>Aviation Oral Master</h1>", unsafe_allow_html=True)
    
    # Audio Activation Button
    st.markdown('<div class="audio-btn">', unsafe_allow_html=True)
    if st.button("📢 1. TAP TO ENABLE AUDIO"):
        wake_up_audio()
        st.success("Audio system activated!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    cat = st.radio("Select Subject:", ["General", "Airframe", "Powerplant"])
    q_count = st.slider("Questions:", 5, 100, 37)
    
    if st.button("🚀 2. START SESSION"):
        try:
            df = pd.read_csv(f"{cat.lower()}.csv")
            raw_data = [row for row in df.values.tolist() if len(row) >= 2]
            st.session_state.pool = random.sample(raw_data, min(len(raw_data), q_count))
            st.session_state.state = 'TEST'
            st.session_state.idx = 0
            st.session_state.wrongs = []
            st.rerun()
        except:
            st.error("CSV files not found. Check your GitHub files.")

# --- PAGE: TEST SESSION ---
elif st.session_state.state == 'TEST':
    pool = st.session_state.pool
    idx = st.session_state.idx
    if idx < len(pool):
        q, a = pool[idx]
        st.write(f"Question {idx+1} of {len(pool)}")
        st.markdown(f"<div class='q-box'><h3>{q}</h3></div>", unsafe_allow_html=True)
        
        if st.button("🔊 Listen to Question"):
            speak(q)
            
        user_ans = st.text_input("Your Answer:", key=f"q_{idx}")
        if st.button("✅ Submit"):
            score = fuzz.token_sort_ratio(user_ans.lower(), a.lower())
            if score >= 60: st.success(f"Correct! ({score}%)")
            else:
                st.error("Incorrect.")
                st.info(f"Answer: {a}")
                st.session_state.wrongs.append({'q': q, 'a': a, 'u': user_ans})
            time.sleep(2.0)
            st.session_state.idx += 1
            st.rerun()
    else:
        st.session_state.state = 'REVIEW'
        st.rerun()
