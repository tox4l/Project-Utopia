import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
import json
import random

# ==========================================
# ⚙️ CRITICAL FIX: PAGE CONFIG FIRST
# ==========================================
st.set_page_config(
    page_title="PROJECT UTOPIA",  # <-- Put the string here, not the variable
    layout="wide",
    page_icon="🪐"               # <-- Put the emoji here
)
# Define these FIRST
PAGE_TITLE = "PROJECT UTOPIA"
PAGE_ICON = "🪐"

# Then run the config
st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon=PAGE_ICON)

# ... imports and the rest of your code ...
# ==========================================
# ⚙️ CONFIGURATION & CONSTANTS
# ==========================================
PAGE_TITLE = "PROJECT UTOPIA"
PAGE_ICON = "🪐"

DATA_FILE = "mission_data.csv"
TODO_FILE = "todo_list.json"
BOOKS_FILE = "library_status.json"
JOURNAL_FILE = "journal_entries.json"

GOAL_MONEY = 400000  # QAR
CURRENCY = "QAR"
GOAL_END_DATE = date(2026, 12, 31)  # end-of-year target horizon

# ----------------------------
# LYRIC BANK
# Keep YOUR existing list here.
# (Not reprinting song lyrics for you.)
# ----------------------------
LYRICS = globals().get("LYRICS", [
    # Put your lyric lines here (or keep your original list).
    "Welcome to Utopia.",
    "Create the wave, don't ride it.",
    "Identify the enemy, then we attack.",
])

# TOXIC MOTIVATION BANK
TOXIC_QUOTES = [
    "You are 19. Zuckerberg had Facebook at 19. You have excuses.",
    "Nobody cares about your potential. They care about your results.",
    "The ZL1 is driving past you right now. Someone else is driving it.",
    "Sleep is the cousin of death. Wake up.",
    "You analyzed the market? Cute. Now sell something.",
    "Your comfort zone is where dreams go to die.",
    "Mediocrity is a disease. You are showing symptoms.",
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
    "Meditations",
]

# THE PODCASTS
REQUIRED_LISTENING = {
    "Alex Hormozi": "The Game (Business Strategy & Acquisition)",
    "Lex Fridman": "Deep Tech, AI & High-Level Discourse",
    "My First Million": "Market Gaps & Business Ideas",
    "Huberman Lab": "Biological Optimization (Sleep/Focus)",
    "Modern Wisdom (Chris Williamson)": "Human Nature, Psychology & Evolution",
}

# ==========================================
# 🛠️ DATA ENGINE
# ==========================================

BASE_COLUMNS = [
    "Date",
    "Cold_Calls",
    "Deep_Work_Hrs",
    "Calories",
    "Workouts",
    "Money_In",
    "Sleep_Hrs",
    "Reading_Pages",
    "Mood",         # 1-5
    "Confidence",   # 1-5
    "Aggression",   # 1-5
    "Notes",
]


def safe_load_json(path, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def safe_save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_files():
    """Initialize data files if they don't exist."""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=BASE_COLUMNS)
        df.to_csv(DATA_FILE, index=False)

    if not os.path.exists(TODO_FILE):
        safe_save_json(TODO_FILE, [])

    if not os.path.exists(BOOKS_FILE):
        books_db = {book: {"status": "Not Started", "progress": 0} for book in REQUIRED_READING}
        safe_save_json(BOOKS_FILE, books_db)

    if not os.path.exists(JOURNAL_FILE):
        safe_save_json(JOURNAL_FILE, [])


