import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
import json
import random
import time

# ==========================================
# ⚙️ CONFIGURATION & CONSTANTS
# ==========================================
PAGE_TITLE = "PROJECT UTOPIA // COMMAND"
PAGE_ICON = "🪐"
DATA_FILE = 'mission_data.csv'
TODO_FILE = 'todo_list.json'
BOOKS_FILE = 'library_status.json'
JOURNAL_FILE = 'journal_entries.json'

GOAL_MONEY = 400000  # QAR Target (ZL1 + C6 + Freedom)
CURRENCY = "QAR"
START_DATE = date(2026, 1, 1) # Assumed start of mission

# TRAVIS SCOTT / UTOPIA LYRIC BANK
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
    "Your ideas are worthless. Your execution is everything.",
]

# LIBRARY & PODCASTS
REQUIRED_READING = [
    "48 Laws of Power", "Influence: The Psychology of Persuasion", "Concise Mastery",
    "The Art of War", "Atomic Habits", "The Laws of Human Nature",
    "33 Strategies of War", "The Art of Seduction", "Meditations"
]

REQUIRED_LISTENING = {
    "Alex Hormozi": "The Game (Business Strategy & Acquisition)",
    "Lex Fridman": "Deep Tech, AI & High-Level Discourse",
    "My First Million": "Market Gaps & Business Ideas",
    "Huberman Lab": "Biological Optimization (Sleep/Focus)",
    "Modern Wisdom": "Human Nature, Psychology & Evolution (Chris Williamson)"
}

# ==========================================
# 🛠️ DATA ENGINE
# ==========================================
def init_files():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Date", "Cold_Calls", "Deep_Work_Hrs", "Calories", "Workouts", "Money_In", "Sleep_Hrs", "Reading_Pages", "Notes"])
        df.to_csv(DATA_FILE, index=False)
    if not os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'w') as f: json.dump([], f)
    if not os.path.exists(BOOKS_FILE):
        books_db = {book: {"status": "Not Started", "progress": 0} for book in REQUIRED_READING}
        with open(BOOKS_FILE, 'w') as f: json.dump(books_db, f)
    if not os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, 'w') as f: json.dump([], f)

