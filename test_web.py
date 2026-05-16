import streamlit as st
import pandas as pd
import random
import time
from fuzzywuzzy import fuzz

# 1. Page Configuration for Smartphone
st.set_page_config(page_title="Aviation Oral Master Mobile", page_icon="✈️")

# Custom UI for Smartphone (Large Buttons & Mobile Font)
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; font-size: 1.2em; border-radius: 15px; margin-bottom: 10px; }
    .stTextInput>div>div>input { height: 3em; font-size: 1.1em; }
    .q-box { background-color: #f0f2f6; padding: 20px; border-radius: 15px; border-left: 8px solid #27ae60; color: #1f1f1f; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Browser-based Voice (JavaScript)
def speak(text):
    js = f"<script>var m=new SpeechSynthesisUtterance('{text.replace("'", "")}');m.lang='en-US';window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# 3. Data Loading Logic
def load_data(category):
    file_path = f"{category.lower()}.csv"
    try:
        df = pd.read_csv(file_path)
        return df.values.tolist()
    except:
        # Dummy data if file is missing for initial test
        return [("Sample Question: What is 1+1?", "2")]

# 4. Session State Initialization
if 'state' not in st.session_state:
    st.session_state.update({'state': 'MENU', 'pool': [], 'idx': 0, 'wrongs': []})

# --- PAGE: MAIN MENU ---
if st.session_state.state == 'MENU':
    st.title("✈️ Aviation Oral Master")
    st.subheader("Mobile Study Portal")
    
    cat = st.radio("Select Subject:", ["General", "Airframe", "Powerplant"])
    q_count = st.slider("Questions:", 5, 50, 37)
    
    if st.button("🚀 START EXAM"):
        raw_data = load_data(cat)
        st.session_state.pool = random.sample(raw_data, min(len(raw_data), q_count))
        st.session_state.state = 'TEST'
        st.session_state.idx = 0
        st.session_state.wrongs = []
        st.rerun()

# --- PAGE: TEST SESSION ---
elif st.session_state.state == 'TEST':
    pool = st.session_state.pool
    idx = st.session_state.idx
    
    if idx < len(pool):
        q, a = pool[idx]
        st.write(f"Question {idx+1} of {len(pool)}")
        st.markdown(f"<div class='q-box'><h3>{q}</h3></div>", unsafe_allow_html=True)
        
        if st.button("🔊 Listen Question"):
            speak(q)
            
        user_ans = st.text_input("Your Answer:", key=f"q_{idx}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Submit"):
                score = fuzz.token_sort_ratio(user_ans.lower(), a.lower())
                if score >= 60:
                    st.success(f"Correct! ({score}%)")
                else:
                    st.error(f"Incorrect. Answer: {a}")
                    st.session_state.wrongs.append({'q': q, 'a': a, 'u': user_ans})
                time.sleep(1.5)
                st.session_state.idx += 1
                st.rerun()
        with col2:
            if st.button("🛑 Stop"):
                st.session_state.state = 'REVIEW'
                st.rerun()
    else:
        st.session_state.state = 'REVIEW'
        st.rerun()

# --- PAGE: REVIEW ---
elif st.session_state.state == 'REVIEW':
    st.title("📝 Mistake Review")
    if not st.session_state.wrongs:
        st.balloons()
        st.success("Perfect Score! No mistakes.")
    else:
        for m in st.session_state.wrongs:
            with st.expander(f"Q: {m['q'][:40]}..."):
                st.write(f"**Question:** {m['q']}")
                st.write(f"**Your Answer:** :red[{m['u']}]")
                st.write(f"**Correct Key:** :green[{m['a']}]")
                
    if st.button("🏠 Back to Menu"):
        st.session_state.state = 'MENU'
        st.rerun()