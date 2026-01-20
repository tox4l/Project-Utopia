import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
import json
import random
import time
import base64

# ==========================================
# ⚙️ CONFIGURATION & CONSTANTS
# ==========================================
PAGE_TITLE = "PROJECT UTOPIA"
PAGE_ICON = "🪐"
DATA_FILE = 'mission_data.csv'
TODO_FILE = 'todo_list.json'
BOOKS_FILE = 'library_status.json'
JOURNAL_FILE = 'journal_entries.json'

GOAL_MONEY = 400000  # QAR
CURRENCY = "QAR"

# TRAVIS SCOTT / UTOPIA LYRIC BANK (EXPANDED)
LYRICS = [
    "The situation we are in at this time, neither a good one, nor is it so unblest.",
    "It can be held that we are in the process of creating a new world.",
    "Welcome to Utopia.",
    "I'm the highest in the room.",
    "Transform with the times, or get left behind.",
    "I can't wait just to shit on you.",
    "Create the wave, don't ride it.",
    "Sun is down, freezin' cold.",
    "Whole squad goin' up, Jackboys on the loose.",
    "Lost forever, but we're still together.",
    "Twin bitches hopping off a jet ski.",
    "Packin' out the stadium, we constructin' the mayhem.",
    "I tried to show 'em, yeah, I tried to show 'em.",
    "See the vision, I'm seein' the vision.",
    "Identify the enemy, then we attack.",
    "If you fall for the games, then you're the one playin'.",
    "Switching lanes, switching gears.",
    "Only trill niggas I know.",
    "Fein', fein', fein', fein'!",
    "I've been flyin' out of town for some peace of mind.",
    "It's a lot of heads poppin' out, but we ain't duckin' no reck.",
]

# TOXIC MOTIVATION BANK
TOXIC_QUOTES = [
    "You are 19. Zuckerberg had Facebook at 19. You have excuses.",
    "Nobody cares about your potential. They care about your results.",
    "The ZL1 is driving past you right now. Someone else is driving it.",
    "Sleep is the cousin of death. Wake up.",
    "You analyzed the market? Cute. Now sell something.",
    "Your comfort zone is where dreams go to die.",
    "Medocrity is a disease. You are showing symptoms.",
    "Do you want to be a boss or a worker? Decide.",
    "Pain is temporary. Being broke is forever if you don't move.",
    "Zero revenue today? Then you are unemployed.",
]

# THE LIBRARY
REQUIRED_READING = [
    "48 Laws of Power",
    "Influence: The Psychology of Persuasion",
    "Concise Mastery",
    "The Art of War",
    "Atomic Habits",
    "The Laws of Human Nature",
    "33 Strategies of War",
    "The Art of Seduction",
    "Meditations"
]

# THE PODCASTS (UPDATED)
REQUIRED_LISTENING = {
    "Alex Hormozi": "The Game (Business Strategy & Acquisition)",
    "Lex Fridman": "Deep Tech, AI & High-Level Discourse",
    "My First Million": "Market Gaps & Business Ideas",
    "Huberman Lab": "Biological Optimization (Sleep/Focus)",
    "Modern Wisdom (Chris Williamson)": "Human Nature, Psychology & Evolution"
}

# ==========================================
# 🛠️ DATA ENGINE
# ==========================================

def init_files():
    """Initialize data files if they don't exist."""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "Date", "Cold_Calls", "Deep_Work_Hrs", 
            "Calories", "Workouts", "Money_In", "Sleep_Hrs", "Reading_Pages", "Notes"
        ])
        df.to_csv(DATA_FILE, index=False)
    
    if not os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'w') as f:
            json.dump([], f)
            
    if not os.path.exists(BOOKS_FILE):
        books_db = {book: {"status": "Not Started", "progress": 0} for book in REQUIRED_READING}
        with open(BOOKS_FILE, 'w') as f:
            json.dump(books_db, f)

    if not os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, 'w') as f:
            json.dump([], f)

