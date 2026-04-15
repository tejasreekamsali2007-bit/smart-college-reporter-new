# ============================================================
#  Smart College Problem Reporter  |  app.py
#  Run:  streamlit run app.py
# ============================================================

import streamlit as st
import json
import sqlite3

# ─────────────────────────────────────────────
#  ★  CREDENTIALS — Edit here to add/remove users
# ─────────────────────────────────────────────

ADMIN_CREDENTIALS = {
    "admin":       "admin123",
    "mrecw":       "mrewc123",
    "hod":         "hod123",
}

STUDENT_CREDENTIALS = {
    "25RH1A05W2":    "25RH1A05W2",
    "25RH1A05X1":    "25RH1A05X1",
    "25RH1A05X6":    "25RH1A05X6",
    "25RH1A05Y1":    "25RH1A05Y1",
    "25RH1A05Y6":    "25RH1A05Y6",
}

# ─────────────────────────────────────────────
# DATABASE FUNCTIONS
# ─────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT PRIMARY KEY,
        type TEXT,
        location TEXT,
        description TEXT,
        priority TEXT,
        date TEXT,
        status TEXT,
        student TEXT,
        accepted TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_complaints():
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("SELECT * FROM complaints")
    rows = c.fetchall()
    conn.close()

    complaints = []
    for r in rows:
        complaints.append({
            "id": r[0],
            "type": r[1],
            "location": r[2],
            "description": r[3],
            "priority": r[4],
            "date": r[5],
            "status": r[6],
            "student": r[7],
            "accepted": r[8] if len(r) > 8 else None,
        })
    return complaints


def get_next_complaint_id():
    """Generate a unique complaint ID based on the database state."""
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM complaints")
    count = c.fetchone()[0]
    conn.close()
    return f"#{count + 101}"


def add_complaint(complaint_data):
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    # Check number of columns in table
    c.execute("PRAGMA table_info(complaints)")
    columns = c.fetchall()
    col_count = len(columns)

    if col_count == 9:
        # New table (with accepted column)
        c.execute("""
        INSERT INTO complaints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint_data["id"],
            complaint_data["type"],
            complaint_data["location"],
            complaint_data["description"],
            complaint_data["priority"],
            complaint_data["date"],
            complaint_data["status"],
            complaint_data["student"],
            complaint_data["accepted"]
        ))
    else:
        # Old table (without accepted column)
        c.execute("""
        INSERT INTO complaints VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint_data["id"],
            complaint_data["type"],
            complaint_data["location"],
            complaint_data["description"],
            complaint_data["priority"],
            complaint_data["date"],
            complaint_data["status"],
            complaint_data["student"]
        ))

    conn.commit()
    conn.close()


def update_complaint_status(complaint_id, status, accepted=None):
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()
    
    if accepted is not None:
        c.execute("""
        UPDATE complaints
        SET status = ?, accepted = ?
        WHERE id = ?
        """, (status, accepted, complaint_id))
    else:
        c.execute("""
        UPDATE complaints
        SET status = ?
        WHERE id = ?
        """, (status, complaint_id))
    
    conn.commit()
    conn.close()
# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Smart College Problem Reporter",
    page_icon="🎓",
    layout="centered",
)