def load_data(): return pd.read_csv(DATA_FILE)
def save_log_entry(entry):
    df = load_data()
    entry_df = pd.DataFrame([entry])
    df = pd.concat([df, entry_df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
def load_json(file):
    try:
        with open(file, 'r') as f: return json.load(f)
    except: return [] # Fail safe
def save_json(file, data):
    with open(file, 'w') as f: json.dump(data, f)

init_files()

# ==========================================
# 🎨 UI & CSS
# ==========================================
st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon=PAGE_ICON)

# INJECT SCRIPTS & STYLES
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
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    :root {{
        --neon-purple: #d8b4fe;
        --neon-red: #ff4b4b;
        --glass-bg: rgba(20, 20, 20, 0.6);
        --glass-border: rgba(255, 255, 255, 0.1);
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: #050505;
        color: #e0e0e0;
        overflow-x: hidden;
    }}
    
    .stApp {{
        background: radial-gradient(circle at 50% -20%, #2e003e 0%, #000000 50%),
                    radial-gradient(circle at 80% 80%, #1a0b2e 0%, #000000 40%);
        background-attachment: fixed;
    }}

    /* ARTIFACT CARDS */
    .artifact-card {{
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .artifact-card:hover {{
        border-color: rgba(216, 180, 254, 0.3);
        box-shadow: 0 0 20px rgba(100, 0, 255, 0.1);
        transform: translateY(-2px);
    }}

    /* TYPOGRAPHY */
    h1 {{
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        letter-spacing: -2px;
        background: linear-gradient(180deg, #fff, #888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
    }}
    
    h2, h3 {{
        font-family: 'Syncopate', sans-serif;
        color: #fff;
        font-weight: 700;
        letter-spacing: 1px;
        font-size: 1.2rem;
    }}
    
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .highlight {{ color: var(--neon-purple); font-weight: bold; }}
    .alert {{ color: var(--neon-red); font-weight: bold; }}

    /* METRICS */
    div[data-testid="stMetricValue"] {{
        font-family: 'Syncopate', sans-serif;
        font-size: 32px;
        color: #fff;
        text-shadow: 0 0 10px rgba(168, 85, 247, 0.3);
    }}
    
    div[data-testid="stMetricLabel"] {{
        font-family: 'JetBrains Mono', monospace;
        color: #888;
        font-size: 11px;
        letter-spacing: 1px;
    }}

    /* BUTTONS & INPUTS */
    .stButton > button {{
        background: #000;
        border: 1px solid var(--neon-purple);
        color: var(--neon-purple);
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        transition: 0.3s;
    }}
    .stButton > button:hover {{
        background: var(--neon-purple);
        color: #000;
        box-shadow: 0 0 15px var(--neon-purple);
    }}
    
    .stTextInput > div > div, .stNumberInput > div > div {{
        background: rgba(0,0,0,0.5);
        border: 1px solid #333;
        color: #fff;
    }}

    /* TAB STYLING */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255,255,255,0.03);
        border: 1px solid transparent;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
    }}
    .stTabs [aria-selected="true"] {{
        border: 1px solid var(--neon-purple) !important;
        color: var(--neon-purple) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 HELPERS
# ==========================================
def get_random_lyric(): return random.choice(LYRICS)
def get_toxic_quote(): return random.choice(TOXIC_QUOTES)

# ==========================================
# 🏠 HEADER
# ==========================================
c_head1, c_head2 = st.columns([5, 1])
with c_head1:
    st.markdown(f"<h1>PROJECT UTOPIA</h1>", unsafe_allow_html=True)
    st.markdown(f"<div id='lyric-display' class='mono' style='color: #d8b4fe; border-left: 2px solid #d8b4fe; padding-left: 10px;'>🎧 {get_random_lyric()}</div>", unsafe_allow_html=True)

with c_head2:
    st.write("")
    if st.button("💀 REALITY CHECK"):
        st.toast(get_toxic_quote(), icon="⚡")

# TABS
tab_dash, tab_plan, tab_log, tab_journal, tab_tasks, tab_arsenal = st.tabs([
    "📊 COMMAND", "🗺️ BATTLE PLAN", "📝 LOGS", "📓 JOURNAL", "✅ OPS", "📚 ARSENAL"
])

# ==========================================
# 📊 TAB 1: COMMAND CENTER (IMPROVED)
# ==========================================
with tab_dash:
    df = load_data()
    
    # --- CALCULATION ENGINE ---
    total_money = df['Money_In'].sum() if not df.empty else 0
    money_remaining = GOAL_MONEY - total_money
    days_elapsed = (date.today() - START_DATE).days
    if days_elapsed <= 0: days_elapsed = 1
    
    # Win Rate: % of days where user did > 2 hrs deep work OR made calls OR worked out
    if not df.empty:
        active_days = df[
            (df['Deep_Work_Hrs'] >= 2) | 
            (df['Cold_Calls'] > 0) | 
            (df['Workouts'] == 1)
        ].shape[0]
        total_logged_days = df.shape[0]
        win_rate = (active_days / total_logged_days * 100) if total_logged_days > 0 else 0
    else:
        win_rate = 0
    
    # Burn Rate needed
    days_left_in_year = 365 - (date.today().timetuple().tm_yday)
    daily_target = money_remaining / days_left_in_year if days_left_in_year > 0 else 0

    # --- ROW 1: STATUS & FINANCE ---
    c1, c2, c3 = st.columns([1.5, 1, 1])
    
    with c1:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown(f"### ⚔️ WAR CHEST: {total_money:,.0f} / {GOAL_MONEY:,.0f} {CURRENCY}")
        prog = min(total_money / GOAL_MONEY, 1.0)
        st.progress(prog)
        st.caption(f"{prog*100:.2f}% COMPLETED")
        
        mc1, mc2 = st.columns(2)
        mc1.metric("LIQUID CASH", f"{total_money:,.0f}", delta="GENERATED")
        mc2.metric("REMAINING GAP", f"{money_remaining:,.0f}", delta_color="inverse")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 🚦 SYSTEM STATUS")
        st.metric("WIN RATE (CONSISTENCY)", f"{win_rate:.1f}%", delta="AIM FOR 90%+")
        status_color = "#00ff00" if win_rate > 80 else "#ff4b4b"
        st.markdown(f"<div style='font-size: 12px; color: {status_color};'>SYSTEM INTEGRITY: {'OPTIMAL' if win_rate > 80 else 'COMPROMISED'}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 🔥 BURN RATE")
        st.metric("REQ. DAILY PROFIT", f"{daily_target:,.0f} {CURRENCY}", delta="TO HIT TARGET")
        st.caption(f"You must net {daily_target:,.0f} QAR every single day until Dec 31.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- ROW 2: IMMEDIATE INTEL ---
    c_intel1, c_intel2 = st.columns([2, 1])
    
    with c_intel1:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### ⚠️ PRIORITY DIRECTIVES")
        todos = load_json(TODO_FILE)
        active_todos = [t for t in todos if not t['done']]
        if active_todos:
            for i, t in enumerate(active_todos[:3]): # Show top 3
                st.markdown(f"<div style='border-bottom: 1px solid #333; padding: 8px 0;'>◻️ <span class='mono'>{t['task']}</span></div>", unsafe_allow_html=True)
            if len(active_todos) > 3:
                st.caption(f"...and {len(active_todos)-3} more in OPS tab.")
        else:
            st.markdown("*No active directives. You are drifting. Go to OPS.*")
        st.markdown("</div>", unsafe_allow_html=True)

    with c_intel2:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 🧬 LAST LOG")
        if not df.empty:
            last = df.iloc[-1]
            st.markdown(f"**DATE:** {last['Date']}")
            st.markdown(f"**CALLS:** {last['Cold_Calls']}")
            st.markdown(f"**DEEP WORK:** {last['Deep_Work_Hrs']} HRS")
            st.markdown(f"**REVENUE:** {last['Money_In']} {CURRENCY}")
        else:
            st.warning("NO DATA FOUND.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 🗺️ TAB 2: DETAILED BATTLE PLAN
# ==========================================
with tab_plan:
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown("## 🗺️ OPERATIONAL BLUEPRINT: Q1 2026")
    st.markdown("This is not a suggestion. This is the script. Deviate and you fail.")
    st.markdown("</div>", unsafe_allow_html=True)

    # PHASE 1
    st.markdown("### 🗓️ PHASE 1: FEB 2026 (FOUNDATION & VALIDATION)")
    
    with st.expander("WEEK 1: THE IDENTITY SHIFT & OFFER", expanded=True):
        st.markdown("""
        **OBJECTIVE:** Establish the vessel. Define the offer.
        - [ ] **LEGAL/ADMIN:** Separate Personal vs Business finances (Wise/Bank).
        - [ ] **BRAND:** "The Hustler" Persona Launch. Post 1 High-Quality Reel/TikTok (Cinematic, dark).
        - [ ] **OFFER:** Define the "AI Support Agent" package. (Setup Fee: 2000 QAR, Retainer: 500 QAR).
        - [ ] **DATA:** Scrape 50 leads (Qatar SMEs: Gyms, Real Estate, Clinics) using Google Maps.
        - [ ] **TECH:** Build a 'Dummy' Agent on Replit/Voiceflow just to show a demo.
        """)

    with st.expander("WEEK 2: AGGRESSIVE OUTREACH"):
        st.markdown("""
        **OBJECTIVE:** Break the silence. Get rejected.
        - [ ] **KPI:** 100 Cold DMs/Emails sent. 20 Cold Calls made.
        - [ ] **SCRIPT:** A/B Test 2 scripts. (1. Direct Pitch, 2. Value-First/Free Audit).
        - [ ] **MEETINGS:** Book 3 Demos.
        - [ ] **CONTENT:** Document the struggle. "Day 7: Getting rejected by 10 CEOs."
        """)

    with st.expander("WEEK 3: FIRST BLOOD"):
        st.markdown("""
        **OBJECTIVE:** Proof of Concept. Money changes hands.
        - [ ] **CLOSE:** Sign Client #1. (Even if you have to discount, get the case study).
        - [ ] **DELIVERY:** Deploy the agent for Client #1. Ensure 99% uptime.
        - [ ] **SYSTEM:** Create a "Client Onboarding" checklist so you don't panic next time.
        """)
        
    with st.expander("WEEK 4: REFINEMENT"):
        st.markdown("""
        **OBJECTIVE:** Iron out bugs. Collect testimonial.
        - [ ] **REVIEW:** Fix bugs in Client #1's agent.
        - [ ] **SOCIAL PROOF:** Get a video testimonial from Client #1.
        - [ ] **OUTREACH:** Use the testimonial to hit 50 new leads. "We did X for [Client Name], we can do it for you."
        """)

    # PHASE 2
    st.markdown("---")
    st.markdown("### 🗓️ PHASE 2: MAR 2026 (SYSTEMIZATION & SCALE)")
    
    with st.expander("WEEK 5: AUTOMATION"):
        st.markdown("""
        **OBJECTIVE:** Remove yourself from the loop.
        - [ ] **TECH:** Build a Python script to scrape leads automatically.
        - [ ] **HIRE:** Find a commission-only setter or a cheap VA for data entry.
        - [ ] **PRICE:** Raise Setup Fee to 4,000 QAR.
        """)

    with st.expander("WEEK 6-8: VELOCITY"):
        st.markdown("""
        **OBJECTIVE:** Velocity.
        - [ ] **KPI:** 10k QAR/Month Run Rate.
        - [ ] **INPUT:** 200 Leades contacted per week.
        - [ ] **BRAND:** "How I run an AI Agency in Qatar" (Long form YouTube).
        """)

# ==========================================
# 📝 TAB 3: LOGS
# ==========================================
with tab_log:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 📝 INPUT TERMINAL")
        with st.form("log_form", clear_on_submit=True):
            date_in = st.date_input("Date", date.today())
            calls = st.number_input("Calls/DMs", min_value=0)
            money = st.number_input(f"Revenue ({CURRENCY})", min_value=0.0)
            deep = st.number_input("Deep Work (Hrs)", min_value=0.0, step=0.5)
            
            st.markdown("---")
            cal = st.number_input("Calories", min_value=0)
            sleep = st.number_input("Sleep (Hrs)", min_value=0.0)
            read = st.number_input("Pages Read", min_value=0)
            workout = st.checkbox("Workout Complete?")
            note = st.text_input("Debrief Note")
            
            if st.form_submit_button("COMMIT ENTRY"):
                save_log_entry({
                    "Date": date_in, "Cold_Calls": calls, "Deep_Work_Hrs": deep,
                    "Calories": cal, "Workouts": 1 if workout else 0,
                    "Money_In": money, "Sleep_Hrs": sleep, "Reading_Pages": read, "Notes": note
                })
                st.toast("ENTRY SAVED.", icon="💾")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("### 🗄️ DATABASE")
        st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True, height=500)

# ==========================================
# 📓 TAB 4: JOURNAL
# ==========================================
with tab_journal:
    st.markdown("### 🧠 NEURAL DUMP")
    
    with st.form("journal_entry"):
        title = st.text_input("Subject Line")
        body = st.text_area("Content", height=150)
        if st.form_submit_button("ENCRYPT THOUGHT"):
            if title and body:
                entries = load_json(JOURNAL_FILE)
                entries.insert(0, {"time": str(datetime.now())[:16], "title": title, "body": body})
                save_json(JOURNAL_FILE, entries)
                st.rerun()

    entries = load_json(JOURNAL_FILE)
    for ent in entries:
        with st.expander(f"{ent['time']} | {ent['title']}"):
            st.markdown(ent['body'])

# ==========================================
# ✅ TAB 5: OPS (TASKS)
# ==========================================
with tab_tasks:
    st.markdown("### ⚔️ TACTICAL OPS")
    
    c_add, c_list = st.columns([1, 2])
    with c_add:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        new_task = st.text_input("New Directive", placeholder="e.g. Call TDT...")
        if st.button("ADD DIRECTIVE"):
            if new_task:
                todos = load_json(TODO_FILE)
                todos.append({"task": new_task, "done": False})
                save_json(TODO_FILE, todos)
                st.rerun()
        if st.button("PURGE COMPLETED"):
            todos = load_json(TODO_FILE)
            todos = [t for t in todos if not t['done']]
            save_json(TODO_FILE, todos)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with c_list:
        todos = load_json(TODO_FILE)
        if todos:
            for i, todo in enumerate(todos):
                done = st.checkbox(todo['task'], value=todo['done'], key=f"todo_{i}")
                if done != todo['done']:
                    todos[i]['done'] = done
                    save_json(TODO_FILE, todos)
                    st.rerun()
        else:
            st.info("NO ACTIVE DIRECTIVES.")

# ==========================================
# 📚 TAB 6: ARSENAL
# ==========================================
with tab_arsenal:
    c_read, c_listen = st.columns(2)
    
    with c_read:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 📘 CODEX")
        books = load_json(BOOKS_FILE)
        for b_name in REQUIRED_READING:
            if b_name not in books: books[b_name] = {"status": "Not Started", "progress": 0}
            b_data = books[b_name]
            
            with st.expander(f"{b_name} ({b_data['progress']}%)"):
                s = st.selectbox("Status", ["Not Started", "Reading", "Absorbed"], 
                               index=["Not Started", "Reading", "Absorbed"].index(b_data.get('status', "Not Started")), key=f"s_{b_name}")
                p = st.slider("Progress", 0, 100, b_data.get('progress', 0), key=f"p_{b_name}")
                
                if s != b_data.get('status') or p != b_data.get('progress'):
                    books[b_name] = {"status": s, "progress": p}
                    save_json(BOOKS_FILE, books)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_listen:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 🎙️ INTEL STREAMS")
        for pod, desc in REQUIRED_LISTENING.items():
            st.markdown(f"**{pod}**")
            st.caption(desc)
            st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)