def load_data(): return pd.read_csv(DATA_FILE)
def save_log_entry(entry):
    df = load_data()
    entry_df = pd.DataFrame([entry])
    df = pd.concat([df, entry_df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def load_json(file):
    with open(file, 'r') as f: return json.load(f)
def save_json(file, data):
    with open(file, 'w') as f: json.dump(data, f)

init_files()

# ==========================================
# 🎨 UI & CSS (UTOPIA AESTHETIC)
# ==========================================
st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon=PAGE_ICON)

# JAVASCRIPT FOR LYRIC ROTATION
# We inject a script that finds the element and updates it every 60s
lyrics_json = json.dumps(LYRICS)
st.markdown(f"""
<script>
    const lyrics = {lyrics_json};
    function updateLyric() {{
        const el = document.getElementById('lyric-display');
        if (el) {{
            const randomLyric = lyrics[Math.floor(Math.random() * lyrics.length)];
            el.innerHTML = "🎧 " + randomLyric;
            el.style.opacity = 0;
            setTimeout(() => {{ el.style.opacity = 0.8; }}, 500);
        }}
    }}
    setInterval(updateLyric, 60000);
</script>
""", unsafe_allow_html=True)

st.markdown(f"""
    <style>
    /* --- GLOBAL RESET & FONTS --- */
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: #050505;
        color: #e0e0e0;
        overflow-x: hidden;
    }}
    
    /* --- ANIMATED BACKGROUND --- */
    .stApp {{
        background: radial-gradient(circle at 50% -20%, #2e003e 0%, #000000 50%),
                    radial-gradient(circle at 80% 80%, #1a0b2e 0%, #000000 40%);
        background-attachment: fixed;
    }}
    
    /* Floating Debris Animation */
    @keyframes float {{
        0% {{ transform: translateY(0px) rotate(0deg); opacity: 0.3; }}
        50% {{ transform: translateY(-20px) rotate(10deg); opacity: 0.6; }}
        100% {{ transform: translateY(0px) rotate(0deg); opacity: 0.3; }}
    }}

    /* --- ARTIFACT CARDS (3D EFFECT) --- */
    .artifact-card {{
        background: rgba(20, 20, 20, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        position: relative;
        overflow: hidden;
    }}
    
    /* Holographic Hover */
    .artifact-card:hover {{
        transform: perspective(1000px) rotateX(2deg) translateY(-5px);
        box-shadow: 0 20px 40px -10px rgba(168, 85, 247, 0.2);
        border-color: rgba(168, 85, 247, 0.5);
    }}
    
    .artifact-card::before {{
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transition: 0.5s;
    }}
    
    .artifact-card:hover::before {{
        left: 100%;
    }}

    /* --- TYPOGRAPHY --- */
    h1 {{
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        letter-spacing: -2px;
        background: linear-gradient(180deg, #fff, #888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem !important;
        text-shadow: 0 0 30px rgba(255,255,255,0.1);
    }}
    
    h2, h3 {{
        font-family: 'Syncopate', sans-serif;
        color: #fff;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    
    #lyric-display {{
        font-family: 'Courier New', monospace;
        color: #d8b4fe;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
        opacity: 0.8;
        transition: opacity 0.5s ease;
        border-left: 2px solid #d8b4fe;
        padding-left: 10px;
    }}

    /* --- METRICS --- */
    div[data-testid="stMetricValue"] {{
        font-family: 'Syncopate', sans-serif;
        font-size: 36px;
        color: #fff;
        text-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
    }}
    
    div[data-testid="stMetricLabel"] {{
        color: #9ca3af;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 2px;
    }}

    /* --- INPUTS --- */
    .stTextInput > div > div, .stNumberInput > div > div, .stTextArea > div > div {{
        background-color: rgba(0, 0, 0, 0.3);
        border: 1px solid #333;
        color: white;
        border-radius: 8px;
    }}
    
    .stTextInput > div > div:focus-within {{
        border-color: #d8b4fe;
        box-shadow: 0 0 15px rgba(216, 180, 254, 0.2);
    }}
    
    /* --- BUTTONS --- */
    .stButton > button {{
        background: #000;
        border: 1px solid #d8b4fe;
        color: #d8b4fe;
        padding: 0.6rem 1.2rem;
        border-radius: 4px;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }}
    
    .stButton > button:hover {{
        background: #d8b4fe;
        color: #000;
        box-shadow: 0 0 20px rgba(216, 180, 254, 0.6);
    }}

    /* --- TABS --- */
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Syncopate', sans-serif;
        font-size: 12px;
        background-color: rgba(255,255,255,0.02);
    }}
    .stTabs [aria-selected="true"] {{
        background-color: rgba(168, 85, 247, 0.1) !important;
        border: 1px solid #a855f7 !important;
        color: #a855f7 !important;
    }}

    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🧠 HELPER FUNCTIONS
# ==========================================
def get_random_lyric():
    return random.choice(LYRICS)

def get_toxic_quote():
    return random.choice(TOXIC_QUOTES)

# ==========================================
# 🏠 MAIN LAYOUT
# ==========================================

# HEADER SECTION
c_head1, c_head2 = st.columns([4, 1])
with c_head1:
    st.markdown(f"<h1>PROJECT UTOPIA</h1>", unsafe_allow_html=True)
    # The ID 'lyric-display' is targeted by the JS above
    st.markdown(f"<div id='lyric-display'>🎧 {get_random_lyric()}</div>", unsafe_allow_html=True)

with c_head2:
    st.write("")
    st.write("")
    if st.button("💀 REALITY CHECK"):
        st.toast(get_toxic_quote(), icon="⚡")

# NAVIGATION TABS
tab_dash, tab_journal, tab_log, tab_tasks, tab_arsenal, tab_protocol = st.tabs([
    "📊 DASHBOARD", 
    "📓 JOURNAL",
    "📝 LOGS", 
    "✅ OPS", 
    "📚 ARSENAL", 
    "🗺️ PLAN"
])

# ==========================================
# 📊 TAB 1: DASHBOARD
# ==========================================
with tab_dash:
    df = load_data()
    total_money = df['Money_In'].sum() if not df.empty else 0
    money_remaining = GOAL_MONEY - total_money
    progress_pct = min(total_money / GOAL_MONEY, 1.0)
    
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown(f"### 🎯 TARGET: {GOAL_MONEY:,.0f} {CURRENCY}")
    st.progress(progress_pct)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("LIQUID CASH", f"{total_money:,.0f}", delta="QAR")
    c2.metric("REMAINING", f"{money_remaining:,.0f}", delta_color="inverse")
    
    # Days left in year calculation
    days_left = (date(2027, 1, 1) - date.today()).days
    c3.metric("TIME REMAINING", f"{days_left} DAYS", delta="HURRY UP")
    
    c4.metric("STATUS", "ACTIVE" if total_money > 0 else "STAGNANT", delta="UTOPIA")
    st.markdown("</div>", unsafe_allow_html=True)

    # Charts
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown("### 📈 TRAJECTORY ARTIFACT")
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        chart_df = df.sort_values('Date')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_df['Date'], y=chart_df['Money_In'], 
            fill='tozeroy', mode='lines+markers', name='Revenue',
            line=dict(color='#d8b4fe', width=3),
            marker=dict(size=8, color='#fff', line=dict(width=2, color='#d8b4fe'))
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ccc', family="Inter"),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            height=300, margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("NO DATA. SYSTEM WAITING.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 📓 TAB 2: JOURNAL (NEW)
# ==========================================
with tab_journal:
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown("### 🧠 MIND DUMP")
    st.markdown("Write freely. Clear the noise. Strategize.")
    
    with st.form("journal_form", clear_on_submit=True):
        j_title = st.text_input("Entry Title", placeholder="e.g., The Vision for March...")
        j_content = st.text_area("Content", height=200, placeholder="Pour it out...")
        j_submit = st.form_submit_button("SAVE TO ARCHIVE")
        
        if j_submit and j_title and j_content:
            entries = load_json(JOURNAL_FILE)
            new_entry = {
                "timestamp": str(datetime.now().strftime("%Y-%m-%d %H:%M")),
                "title": j_title,
                "content": j_content
            }
            entries.insert(0, new_entry) # Add to top
            save_json(JOURNAL_FILE, entries)
            st.success("ENTRY ENCRYPTED.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display Entries
    entries = load_json(JOURNAL_FILE)
    if entries:
        for ent in entries:
            with st.expander(f"📓 {ent['timestamp']} | {ent['title']}"):
                st.markdown(f"_{ent['content']}_")
    else:
        st.info("The archive is empty.")

# ==========================================
# 📝 TAB 3: LOGS
# ==========================================
with tab_log:
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown("### 📝 TACTICAL INPUT")
    with st.form("main_log_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            l_date = st.date_input("Date", date.today())
            l_calls = st.number_input("Cold Calls", min_value=0)
            l_money = st.number_input("Money In", min_value=0.0)
            l_deep = st.number_input("Deep Work (Hrs)", min_value=0.0, step=0.5)
        with c2:
            l_cal = st.number_input("Calories", min_value=0)
            l_sleep = st.number_input("Sleep (Hrs)", min_value=0.0)
            l_read = st.number_input("Pages Read", min_value=0)
            l_workout = st.checkbox("Workout Done?")
            l_notes = st.text_input("Short Note")
            
        if st.form_submit_button("LOG DATA"):
            save_log_entry({
                "Date": l_date, "Cold_Calls": l_calls, "Deep_Work_Hrs": l_deep,
                "Calories": l_cal, "Workouts": 1 if l_workout else 0,
                "Money_In": l_money, "Sleep_Hrs": l_sleep, "Reading_Pages": l_read, "Notes": l_notes
            })
            st.toast("LOGGED.", icon="💾")
    st.markdown("</div>", unsafe_allow_html=True)
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

# ==========================================
# ✅ TAB 4: OPS
# ==========================================
with tab_tasks:
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown("### ⚔️ DIRECTIVES")
    
    col_in, col_btn = st.columns([4, 1])
    with col_in:
        new_task = st.text_input("New Task", placeholder="Execute order...", label_visibility="collapsed")
    with col_btn:
        if st.button("ADD"):
            if new_task:
                todos = load_json(TODO_FILE)
                todos.append({"task": new_task, "done": False})
                save_json(TODO_FILE, todos)
                st.rerun()
                
    todos = load_json(TODO_FILE)
    if todos:
        for i, todo in enumerate(todos):
            done = st.checkbox(todo['task'], value=todo['done'], key=f"t_{i}")
            if done != todo['done']:
                todos[i]['done'] = done
                save_json(TODO_FILE, todos)
                st.rerun()
        
        if st.button("PURGE COMPLETED"):
            todos = [t for t in todos if not t['done']]
            save_json(TODO_FILE, todos)
            st.rerun()
    else:
        st.markdown("*No active directives.*")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 📚 TAB 5: ARSENAL
# ==========================================
with tab_arsenal:
    c_b, c_p = st.columns(2)
    
    with c_b:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 📘 CODEX (BOOKS)")
        books = load_json(BOOKS_FILE)
        for title in REQUIRED_READING:
            if title not in books: books[title] = {"status": "Not Started", "progress": 0}
            b = books[title]
            
            with st.expander(f"{title} ({b['progress']}%)"):
                s = st.selectbox("Status", ["Not Started", "Reading", "Done"], key=f"s_{title}", 
                               index=["Not Started", "Reading", "Done"].index(b['status'] if b['status'] in ["Not Started", "Reading", "Done"] else "Not Started"))
                p = st.slider("Progress", 0, 100, b['progress'], key=f"p_{title}")
                if s != b['status'] or p != b['progress']:
                    books[title] = {"status": s, "progress": p}
                    save_json(BOOKS_FILE, books)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_p:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 🎙️ SIGNAL INTERCEPT (PODCASTS)")
        for name, desc in REQUIRED_LISTENING.items():
            st.markdown(f"""
            <div style='margin-bottom: 15px; border-left: 2px solid #d8b4fe; padding-left: 10px;'>
                <div style='font-weight: 700; color: #fff;'>{name}</div>
                <div style='font-size: 12px; color: #888;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 🗺️ TAB 6: PLAN
# ==========================================
with tab_protocol:
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown("## 🗓️ Q1 2026: THE BLUEPRINT")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### PHASE 1 (FEB)")
        st.markdown("""
        * [ ] **ID:** Launch "Hustler" Persona.
        * [ ] **OPS:** 50 Cold DMs.
        * [ ] **TECH:** Build AI Agent MVP (Voiceflow).
        * [ ] **WIN:** 1st Client Signed.
        """)
    with c2:
        st.markdown("### PHASE 2 (MAR)")
        st.markdown("""
        * [ ] **SCALE:** Hire VA for Leads.
        * [ ] **AUTO:** Automate Fulfillment.
        * [ ] **MONEY:** Hit 10k QAR/Month.
        """)
    st.markdown("</div>", unsafe_allow_html=True)