# ─────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────
def load_styles():
    st.markdown("""
    <style>
    h1 {
    color: black !important;
    font-size: 4rem !important;
}

    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

    /* DARKER BACKGROUND */
    .stApp { 
        background: linear-gradient(f4f7ff);
    }

    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 960px; }

    /* HEADER - STRONG CONTRAST */
    .app-header {
    background: transparent !important;
    box-shadow: none !important;
    padding: 0;
    text-align: center;

    }
    .main-tittle {
    font-size: 4rem !important;   /* BIG TITLE */
    font-weight: 900;
    color: #000000 !important;    /* BLACK TEXT */
    margin: 20px 0;
    }
    .app-header h1{
        font-size: 3.5rem;      /* 🔼 bigger */
        font-weight: 900;
        color: #000000;         /* ⚫ black text */
        margin-top: 10px;
    }
    .app-header p {
    color: #ADD8E6;   /* darker subtitle */
    font-size: 1.5rem;
    }

   

    .login-title, .card-title {
        text-align: center;
        margin-bottom: 15px;
        color: #1e4d8c !important;
        font-weight: 900;
        font-size: 4rem;
    }

    .login-subtitle, .card-subtitle {
        color: #555;
    }

    /* BUTTONS - MORE VISIBLE */
    div[data-testid="stButton"] > button {
        background: #38bdf8;
        border: 2px solid #1e4d8c;
        color: #0d2b5e;
        border-radius: 12px;
        font-weight: 700;
    }

    div[data-testid="stButton"] > button:hover {
        background: #1e4d8c;
        color: #ffffff;
    }

    /* PRIMARY BUTTON */
    .blue-btn > div[data-testid="stButton"] > button {
        background: #1e4d8c !important;
        color: #fff !important;
        border: none !important;
    }

    /* GREEN BUTTON */
    .green-btn > div[data-testid="stButton"] > button {
        background: #2a9d3a !important;
        color: #fff !important;
        border: none !important;
    }

    /* RED BUTTON */
    .red-btn > div[data-testid="stButton"] > button {
        background: #c0392b !important;
        color: #fff !important;
        border: none !important;
    }

    /* TEXT FIXES */
    .card p, .card h1, .card h2, .card h3, .card h4 {
    color: #111 !important;
}
  

    /* TABLE VISIBILITY */
    table.cmp-table th {
        background: #1e4d8c;
        color: #ffffff;
    }

    table.cmp-table td {
        background: #ffffff;
        color: #111;
    }

    table.cmp-table tr:hover td {
        background: #eef4ff;
    }
    header[data-testid="stHeader"]{
    background: transparent !important}

    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "page":           "login",
        "role":           None,
        "username":       "",
        "issue_type":     "",
        "complaints":     [],
        "admin_tab":      "dashboard",   # "dashboard" | "complaints"
        "cmp_page":       0,             # pagination for complaints table
        "view_complaint": None,          # id of complaint being viewed
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    st.session_state.complaints = get_complaints()
# ─────────────────────────────────────────────
#  NAVIGATION
# ─────────────────────────────────────────────
def go(page, issue_type=""):
    st.session_state.page       = page
    st.session_state.issue_type = issue_type
    st.rerun()


# ─────────────────────────────────────────────
#  SHARED COMPONENTS
# ─────────────────────────────────────────────
def render_header():
    role_label = "Admin Panel" if st.session_state.role == "admin" else "Student Portal"
    st.markdown(f"""
    <div class="app-header">
        <div style="font-size:2rem;">🎓</div>
        <div style="flex:1;">
            <h1 class="main-tittle">Smart College Problem Reporter</h1>
            <p>Report campus issues instantly to management</p>
        </div>
        <div style="text-align:right; font-size:.78rem; opacity:.85;">
            👤 {st.session_state.username}<br>
            <span style="font-size:.7rem; background:rgba(255,255,255,.15);
                        padding:2px 8px; border-radius:99px;">{role_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def logout_button():
    st.markdown('<div class="red-btn">', unsafe_allow_html=True)
    if st.button("🚪  Log Out"):
        for k in ["role", "username", "issue_type"]:
            st.session_state[k] = None if k == "role" else ""
        st.session_state.page = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def back_button(label="← Back to Home", dest="home"):
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button(label):
        go(dest)
    st.markdown('</div>', unsafe_allow_html=True)


def badge_html(status):
    cls = {
        "Resolved":    "badge-green",
        "In Progress": "badge-amber",
        "Pending":     "badge-red",
        "Accepted":    "badge-blue",
        "Declined":    "badge-red",
    }.get(status, "badge-amber")
    return f'<span class="badge {cls}">{status}</span>'


# ─────────────────────────────────────────────
#  PAGE 0 — LOGIN
# ─────────────────────────────────────────────
def page_login():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-icon">🎓</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:40px";class="login-title"><B>SMART COLLEGE PROBLEM REPORTER</B></p>', unsafe_allow_html=True)

    role = st.radio(
        "Login as",
        ["🎒  Student", "🛡️  Administration"],
        horizontal=True,
        label_visibility="collapsed",
    )
    is_admin = "Administration" in role

    st.markdown(
        f'<p class="login-subtitle">'
        f'{"Administration login — restricted access" if is_admin else "Student login — report campus issues"}'
        f'</p>',
        unsafe_allow_html=True,
    )

    username = st.text_input("👤  Username", placeholder="Enter your username")
    password = st.text_input("🔒  Password", type="password", placeholder="Enter your password")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="blue-btn">', unsafe_allow_html=True)
    login_clicked = st.button("Log In", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if login_clicked:
        uname = username.strip()
        pwd   = password.strip()
        if not uname or not pwd:
            st.error("⚠️  Please enter both username and password.")
        elif is_admin:
            if ADMIN_CREDENTIALS.get(uname) == pwd:
                st.session_state.role     = "admin"
                st.session_state.username = uname
                st.session_state.admin_tab = "dashboard"
                go("admin_dashboard")
            else:
                st.error("❌  Invalid admin credentials.")
        else:
            if STUDENT_CREDENTIALS.get(uname) == pwd:
                st.session_state.role     = "student"
                st.session_state.username = uname
                go("home")
            else:
                st.error("❌  Invalid student credentials.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="app-footer">
        Fast Reporting <span>•</span> Quick Resolution <span>•</span> Enhanced Campus Management
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 1 — STUDENT HOME
# ─────────────────────────────────────────────
def page_home():
    render_header()
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col_title, col_logout = st.columns([3, 1])
    with col_title:
        st.markdown(
            f'<p class="card-title">Welcome, {st.session_state.username.capitalize()}! 👋</p>',
            unsafe_allow_html=True,
        )
        st.markdown('<p class="card-subtitle">Select the type of issue you want to report</p>', unsafe_allow_html=True)
    with col_logout:
        logout_button()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💻  Computer Issue\n\nPC or Lab Problems"):
            go("report", "Computer Issue")
        if st.button("📺  Board / Projector Issue\n\nSmart Board Problems"):
            go("report", "Board / Projector Issue")
    with col2:
        if st.button("🔏  Biometric Issue\n\nFingerprint Scanner Issues"):
            go("report", "Biometric Issue")
        if st.button("📶  Network Issue\n\nInternet / Wi-Fi Problems"):
            go("report", "Network Issue")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="blue-btn">', unsafe_allow_html=True)
        if st.button("📋  My Complaints", use_container_width=True):
            go("complaints")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="green-btn">', unsafe_allow_html=True)
        if st.button("📍  Track Status  ✅", use_container_width=True):
            go("track")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="app-footer">
        Fast Reporting <span>•</span> Quick Resolution <span>•</span> Enhanced Campus Management
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 2 — REPORT AN ISSUE
# ─────────────────────────────────────────────
ISSUE_TYPES = [
    "Computer Issue",
    "Biometric Issue",
    "Board / Projector Issue",
    "Network Issue",
    "Other",
]

def page_report():
    render_header()
    st.markdown('<div class="card">', unsafe_allow_html=True)
    back_button()

    st.markdown('<p class="card-title">📝 Report an Issue</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="card-subtitle">Category: '
        f'<strong style="color:#185FA5">{st.session_state.issue_type}</strong></p>',
        unsafe_allow_html=True,
    )

    with st.form("report_form", clear_on_submit=True):
        location = st.text_input("📍 Location *", placeholder="e.g. Block C, Lab 204")
        col1, col2 = st.columns(2)
        with col1:
            default_idx = (
                ISSUE_TYPES.index(st.session_state.issue_type)
                if st.session_state.issue_type in ISSUE_TYPES else 0
            )
            issue_type = st.selectbox("🔧 Issue Type *", ISSUE_TYPES, index=default_idx)
        with col2:
            priority = st.selectbox("⚡ Priority", ["Medium", "Low", "High"])

        description = st.text_area(
            "📄 Description *",
            placeholder="Describe the problem clearly — what happened, where, and since when…",
            height=120,
        )
        st.file_uploader(
            "📷 Upload Image  (optional — PNG / JPG, max 10 MB)",
            type=["png", "jpg", "jpeg"],
        )
        submitted = st.form_submit_button("🚀 Submit Complaint", use_container_width=True)

    if submitted:
        if not location.strip() or not description.strip():
            st.error("⚠️  Please fill in both Location and Description.")
        else:
            cid = get_next_complaint_id()
            complaint_data = {
                "id": cid,
                "type": issue_type,
                "location": location.strip(),
                "description": description.strip(),
                "priority": priority,
                "date": "Today",
                "status": "Pending",
                "student": st.session_state.username,
                "accepted": None
            }
            
            add_complaint(complaint_data)
            
            st.success(f"✅ Complaint **{cid}** submitted! Our team will respond within 24–48 hours.")
            st.balloons()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE 3 — MY COMPLAINTS
# ─────────────────────────────────────────────
def page_complaints():
    render_header()
    st.markdown('<div class="card">', unsafe_allow_html=True)
    back_button()

    st.markdown('<p class="card-title">📋 My Complaints</p>', unsafe_allow_html=True)
    st.markdown('<p class="card-subtitle">All your submitted complaints and their current status</p>', unsafe_allow_html=True)

    my_complaints = [
        c for c in st.session_state.complaints
        if c.get("student") == st.session_state.username
    ]

    if not my_complaints:
        st.info("No complaints submitted yet. Go to Home to report an issue.")
    else:
        for c in my_complaints:
            st.markdown(f"""
            <div class="complaint-row">
                <div>
                    <h4>{c['type']}
                        <span style="font-size:.75rem;color:#aaa;margin-left:6px;">{c['id']}</span>
                    </h4>
                    <p>📍 {c['location']} &nbsp;·&nbsp; 🗓 {c['date']}</p>
                </div>
                {badge_html(c['status'])}
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 4 — TRACK STATUS
# ─────────────────────────────────────────────
STEP_LABELS = ["Complaint submitted", "Assigned to technician", "Issue resolved"]
TRACK_STEPS = {
    "Pending":     [True,  False, False],
    "In Progress": [True,  True,  False],
    "Resolved":    [True,  True,  True ],
}

def render_timeline(status):
    done_flags = TRACK_STEPS.get(status, [True, False, False])
    for label, done in zip(STEP_LABELS, done_flags):
        dot_class = "step-dot-done"  if done else "step-dot-pending"
        symbol    = "✓"              if done else "·"
        weight    = "700"            if done else "400"
        color     = "#1a3a6b"        if done else "#aaa"
        st.markdown(f"""
        <div class="step-row">
            <div class="{dot_class}">{symbol}</div>
            <span style="font-size:.9rem; font-weight:{weight}; color:{color};">{label}</span>
        </div>""", unsafe_allow_html=True)


def page_track():
    render_header()
    st.markdown('<div class="card">', unsafe_allow_html=True)
    back_button()

    st.markdown('<p class="card-title">📍 Track Complaint Status</p>', unsafe_allow_html=True)
    st.markdown('<p class="card-subtitle">Enter your complaint ID to see live progress</p>', unsafe_allow_html=True)

    cmp_id = st.text_input("Complaint ID", placeholder="e.g. #101").strip()

    if st.button("🔍  Search", use_container_width=True):
        if not cmp_id:
            st.warning("Please enter a complaint ID.")
        else:
            match = next(
                (c for c in st.session_state.complaints
                 if c["id"] == cmp_id and c.get("student") == st.session_state.username),
                None,
            )
            if match is None:
                st.error(f"❌ '{cmp_id}' not found. Please check the complaint ID from 'My Complaints'.")
            else:
                st.markdown(f"""
                <div style="background:#f4f8ff; border:1px solid #cde0f5;
                            border-radius:12px; padding:16px; margin-bottom:1rem;">
                    <p style="font-weight:700; color:#1a3a6b; margin:0 0 4px;">
                        {match['type']}
                        <span style="font-size:.78rem; color:#aaa; margin-left:6px;">{match['id']}</span>
                    </p>
                    <p style="font-size:.82rem; color:#6b7a99; margin:0 0 14px;">
                        📍 {match['location']} &nbsp;·&nbsp; Status: {match['status']}
                    </p>
                """, unsafe_allow_html=True)
                render_timeline(match["status"])
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ADMIN — DASHBOARD TAB (stats + charts)
# ─────────────────────────────────────────────
def render_admin_dashboard_tab():
    all_c = st.session_state.complaints
    total    = len(all_c)
    resolved = sum(1 for c in all_c if c["status"] == "Resolved")
    progress = sum(1 for c in all_c if c["status"] == "In Progress")
    # Simulate avg response time
    avg_resp = "2.5 hrs"

    # ── Stat cards ──
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:1.6rem;">
        <div class="stat-card" style="background:#1e4d8c; color:#fff;">
            <div class="stat-icon">📋</div>
            <div class="stat-value">{total}</div>
            <div class="stat-label">Total Complaints</div>
        </div>
        <div class="stat-card" style="background:#2a9d3a; color:#fff;">
            <div class="stat-icon">✅</div>
            <div class="stat-value">{resolved}</div>
            <div class="stat-label">Resolved Issues</div>
        </div>
        <div class="stat-card" style="background:#e67e22; color:#fff;">
            <div class="stat-icon">⏳</div>
            <div class="stat-value">{progress}</div>
            <div class="stat-label">Issues In Progress</div>
        </div>
        <div class="stat-card" style="background:#c0392b; color:#fff;">
            <div class="stat-icon">⏱️</div>
            <div class="stat-value">{avg_resp}</div>
            <div class="stat-label">Avg. Response Time</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts row ──
    # Count by type
    type_counts = {}
    for c in all_c:
        t = c["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    # Monthly trend — simulate with static + real total
    months_labels = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
    months_data   = [34, 29, 41, 45, 65, max(total, 0)]

    # Serialize for JS
    tc_labels = list(type_counts.keys()) or ["Computer Issue", "Network Issue", "Biometric Issue", "Board / Projector Issue"]
    tc_values = list(type_counts.values()) or [51, 30, 22, 21]
    colors_pie = ["#1e4d8c", "#e67e22", "#2a9d3a", "#c0392b", "#8e44ad"]

    chart_data = json.dumps({
        "months": months_labels,
        "trend":  months_data,
        "pie_labels": tc_labels,
        "pie_values": tc_values,
        "colors": colors_pie[:len(tc_labels)],
    })

    st.components.v1.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Nunito', sans-serif; }}
      body {{ background: transparent; padding: 0; }}
      .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
      .chart-card {{
        background: #fff; border: 1px solid #e0eaf8; border-radius: 14px; padding: 16px;
      }}
      .chart-title {{ font-size: 14px; font-weight: 800; color: #1a3a6b; margin-bottom: 12px; }}
      .legend {{ display: flex; flex-direction: column; gap: 6px; margin-top: 12px; font-size: 12px; color: #555; }}
      .legend-row {{ display: flex; align-items: center; justify-content: space-between; gap: 6px; }}
      .leg-dot {{ width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }}
    </style>
    </head>
    <body>
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-title">Complaints Trend</div>
        <div style="position:relative; height:200px;">
          <canvas id="trendChart" role="img" aria-label="Bar chart of monthly complaint trends">Monthly complaint trend data.</canvas>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Issues Breakdown</div>
        <div style="position:relative; height:180px;">
          <canvas id="pieChart" role="img" aria-label="Donut chart of issue type breakdown">Issue type breakdown.</canvas>
        </div>
        <div class="legend" id="pieLegend"></div>
      </div>
    </div>

    <script>
    const d = {chart_data};

    // Trend bar chart
    new Chart(document.getElementById('trendChart'), {{
      type: 'bar',
      data: {{
        labels: d.months,
        datasets: [{{
          label: 'Complaints',
          data: d.trend,
          backgroundColor: d.months.map((_, i) => i === d.months.length - 2 ? '#2a9d3a' : '#1e4d8c'),
          borderRadius: 6,
        }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          y: {{ beginAtZero: true, ticks: {{ font: {{ size: 11 }} }}, grid: {{ color: '#f0f0f0' }} }},
          x: {{ ticks: {{ font: {{ size: 11 }} }}, grid: {{ display: false }} }}
        }}
      }}
    }});

    // Donut pie chart
    new Chart(document.getElementById('pieChart'), {{
      type: 'doughnut',
      data: {{
        labels: d.pie_labels,
        datasets: [{{
          data: d.pie_values,
          backgroundColor: d.colors,
          borderWidth: 2,
          borderColor: '#fff',
        }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{
          label: (ctx) => ` ${{ctx.label}}: ${{ctx.parsed}}`
        }} }} }},
        cutout: '55%',
      }}
    }});

    // Custom legend
    const leg = document.getElementById('pieLegend');
    const total = d.pie_values.reduce((a,b) => a+b, 0);
    d.pie_labels.forEach((lbl, i) => {{
      const pct = total > 0 ? ((d.pie_values[i]/total)*100).toFixed(1) : '0';
      const row = document.createElement('div');
      row.className = 'legend-row';
      row.innerHTML = `<div style="display:flex;align-items:center;gap:5px;"><div class="leg-dot" style="background:${{d.colors[i]}}"></div>${{lbl}} (${{d.pie_values[i]}})</div><span style="font-weight:700;color:#1a3a6b;">${{d.pie_values[i]}}</span>`;
      leg.appendChild(row);
    }});
    </script>
    </body>
    </html>
    """, height=370)


# ─────────────────────────────────────────────
#  ADMIN — COMPLAINTS TABLE TAB
# ─────────────────────────────────────────────
ROWS_PER_PAGE = 5

def render_admin_complaints_tab():
    all_c = st.session_state.complaints

    # ── Filters ──
    col_f1, col_f2 = st.columns([2, 3])
    with col_f1:
        status_filter = st.selectbox(
            "Status",
            ["All", "Pending", "In Progress", "Resolved"],
            key="tbl_status_filter",
        )
    with col_f2:
        search_q = st.text_input("🔍 Search", placeholder="Issue type, location, student…", key="tbl_search")

    # Apply filters
    filtered = all_c
    if status_filter != "All":
        filtered = [c for c in filtered if c["status"] == status_filter]
    if search_q.strip():
        q = search_q.strip().lower()
        filtered = [
            c for c in filtered
            if q in c.get("type","").lower()
            or q in c.get("location","").lower()
            or q in c.get("student","").lower()
            or q in c.get("description","").lower()
        ]

    total_rows = len(filtered)
    page       = st.session_state.cmp_page
    max_page   = max(0, (total_rows - 1) // ROWS_PER_PAGE)
    page       = min(page, max_page)
    st.session_state.cmp_page = page

    page_rows = filtered[page * ROWS_PER_PAGE : (page + 1) * ROWS_PER_PAGE]

    if not filtered:
        st.info("No complaints match the current filters.")
        return

    # ── Table ──
    for i, c in enumerate(page_rows):
        global_i = st.session_state.complaints.index(c)
        pri_cls  = {"High": "pri-high", "Medium": "pri-medium", "Low": "pri-low"}.get(c.get("priority","Medium"), "pri-medium")

        with st.expander(
            f"{c['id']}  |  {c['type']}  —  📍 {c['location']}  |  👤 {c.get('student','?')}",
            expanded=False,
        ):
            # Detail card
            st.markdown(f"""
            <div class="admin-row">
                <h4>{c['type']} &nbsp; {badge_html(c['status'])}</h4>
                <p>📍 <b>Location:</b> {c['location']}</p>
                <p>👤 <b>Student:</b> {c.get('student','—')} &nbsp;·&nbsp;
                   ⚡ <b>Priority:</b> <span class="{pri_cls}">{c.get('priority','—')}</span> &nbsp;·&nbsp;
                   🗓 <b>Date:</b> {c['date']}</p>
                <p>📄 <b>Description:</b> {c.get('description','—')}</p>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 2])

            with col_a:
                st.markdown('<div class="green-btn">', unsafe_allow_html=True)
                if st.button("✔ Accept", key=f"acc_{i}_{page}"):
                    update_complaint_status(c["id"], "In Progress", "True")
                    st.session_state.complaints = get_complaints()
                    st.success(f"{c['id']} accepted.")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col_b:
                st.markdown('<div class="red-btn">', unsafe_allow_html=True)
                if st.button("✖ Decline", key=f"dec_{i}_{page}"):
                    update_complaint_status(c["id"], "Resolved", "False")
                    st.session_state.complaints = get_complaints()
                    st.warning(f"{c['id']} declined.")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col_c:
                acc = c.get("accepted")
                if acc == "True":
                    st.markdown('<span class="badge badge-blue" style="display:inline-block;margin-top:8px;">Accepted ✔</span>', unsafe_allow_html=True)
                elif acc == "False":
                    st.markdown('<span class="badge badge-red" style="display:inline-block;margin-top:8px;">Declined ✖</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="{pri_cls}" style="display:inline-block;margin-top:8px;">{c.get("priority","—")}</span>', unsafe_allow_html=True)

            with col_d:
                new_status = st.selectbox(
                    "Update Status",
                    ["Pending", "In Progress", "Resolved"],
                    index=["Pending", "In Progress", "Resolved"].index(c["status"]),
                    key=f"sel_{i}_{page}",
                )
                st.markdown('<div class="blue-btn">', unsafe_allow_html=True)
                if st.button("💾 Save", key=f"save_{i}_{page}", use_container_width=True):
                    update_complaint_status(c["id"], new_status)
                    st.session_state.complaints = get_complaints()
                    st.success(f"{c['id']} → {new_status}")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Pagination
    if total_rows > 0:
        st.markdown(f"<p style='font-size:.8rem;color:#6b7a99;margin-top:8px;'>{page*ROWS_PER_PAGE+1}–{min((page+1)*ROWS_PER_PAGE, total_rows)} of {total_rows}</p>", unsafe_allow_html=True)
        pc1, pc2, pc3 = st.columns([2, 1, 1])
        with pc2:
            if page > 0:
                if st.button("← Previous"):
                    st.session_state.cmp_page -= 1
                    st.rerun()
        with pc3:
            if page < max_page:
                if st.button("Next →"):
                    st.session_state.cmp_page += 1
                    st.rerun()

# ─────────────────────────────────────────────
#  PAGE 5 — ADMIN DASHBOARD (tabbed)
# ─────────────────────────────────────────────
def page_admin_dashboard():
    render_header()
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col_title, col_logout = st.columns([3, 1])
    with col_title:
        st.markdown('<p class="card-title">🛡️ Admin Dashboard</p>', unsafe_allow_html=True)
    with col_logout:
        logout_button()

    # Tab nav
    tab_col1, tab_col2 = st.columns(2)
    with tab_col1:
        if st.button("📊  Dashboard Overview", use_container_width=True,
                     type="primary" if st.session_state.admin_tab == "dashboard" else "secondary"):
            st.session_state.admin_tab = "dashboard"
            st.session_state.cmp_page = 0
            st.rerun()
    with tab_col2:
        if st.button("📋  Manage Complaints", use_container_width=True,
                     type="primary" if st.session_state.admin_tab == "complaints" else "secondary"):
            st.session_state.admin_tab = "complaints"
            st.session_state.cmp_page = 0
            st.rerun()

    st.markdown("<hr style='border:none;border-top:2px solid #e0eaf8;margin:1rem 0 1.2rem;'>", unsafe_allow_html=True)

    if st.session_state.admin_tab == "dashboard":
        render_admin_dashboard_tab()
    else:
        render_admin_complaints_tab()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="app-footer">
        Admin Portal <span>•</span> Smart College Problem Reporter
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN — PAGE ROUTER
# ─────────────────────────────────────────────
def main():
    load_styles()
    init_state()
    init_db()

    if st.session_state.role is None and st.session_state.page != "login":
        st.session_state.page = "login"

    routes = {
        "login":           page_login,
        "home":            page_home,
        "report":          page_report,
        "complaints":      page_complaints,
        "track":           page_track,
        "admin_dashboard": page_admin_dashboard,
    }

    routes.get(st.session_state.page, page_login)()


if __name__ == "__main__":
    main()