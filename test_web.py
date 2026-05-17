import streamlit as st
import pandas as pd
import random
import time
from fuzzywuzzy import fuzz

# 1. Page Config
st.set_page_config(page_title="Aviation Oral Master", page_icon="✈️")

# --- Custom Image Insertion (v10.6.0) ---
# This line adds Abraham's custom vintage propeller aircraft image.
st.image("image_0.png", use_container_width=True)
# ---------------------------------------

# Custom UI: Professional English Interface with new Image
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; font-size: 1.2em; border-radius: 15px; margin-bottom: 10px; background-color: #1A5276; color: white; font-weight: bold; }
    .stTextInput>div>div>input { height: 3em; font-size: 1.1em; }
    .q-box { background-color: #f4f6f7; padding: 25px; border-radius: 15px; border-left: 10px solid #27ae60; color: #1c2833; margin-bottom: 25px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    h1, h3 { color: #154360; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Optimized Voice Function
def speak(text):
    js_code = f"""
    <script>
    function playTTS() {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance();
        msg.text = "{text.replace('"', '').replace("'", "")}";
        msg.lang = 'en-US';
        msg.rate = 0.9; 
        window.speechSynthesis.speak(msg);
    }}
    playTTS();
    </script>
    """
    st.components.v1.html(js_code, height=0)

# 3. Data Loader
def load_data(category):
    file_path = f"{category.lower()}.csv"
    try:
        df = pd.read_csv(file_path)
        data = [row for row in df.values.tolist() if len(row) >= 2]
        return data
    except:
        return []

# 4. Session State
if 'state' not in st.session_state:
    st.session_state.update({'state': 'MENU', 'pool': [], 'idx': 0, 'wrongs': []})

# --- PAGE: MAIN MENU ---
if st.session_state.state == 'MENU':
    # Changed to accommodate the image.
    st.markdown("<h1>Aviation Oral Master</h1>", unsafe_allow_html=True)
    st.subheader("FAA Certification Prep")
    
    cat = st.radio("Select Subject:", ["General", "Airframe", "Powerplant"])
    q_count = st.slider("Number of Questions:", 5, 100, 37)
    
    if st.button("🚀 START SESSION"):
        raw_data = load_data(cat)
        if len(raw_data) > 0:
            st.session_state.pool = random.sample(raw_data, min(len(raw_data), q_count))
            st.session_state.state = 'TEST'
            st.session_state.idx = 0
            st.session_state.wrongs = []
            st.rerun()
        else:
            st.error(f"Error: {cat}.csv not found or empty.")

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
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Submit"):
                score = fuzz.token_sort_ratio(user_ans.lower(), a.lower())
                if score >= 60:
                    st.success(f"Correct! ({score}%)")
                else:
                    st.error(f"Incorrect.")
                    st.info(f"Answer: {a}")
                    st.session_state.wrongs.append({'q': q, 'a': a, 'u': user_ans})
                time.sleep(2.0)
                st.session_state.idx += 1
                st.rerun()
        with col2:
            if st.button("🛑 Exit & Review"):
                st.session_state.state = 'REVIEW'
                st.rerun()
    else:
        st.session_state.state = 'REVIEW'
        st.rerun()

# --- PAGE: REVIEW ---
elif st.session_state.state == 'REVIEW':
    st.title("📝 Performance Review")
    if not st.session_state.wrongs:
        st.balloons()
        st.success("Perfect! You're ready for the exam.")
    else:
        st.warning(f"You missed {len(st.session_state.wrongs)} questions.")
        for m in st.session_state.wrongs:
            with st.expander(f"Q: {m['q'][:50]}..."):
                st.write(f"**Question:** {m['q']}")
                st.write(f"**Your Answer:** :red[{m['u']}]")
                st.write(f"**Correct Key:** :green[{m['a']}]")
                
    if st.button("🏠 Back to Main Menu"):
        st.session_state.state = 'MENU'
        st.rerun()