def ensure_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Add missing columns safely; keep compatibility with older CSVs."""
    changed = False
    for col in BASE_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col not in ("Date", "Notes") else ""
            changed = True

    # Normalize types
    if not df.empty:
        # Date handling
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        # numeric columns
        num_cols = [c for c in BASE_COLUMNS if c not in ("Date", "Notes")]
        for c in num_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

        df["Notes"] = df["Notes"].fillna("").astype(str)

    if changed:
        df.to_csv(DATA_FILE, index=False)
    return df


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    return ensure_schema(df)


def upsert_log_entry(entry: dict):
    """
    Upsert by Date (1 row per day).
    If date exists, overwrite it. Else append.
    """
    df = load_data()

    entry_date = pd.to_datetime(entry["Date"]).normalize()

    if df.empty:
        out = pd.DataFrame([entry])
        out["Date"] = pd.to_datetime(out["Date"]).dt.normalize()
        ensure_schema(out).to_csv(DATA_FILE, index=False)
        return

    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()

    mask = df["Date"] == entry_date
    if mask.any():
        # overwrite row(s) for that date
        for k, v in entry.items():
            df.loc[mask, k] = v
    else:
        df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)

    df = ensure_schema(df)
    df.to_csv(DATA_FILE, index=False)


init_files()

# ==========================================
# 🧠 HELPER FUNCTIONS (SYSTEM UPGRADE PACK)
# ==========================================

def get_random_lyric():
    return random.choice(LYRICS) if LYRICS else "Silence is also data."


def get_toxic_quote():
    return random.choice(TOXIC_QUOTES)


def last_n_days(df: pd.DataFrame, n: int) -> pd.DataFrame:
    if df.empty:
        return df
    df2 = df.dropna(subset=["Date"]).sort_values("Date")
    cutoff = pd.to_datetime(date.today() - timedelta(days=n - 1))
    return df2[df2["Date"] >= cutoff]


def days_since_last_positive(df: pd.DataFrame, col: str) -> int:
    if df.empty:
        return 10_000
    df2 = df.dropna(subset=["Date"]).sort_values("Date")
    last = df2[df2[col] > 0]["Date"].max()
    if pd.isna(last):
        return 10_000
    return (date.today() - pd.to_datetime(last).date()).days


def consecutive_streak(df: pd.DataFrame, predicate_fn) -> int:
    """
    Count consecutive days (ending today or latest logged date) where predicate is true.
    We treat missing days as breaks. This is discipline, not wishful thinking.
    """
    if df.empty:
        return 0
    df2 = df.dropna(subset=["Date"]).sort_values("Date").copy()
    df2["d"] = df2["Date"].dt.date

    # Work backward from latest logged date (not necessarily today)
    days = list(df2["d"].unique())
    if not days:
        return 0

    streak = 0
    expected = days[-1]

    for d in reversed(days):
        if d != expected:
            break
        row = df2[df2["d"] == d].iloc[-1]
        if predicate_fn(row):
            streak += 1
            expected = expected - timedelta(days=1)
        else:
            break
    return streak


def failure_state(df: pd.DataFrame) -> str:
    """
    CONSEQUENCE ENGINE:
    Evaluate last 7 days. Return CRITICAL/WEAK/STABLE/ASCENDING.
    """
    if df.empty:
        return "CRITICAL"

    w = last_n_days(df, 7)
    if w.empty:
        return "CRITICAL"

    score = 0
    score += (w["Deep_Work_Hrs"].mean() >= 4)
    score += (w["Cold_Calls"].sum() >= 50)
    score += (w["Workouts"].sum() >= 4)
    score += (w["Money_In"].sum() > 0)
    score += (w["Reading_Pages"].sum() >= 50)

    if score <= 1:
        return "CRITICAL"
    elif score <= 2:
        return "WEAK"
    elif score <= 3:
        return "STABLE"
    else:
        return "ASCENDING"


def dominance_score(df: pd.DataFrame) -> float:
    """
    DOMINANCE SCORE (0-100):
    Money 40, Deep Work 25, Cold Calls 15, Fitness 10, Reading 10.
    """
    if df.empty:
        return 0.0

    w = last_n_days(df, 30)
    if w.empty:
        return 0.0

    money = min(w["Money_In"].sum() / 10000, 1) * 40
    deep = min(w["Deep_Work_Hrs"].sum() / 120, 1) * 25
    calls = min(w["Cold_Calls"].sum() / 300, 1) * 15
    fit = min(w["Workouts"].sum() / 20, 1) * 10
    read = min(w["Reading_Pages"].sum() / 600, 1) * 10

    return round(money + deep + calls + fit + read, 1)


def projected_year_end(df: pd.DataFrame, goal_end: date) -> int:
    """
    PREDICTIVE TRAJECTORY:
    total_so_far + avg_daily(last 14) * days_remaining
    """
    if df.empty:
        return 0
    df2 = df.dropna(subset=["Date"]).sort_values("Date")
    total = float(df2["Money_In"].sum())
    w = last_n_days(df2, 14)
    if w.empty:
        return int(total)

    daily_avg = float(w["Money_In"].mean())
    days_remaining = max((goal_end - date.today()).days, 0)
    return int(total + daily_avg * days_remaining)


def adaptive_quote(df: pd.DataFrame) -> str:
    """
    ESCALATING TOXICITY:
    Gets meaner the longer you stall.
    """
    ds = days_since_last_positive(df, "Money_In")

    if ds >= 14:
        return "Two weeks with no revenue. This isn’t bad luck. This is you avoiding work."
    if ds >= 7:
        return "Seven days broke. At this point, you’re practicing failure."
    if ds >= 3:
        return random.choice(TOXIC_QUOTES)
    return "Momentum detected. Don’t get cute. Execute."


def war_mode_lock_dashboard(df: pd.DataFrame) -> bool:
    """
    WAR MODE:
    Dashboard access requires yesterday: Deep Work >= 4 and Cold Calls >= 10.
    Missing log counts as failure.
    """
    if df.empty:
        return True

    y = date.today() - timedelta(days=1)
    df2 = df.dropna(subset=["Date"]).copy()
    df2["d"] = df2["Date"].dt.date

    row = df2[df2["d"] == y]
    if row.empty:
        return True

    r = row.iloc[-1]
    return not (r["Deep_Work_Hrs"] >= 4 and r["Cold_Calls"] >= 10)


def war_mode_lock_arsenal(df: pd.DataFrame) -> bool:
    """
    ARSENAL LOCK:
    If no reading logged in 5 days, lock books tab.
    """
    return days_since_last_positive(df, "Reading_Pages") >= 5


def apply_consequence_css(state: str):
    """
    Visual punishment. Humans respond to pain.
    """
    if state == "CRITICAL":
        css = """
        <style>
          html, body, .stApp { filter: grayscale(1) brightness(0.7) contrast(1.1); }
          .artifact-card { border-color: rgba(239,68,68,0.6) !important; box-shadow: 0 0 25px rgba(239,68,68,0.15) !important; }
          @keyframes pulseRed { 0%{box-shadow:0 0 15px rgba(239,68,68,.15);} 50%{box-shadow:0 0 35px rgba(239,68,68,.25);} 100%{box-shadow:0 0 15px rgba(239,68,68,.15);} }
          .artifact-card { animation: pulseRed 2.2s infinite; }
        </style>
        """
    elif state == "WEAK":
        css = """
        <style>
          html, body, .stApp { filter: brightness(0.85); }
          .artifact-card { border-color: rgba(245,158,11,0.35) !important; }
        </style>
        """
    elif state == "ASCENDING":
        css = """
        <style>
          .artifact-card { border-color: rgba(168,85,247,0.45) !important; box-shadow: 0 0 30px rgba(168,85,247,0.12) !important; }
        </style>
        """
    else:
        css = "<style></style>"

    st.markdown(css, unsafe_allow_html=True)




# JS lyric rotation
lyrics_json = json.dumps(LYRICS)
st.markdown(
    f"""
<script>
  const lyrics = {lyrics_json};
  function updateLyric() {{
    const el = document.getElementById('lyric-display');
    if (el && lyrics && lyrics.length) {{
      const randomLyric = lyrics[Math.floor(Math.random() * lyrics.length)];
      el.style.opacity = 0;
      setTimeout(() => {{
        el.innerHTML = "🎧 " + randomLyric;
        el.style.opacity = 0.85;
      }}, 250);
    }}
  }}
  setInterval(updateLyric, 60000);
  setTimeout(updateLyric, 500);
</script>
""",
    unsafe_allow_html=True,
)

# Base CSS (your original look, kept, lightly extended)
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
  background-color: #050505;
  color: #e0e0e0;
  overflow-x: hidden;
}

.stApp {
  background: radial-gradient(circle at 50% -20%, #2e003e 0%, #000000 50%),
              radial-gradient(circle at 80% 80%, #1a0b2e 0%, #000000 40%);
  background-attachment: fixed;
}

.artifact-card {
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
}

.artifact-card:hover {
  transform: perspective(1000px) rotateX(2deg) translateY(-5px);
  box-shadow: 0 20px 40px -10px rgba(168, 85, 247, 0.2);
  border-color: rgba(168, 85, 247, 0.5);
}

.artifact-card::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
  transition: 0.5s;
}
.artifact-card:hover::before { left: 100%; }

h1 {
  font-family: 'Syncopate', sans-serif;
  font-weight: 700;
  letter-spacing: -2px;
  background: linear-gradient(180deg, #fff, #888);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 4rem !important;
  text-shadow: 0 0 30px rgba(255,255,255,0.1);
}
h2, h3 {
  font-family: 'Syncopate', sans-serif;
  color: #fff;
  font-weight: 700;
  letter-spacing: 1px;
}

#lyric-display {
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
}

div[data-testid="stMetricValue"] {
  font-family: 'Syncopate', sans-serif;
  font-size: 34px;
  color: #fff;
  text-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
}
div[data-testid="stMetricLabel"] {
  color: #9ca3af;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 2px;
}

.stTextInput > div > div, .stNumberInput > div > div, .stTextArea > div > div {
  background-color: rgba(0, 0, 0, 0.3);
  border: 1px solid #333;
  color: white;
  border-radius: 8px;
}

.stTextInput > div > div:focus-within {
  border-color: #d8b4fe;
  box-shadow: 0 0 15px rgba(216, 180, 254, 0.2);
}

.stButton > button {
  background: #000;
  border: 1px solid #d8b4fe;
  color: #d8b4fe;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  font-family: 'Syncopate', sans-serif;
  font-weight: 700;
  transition: all 0.3s ease;
  text-transform: uppercase;
}
.stButton > button:hover {
  background: #d8b4fe;
  color: #000;
  box-shadow: 0 0 20px rgba(216, 180, 254, 0.6);
}

.stTabs [data-baseweb="tab"] {
  font-family: 'Syncopate', sans-serif;
  font-size: 12px;
  background-color: rgba(255,255,255,0.02);
}
.stTabs [aria-selected="true"] {
  background-color: rgba(168, 85, 247, 0.1) !important;
  border: 1px solid #a855f7 !important;
  color: #a855f7 !important;
}

.badge {
  display:inline-block;
  padding: 6px 10px;
  border: 1px solid rgba(216,180,254,0.4);
  border-radius: 999px;
  font-size: 11px;
  letter-spacing: 1px;
  color: #d8b4fe;
  background: rgba(0,0,0,0.25);
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 🏠 MAIN LAYOUT + SYSTEM CORE
# ==========================================
df = load_data()
state = failure_state(df)


# sidebar controls (no sugarcoat but you might want to disable locks while testing)
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM CONTROL")
    WAR_MODE = st.toggle("WAR MODE (LOCKS)", value=True)
    CONSEQUENCE_VISUALS = st.toggle("CONSEQUENCE VISUALS", value=True)
    if not CONSEQUENCE_VISUALS:
        st.markdown("<style>html, body, .stApp { filter:none !important; }</style>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"**STATE:** `{state}`")
    st.markdown(f"<span class='badge'>DOMINANCE {dominance_score(df)}</span>", unsafe_allow_html=True)

# HEADER
c_head1, c_head2 = st.columns([4, 1])
with c_head1:
    st.markdown("<h1>PROJECT UTOPIA</h1>", unsafe_allow_html=True)
    st.markdown(f"<div id='lyric-display'>🎧 {get_random_lyric()}</div>", unsafe_allow_html=True)

with c_head2:
    st.write("")
    st.write("")
    if st.button("💀 REALITY CHECK"):
        st.toast(adaptive_quote(df), icon="⚡")

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
# 📊 TAB 1: DASHBOARD (UPGRADED)
# ==========================================
with tab_dash:
    df = load_data()
    total_money = df["Money_In"].sum() if not df.empty else 0.0
    money_remaining = GOAL_MONEY - total_money
    progress_pct = min(total_money / GOAL_MONEY, 1.0)

    # Trajectory + prediction
    days_left = max((GOAL_END_DATE - date.today()).days, 0)
    projection = projected_year_end(df, GOAL_END_DATE)
    proj_delta = "ON COURSE" if projection >= GOAL_MONEY else "FAILURE TRAJECTORY"

    # Streaks
    revenue_streak = consecutive_streak(df, lambda r: r["Money_In"] > 0)
    discipline_streak = consecutive_streak(df, lambda r: (r["Deep_Work_Hrs"] >= 4 and r["Cold_Calls"] >= 10))
    reading_gap = days_since_last_positive(df, "Reading_Pages")
    revenue_gap = days_since_last_positive(df, "Money_In")

    dashboard_locked = WAR_MODE and war_mode_lock_dashboard(df)

    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown(f"### 🎯 TARGET: {GOAL_MONEY:,.0f} {CURRENCY}")
    st.progress(progress_pct)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("LIQUID CASH", f"{total_money:,.0f}", delta=CURRENCY)
    m2.metric("REMAINING", f"{money_remaining:,.0f}", delta_color="inverse")
    m3.metric("TIME REMAINING", f"{days_left} DAYS", delta="HURRY UP")
    m4.metric("DOMINANCE INDEX", dominance_score(df), delta="MONTHLY")
    m5.metric("PROJECTED YEAR-END", f"{projection:,.0f}", delta=proj_delta)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("REVENUE STREAK", f"{revenue_streak} days")
    s2.metric("DISCIPLINE STREAK", f"{discipline_streak} days")
    s3.metric("DAYS SINCE REVENUE", f"{revenue_gap}")
    s4.metric("DAYS SINCE READING", f"{reading_gap}")
    st.markdown("</div>", unsafe_allow_html=True)

    # WAR MODE LOCK SCREEN
    if dashboard_locked:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.error("WAR MODE ACTIVE. DASHBOARD ACCESS DENIED.")
        st.markdown("**Unlock condition:** Yesterday must have **Deep Work ≥ 4 hours** AND **Cold Calls ≥ 10**. Missing log counts as failure.")
        st.markdown("Go to **📝 LOGS** and fix your record.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Charts
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 📈 TRAJECTORY ARTIFACT")
        if not df.empty:
            chart_df = df.dropna(subset=["Date"]).sort_values("Date").copy()
            chart_df["cum_money"] = chart_df["Money_In"].cumsum()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=chart_df["Date"], y=chart_df["Money_In"],
                fill="tozeroy", mode="lines+markers", name="Daily Revenue",
                line=dict(color="#d8b4fe", width=3),
                marker=dict(size=7, color="#fff", line=dict(width=2, color="#d8b4fe")),
            ))
            fig.add_trace(go.Scatter(
                x=chart_df["Date"], y=chart_df["cum_money"],
                mode="lines", name="Cumulative",
                line=dict(color="rgba(255,255,255,0.35)", width=2, dash="dot"),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ccc", family="Inter"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                height=340,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("NO DATA. SYSTEM WAITING.")
        st.markdown("</div>", unsafe_allow_html=True)

        # Identity Drift
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.markdown("### 🧬 IDENTITY DRIFT (Mood / Confidence / Aggression)")
        if not df.empty:
            id_df = df.dropna(subset=["Date"]).sort_values("Date").copy()
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=id_df["Date"], y=id_df["Mood"], mode="lines+markers", name="Mood"))
            fig2.add_trace(go.Scatter(x=id_df["Date"], y=id_df["Confidence"], mode="lines+markers", name="Confidence"))
            fig2.add_trace(go.Scatter(x=id_df["Date"], y=id_df["Aggression"], mode="lines+markers", name="Aggression"))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ccc", family="Inter"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", range=[0, 5.2]),
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("NO IDENTITY SIGNALS YET.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 📓 TAB 2: JOURNAL (UPGRADED)
# ==========================================
with tab_journal:
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown("### 🧠 MIND DUMP")
    st.markdown("Write freely. Clear the noise. Strategize.")

    with st.form("journal_form", clear_on_submit=True):
        j_title = st.text_input("Entry Title", placeholder="e.g., The Vision for March...")
        j_content = st.text_area("Content", height=200, placeholder="Pour it out...")
        j_tag = st.text_input("Tag (optional)", placeholder="e.g., discipline / money / relationships / school")
        j_submit = st.form_submit_button("SAVE TO ARCHIVE")

        if j_submit and j_title and j_content:
            entries = safe_load_json(JOURNAL_FILE, [])
            new_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "title": j_title.strip(),
                "tag": j_tag.strip(),
                "content": j_content.strip(),
            }
            entries.insert(0, new_entry)
            safe_save_json(JOURNAL_FILE, entries)
            st.success("ENTRY ARCHIVED.")

    st.markdown("</div>", unsafe_allow_html=True)

    entries = safe_load_json(JOURNAL_FILE, [])
    if entries:
        for ent in entries:
            tag = f" • #{ent.get('tag','')}" if ent.get("tag") else ""
            with st.expander(f"📓 {ent['timestamp']} | {ent['title']}{tag}"):
                st.markdown(ent["content"])
    else:
        st.info("The archive is empty.")

# ==========================================
# 📝 TAB 3: LOGS (UPGRADED: IDENTITY LOGGING)
# ==========================================
with tab_log:
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown("### 📝 TACTICAL INPUT (1 ENTRY PER DAY)")

    with st.form("main_log_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1.1, 1.1, 1.2])
        with c1:
            l_date = st.date_input("Date", date.today())
            l_calls = st.number_input("Cold Calls", min_value=0, step=1)
            l_money = st.number_input("Money In", min_value=0.0, step=50.0)
            l_deep = st.number_input("Deep Work (Hrs)", min_value=0.0, step=0.5)
        with c2:
            l_cal = st.number_input("Calories", min_value=0, step=50)
            l_sleep = st.number_input("Sleep (Hrs)", min_value=0.0, step=0.5)
            l_read = st.number_input("Pages Read", min_value=0, step=5)
            l_workout = st.checkbox("Workout Done?")
        with c3:
            st.markdown("#### 🧬 Identity Signals")
            l_mood = st.slider("Mood", 1, 5, 3)
            l_conf = st.slider("Confidence", 1, 5, 3)
            l_aggr = st.slider("Aggression", 1, 5, 3)
            l_notes = st.text_input("Short Note")

        if st.form_submit_button("LOG DATA"):
            upsert_log_entry({
                "Date": pd.to_datetime(l_date),
                "Cold_Calls": int(l_calls),
                "Deep_Work_Hrs": float(l_deep),
                "Calories": int(l_cal),
                "Workouts": 1 if l_workout else 0,
                "Money_In": float(l_money),
                "Sleep_Hrs": float(l_sleep),
                "Reading_Pages": int(l_read),
                "Mood": int(l_mood),
                "Confidence": int(l_conf),
                "Aggression": int(l_aggr),
                "Notes": str(l_notes),
            })
            st.toast("LOGGED (UPSERTED).", icon="💾")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    df = load_data()
    if not df.empty:
        show_df = df.copy()
        show_df["Date"] = pd.to_datetime(show_df["Date"]).dt.date
        st.dataframe(show_df.sort_values("Date", ascending=False), use_container_width=True)
    else:
        st.info("NO LOGS YET. START.")

# ==========================================
# ✅ TAB 4: OPS (TASKS)
# ==========================================
with tab_tasks:
    st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
    st.markdown("### ⚔️ DIRECTIVES")

    todos = safe_load_json(TODO_FILE, [])

    col_in, col_btn = st.columns([4, 1])
    with col_in:
        new_task = st.text_input("New Task", placeholder="Execute order...", label_visibility="collapsed")
    with col_btn:
        if st.button("ADD"):
            if new_task:
                todos.append({
                    "task": new_task.strip(),
                    "done": False,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                safe_save_json(TODO_FILE, todos)
                st.rerun()

    if todos:
        for i, todo in enumerate(todos):
            label = f"{todo['task']}  ·  ({todo.get('created','')})"
            done = st.checkbox(label, value=todo.get("done", False), key=f"t_{i}")
            if done != todo.get("done", False):
                todos[i]["done"] = done
                safe_save_json(TODO_FILE, todos)
                st.rerun()

        if st.button("PURGE COMPLETED"):
            todos = [t for t in todos if not t.get("done", False)]
            safe_save_json(TODO_FILE, todos)
            st.rerun()
    else:
        st.markdown("*No active directives.*")

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 📚 TAB 5: ARSENAL (LOCKED IF YOU NEGLECT READING)
# ==========================================
with tab_arsenal:
    df = load_data()
    locked = WAR_MODE and war_mode_lock_arsenal(df)

    if locked:
        st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
        st.error("ARSENAL LOCKED.")
        st.markdown("No reading logged in **5 days**. Unlock by logging **Reading Pages > 0** in **📝 LOGS**.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        c_b, c_p = st.columns(2)

        with c_b:
            st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
            st.markdown("### 📘 CODEX (BOOKS)")

            books = safe_load_json(BOOKS_FILE, {})
            # ensure all exist
            for title in REQUIRED_READING:
                if title not in books:
                    books[title] = {"status": "Not Started", "progress": 0}

            for title in REQUIRED_READING:
                b = books[title]
                with st.expander(f"{title} ({b.get('progress',0)}%)"):
                    s = st.selectbox(
                        "Status",
                        ["Not Started", "Reading", "Done"],
                        key=f"s_{title}",
                        index=["Not Started", "Reading", "Done"].index(b.get("status", "Not Started"))
                        if b.get("status", "Not Started") in ["Not Started", "Reading", "Done"]
                        else 0
                    )
                    p = st.slider("Progress", 0, 100, int(b.get("progress", 0)), key=f"p_{title}")
                    if s != b.get("status") or p != b.get("progress"):
                        books[title] = {"status": s, "progress": p}
                        safe_save_json(BOOKS_FILE, books)
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        with c_p:
            st.markdown("<div class='artifact-card'>", unsafe_allow_html=True)
            st.markdown("### 🎙️ SIGNAL INTERCEPT (PODCASTS)")
            for name, desc in REQUIRED_LISTENING.items():
                st.markdown(
                    f"""
                    <div style='margin-bottom: 15px; border-left: 2px solid #d8b4fe; padding-left: 10px;'>
                      <div style='font-weight: 700; color: #fff;'>{name}</div>
                      <div style='font-size: 12px; color: #888;'>{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 🗺️ TAB 6: PLAN (UNCHANGED STRUCTURE, MORE AUTHORITY)
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

    st.markdown("---")
    st.markdown("### 🧨 SYSTEM DIRECTIVE (AUTO)")
    # Simple “orders” generated from your deficits (no AI API needed)
    orders = []
    w7 = last_n_days(load_data(), 7)
    if w7.empty or w7["Money_In"].sum() <= 0:
        orders.append("Log revenue today (even if small). No income logged = fantasy life.")
    if w7.empty or w7["Cold_Calls"].sum() < 50:
        orders.append("Cold outreach to hit 50/week. No calls = no pipeline.")
    if w7.empty or w7["Deep_Work_Hrs"].mean() < 4:
        orders.append("Minimum 4 hours deep work/day. Stop negotiating with yourself.")
    if w7.empty or w7["Workouts"].sum() < 4:
        orders.append("Train 4x/week. Your body is part of the business machine.")
    if w7.empty or w7["Reading_Pages"].sum() < 50:
        orders.append("Read 50 pages/week. Your brain shouldn’t rot for free.")

    if not orders:
        orders = ["Maintain pace. Raise targets next week. Comfort is illegal."]

    for o in orders[:5]:
        st.markdown(f"- {o}")

    st.markdown("</div>", unsafe_allow_html=True)
