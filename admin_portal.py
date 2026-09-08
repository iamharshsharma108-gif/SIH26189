import os
import sys
import json
import secrets
import sqlite3
import datetime
import platform
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import pandas as pd
import streamlit as st

# ============================================================
# MODULE 1: APP, PATH & EMAIL CONFIGURATION
# ============================================================
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "server_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "cyber_rakshak.sqlite3"
FEEDBACK_DB_PATH = DATA_DIR / "voxshield_feedback.sqlite3"

# System Admin Email Target
SYSTEM_ADMIN_EMAIL = "hskiraoli7@gmail.com"

# Gmail SMTP Credentials
GMAIL_SENDER = "hskiraoli7@gmail.com"
GMAIL_APP_PASSWORD = "yzmu ngsn tglb xxrw"

st.set_page_config(
    page_title="Cyber Rakshak · Admin & Team Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# MODULE 2: DATABASE UTILITIES & FEEDBACK ENGINE
# ============================================================
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    return conn

def get_feedback_db():
    conn = sqlite3.connect(FEEDBACK_DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    return conn

def init_admin_db():
    """Creates database tables for Admins, Regular Users, and Feedback."""
    with get_db() as c:
        # Table 1: Admin / Team members
        c.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                dob TEXT NOT NULL,
                password_hash TEXT DEFAULT '',
                approval_status TEXT DEFAULT 'PENDING',
                reset_token TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Table 2: Regular Users
        c.execute("""
            CREATE TABLE IF NOT EXISTS regular_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                dob TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                subject TEXT,
                description TEXT,
                priority TEXT,
                created TEXT,
                updated_at TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS dataset_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                case_id INTEGER,
                dataset TEXT,
                source TEXT,
                records INTEGER,
                created_at TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                ev_code TEXT,
                type TEXT,
                source TEXT,
                timestamp TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                target TEXT,
                details TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        c.commit()

    # Table 3: Dedicated Feedback DB
    with get_feedback_db() as f_c:
        f_c.execute("""
            CREATE TABLE IF NOT EXISTS portal_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT DEFAULT 'Anonymous',
                user_email TEXT DEFAULT '',
                category TEXT DEFAULT 'General',
                rating INTEGER DEFAULT 5,
                comments TEXT NOT NULL,
                status TEXT DEFAULT 'NEW',
                created_at TEXT NOT NULL
            )
        """)
        f_c.commit()

def seed_team_members():
    """Seeds internal admin team members."""
    team_data = [
        ("Harsh", "harsh@cyberrakshak.internal", "harsh_cyber_rakshak_26189"),
        ("Devansh", "devansh@cyberrakshak.internal", "devansh_cyber_rakshak_26189"),
        ("Avinash", "avinash@cyberrakshak.internal", "avinash_cyber_rakshak_26189"),
        ("Manish", "manish@cyberrakshak.internal", "manish_cyber_rakshak_26189"),
        ("Krish", "krish@cyberrakshak.internal", "krish_cyber_rakshak_26189"),
        ("Mahak", "mahak@cyberrakshak.internal", "mahak_cyber_rakshak_26189"),
    ]
    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with get_db() as c:
        for name, email, key in team_data:
            c.execute("""
                INSERT INTO admin_users 
                (full_name, email, dob, password_hash, approval_status, reset_token, created_at, updated_at)
                VALUES (?, ?, '2000-01-01', ?, 'APPROVED', '', ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    full_name=excluded.full_name,
                    password_hash=excluded.password_hash,
                    approval_status='APPROVED',
                    updated_at=excluded.updated_at
            """, (name, email, key, now_ts, now_ts))
        c.commit()

init_admin_db()
seed_team_members()

def log_audit_action(actor, action, target="", details=""):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as c:
        c.execute(
            "INSERT INTO audit_logs (actor, action, target, details, timestamp) VALUES (?, ?, ?, ?, ?)",
            (actor, action, target, details, ts)
        )
        c.commit()

def send_real_email(recipient_email, subject, body):
    if GMAIL_APP_PASSWORD == "YOUR_16_CHAR_APP_PASSWORD":
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_SENDER
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, recipient_email, msg.as_string())
        return True
    except Exception:
        return False

def send_admin_notification(user_name, user_email, user_dob, reg_type):
    subject = f"Cyber Rakshak - New {reg_type} Registration Alert"
    body = f"Alert: A new {reg_type} registration request was submitted.\n\nName/Username: {user_name}\nEmail: {user_email}\nDOB: {user_dob}"
    send_real_email(SYSTEM_ADMIN_EMAIL, subject, body)
    log_audit_action("SYSTEM_EMAIL", "NOTIFICATION_SENT", SYSTEM_ADMIN_EMAIL, body)

def send_password_reset_link(user_email, token):
    reset_url = f"http://localhost:8501/?token={token}"
    subject = "Cyber Rakshak - Password Setup Token"
    body = f"Hello,\n\nYour registration has been approved. Click the link below to configure your password:\n{reset_url}"
    send_real_email(user_email, subject, body)
    log_audit_action("SYSTEM_EMAIL", "RESET_LINK_GENERATED", user_email, f"Password link: {reset_url}")

# ============================================================
# MODULE 3: VISUAL STYLING
# ============================================================
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&family=Source+Serif+4:wght@500;600&display=swap');

:root {
  --paper: #f3f1eb;
  --ink: #17201e;
  --muted: #68716d;
  --accent: #9b4f3e;
}

.stApp { background: var(--paper) !important; color: var(--ink) !important; }
.block-container { max-width: 1320px !important; padding: 20px 32px 60px !important; }
[data-testid="stSidebar"] { background: #f6f1e7 !important; border-right: 1px solid #d9d4ca !important; }

.admin-brand { padding: 10px 4px 18px; border-bottom: 1px solid #d9d4ca; margin-bottom: 16px; }
.admin-title-head { font-family: 'Source Serif 4', Georgia, serif !important; font-size: 24px !important; font-weight: 600 !important; }
.admin-sub-head { font-family: 'IBM Plex Mono', monospace !important; font-size: 10px !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; color: var(--muted) !important; }

.workspace-head { background: #fbfaf7 !important; border: 1px solid #d8d1c3 !important; border-radius: 4px !important; padding: 22px 26px !important; margin-bottom: 20px !important; }
.workspace-title { font-family: 'Source Serif 4', Georgia, serif !important; font-size: 32px !important; font-weight: 700 !important; color: #182230 !important; }

.stButton>button { border-radius: 2px !important; background: #eee9dc !important; border: 1px solid #cfc7b8 !important; font-weight: 600 !important; }
.stButton>button[type="primary"] { background: var(--accent) !important; border-color: var(--accent) !important; color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MODULE 4: AUTHENTICATION ENGINE
# ============================================================
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "admin_user" not in st.session_state:
    st.session_state.admin_user = ""

query_params = st.query_params
reset_token = query_params.get("token", None)

if not st.session_state.admin_authenticated:
    with st.sidebar:
        st.markdown("""
            <div class="admin-brand">
                <div class="admin-title-head">🛡️ CYBER RAKSHAK</div>
                <div class="admin-sub-head">System Administration Console</div>
            </div>
        """, unsafe_allow_html=True)
        st.info("Please Log In, Register, or submit feedback using the main portal window.")

    st.markdown("""
        <div class="workspace-head">
            <div class="admin-sub-head">AUTHENTICATION & FEEDBACK GATEWAY</div>
            <div class="workspace-title">Cyber Rakshak Access Portal</div>
        </div>
    """, unsafe_allow_html=True)

    if reset_token:
        st.markdown("### 🔑 Set Your Account Password")
        with get_db() as c:
            user_rec = c.execute("SELECT * FROM admin_users WHERE reset_token=?", (reset_token,)).fetchone()

        if user_rec:
            st.success(f"Token validated for Admin Account: **{user_rec['email']}**")
            new_pass = st.text_input("Enter New Password", type="password", key="new_pwd_set")
            confirm_pass = st.text_input("Confirm New Password", type="password", key="confirm_pwd_set")

            if st.button("Set Password & Login", type="primary"):
                if new_pass and new_pass == confirm_pass:
                    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with get_db() as c:
                        c.execute(
                            "UPDATE admin_users SET password_hash=?, reset_token='', approval_status='APPROVED', updated_at=? WHERE id=?",
                            (new_pass, now_ts, user_rec["id"])
                        )
                        c.commit()
                    log_audit_action(user_rec["email"], "PASSWORD_SET_SUCCESS", "System", "Password established via token")
                    st.success("Password configured successfully! Proceeding to login...")
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error("Passwords do not match or field is empty.")
        else:
            st.error("Invalid or expired password reset link token.")
            if st.button("Return to Login Portal"):
                st.query_params.clear()
                st.rerun()

    else:
        auth_tab1, auth_tab2, auth_tab3, auth_tab4 = st.tabs([
            "🔒 Admin Sign In", 
            "📝 Register Admin Member", 
            "👤 Register Regular User", 
            "💬 Portal Feedback"
        ])

        # TAB 1: ADMIN LOGIN
        with auth_tab1:
            st.markdown("### Login to Admin Console")
            login_input = st.text_input("Registered Email ID or Name", key="login_email_input").strip().lower()
            login_pass = st.text_input("Password / Passkey", type="password", key="login_pass_input").strip()

            if st.button("Sign In as Admin", type="primary"):
                with get_db() as c:
                    user = c.execute(
                        """
                        SELECT * FROM admin_users 
                        WHERE (LOWER(email) = ? OR LOWER(email) LIKE ? || '@%' OR LOWER(full_name) = ?) 
                        AND password_hash = ?
                        """, 
                        (login_input, login_input, login_input, login_pass)
                    ).fetchone()

                if user:
                    if user["approval_status"] == "APPROVED":
                        st.session_state.admin_authenticated = True
                        st.session_state.admin_user = user["full_name"]
                        log_audit_action(user["email"], "ADMIN_LOGIN", "System", "Successful admin portal authentication")
                        st.rerun()
                    elif user["approval_status"] == "PENDING":
                        st.warning("Your admin account is pending approval by the administrator.")
                    else:
                        st.error("Account access rejected. Contact system administrator.")
                else:
                    st.error("Invalid admin credentials or passkey.")

        # TAB 2: REGISTER ADMIN RECORD
        with auth_tab2:
            st.markdown("### Register Admin / Team Member")
            reg_name = st.text_input("Full Name", key="reg_admin_name")
            reg_email = st.text_input("Email ID", key="reg_admin_email")
            reg_dob = st.date_input("Date of Birth", min_value=datetime.date(1950, 1, 1), key="reg_admin_dob")

            if st.button("Submit Admin Registration", type="primary"):
                if reg_name and reg_email:
                    email_clean = reg_email.strip().lower()
                    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        with get_db() as c:
                            c.execute(
                                """INSERT INTO admin_users 
                                   (full_name, email, dob, approval_status, created_at, updated_at) 
                                   VALUES (?, ?, ?, 'PENDING', ?, ?)""",
                                (reg_name, email_clean, str(reg_dob), now_ts, now_ts)
                            )
                            c.commit()

                        send_admin_notification(reg_name, email_clean, str(reg_dob), "Admin")
                        log_audit_action(email_clean, "ADMIN_REGISTRATION", "admin_users", "Pending admin authentication")
                        st.success("Admin registration submitted! Notification sent to system admin.")
                    except sqlite3.IntegrityError:
                        st.error("An admin account with this email address already exists.")
                else:
                    st.error("Please fill in all mandatory fields.")

        # TAB 3: REGISTER REGULAR USER RECORD
        with auth_tab3:
            st.markdown("### Register Regular User Account")
            reg_username = st.text_input("Username", key="reg_usr_username")
            reg_uemail = st.text_input("Email ID", key="reg_usr_email")
            reg_udob = st.date_input("Date of Birth", min_value=datetime.date(1950, 1, 1), key="reg_usr_dob")
            reg_upass = st.text_input("Account Password", type="password", key="reg_usr_pass")

            if st.button("Register User Account", type="primary"):
                if reg_username and reg_uemail and reg_upass:
                    email_clean = reg_uemail.strip().lower()
                    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        with get_db() as c:
                            c.execute(
                                """INSERT INTO regular_users 
                                   (username, email, dob, password_hash, is_active, created_at, updated_at) 
                                   VALUES (?, ?, ?, ?, 1, ?, ?)""",
                                (reg_username, email_clean, str(reg_udob), reg_upass, now_ts, now_ts)
                            )
                            c.commit()

                        send_admin_notification(reg_username, email_clean, str(reg_udob), "Regular User")
                        log_audit_action(email_clean, "USER_REGISTRATION", "regular_users", "Registered directly")
                        st.success("Regular User account created successfully!")
                    except sqlite3.IntegrityError:
                        st.error("A user with this username or email address already exists.")
                else:
                    st.error("Please fill in all mandatory fields.")

        # TAB 4: PUBLIC PORTAL FEEDBACK SUBMISSION
        with auth_tab4:
            st.markdown("### Submit Feedback for Cyber Rakshak Portal")
            fb_name = st.text_input("Your Name (Optional)", key="pub_fb_name")
            fb_email = st.text_input("Your Email (Optional)", key="pub_fb_email")
            fb_category = st.selectbox("Category", ["Bug Report", "Feature Request", "UI/UX Suggestion", "General Feedback"], key="pub_fb_cat")
            fb_rating = st.slider("Rating (1 = Poor, 5 = Excellent)", 1, 5, 5, key="pub_fb_rate")
            fb_comments = st.text_area("Your Comments / Suggestions", key="pub_fb_comm")

            if st.button("Submit Feedback", type="primary"):
                if fb_comments.strip():
                    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with get_feedback_db() as f_c:
                        f_c.execute(
                            """INSERT INTO portal_feedback 
                               (user_name, user_email, category, rating, comments, status, created_at) 
                               VALUES (?, ?, ?, ?, ?, 'NEW', ?)""",
                            (fb_name.strip() or "Anonymous", fb_email.strip(), fb_category, fb_rating, fb_comments.strip(), now_ts)
                        )
                        f_c.commit()
                    log_audit_action(fb_email.strip() or "Anonymous", "FEEDBACK_SUBMITTED", "voxshield_feedback", fb_category)
                    st.success("Thank you! Your feedback has been logged into the portal system.")
                else:
                    st.error("Please enter your comments before submitting.")

    st.stop()

# ============================================================
# MODULE 5: SIDEBAR CONTROL FOR LOGGED-IN USERS
# ============================================================
with st.sidebar:
    st.markdown("""
        <div class="admin-brand">
            <div class="admin-title-head">🛡️ CYBER RAKSHAK</div>
            <div class="admin-sub-head">System Administration Console</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.success(f"Active Session:\n**{st.session_state.admin_user}**")
    if st.button("Log Out Admin", width="stretch"):
        log_audit_action(st.session_state.admin_user, "ADMIN_LOGOUT", "System", "Session terminated")
        st.session_state.admin_authenticated = False
        st.session_state.admin_user = ""
        st.rerun()

# ============================================================
# MODULE 6: MAIN ADMIN DASHBOARD WORKSPACE
# ============================================================
st.markdown("""
    <div class="workspace-head">
        <div class="admin-sub-head">CYBER RAKSHAK CENTRAL CONTROL</div>
        <div class="workspace-title">Administrative Portal</div>
    </div>
""", unsafe_allow_html=True)

nav_tabs = st.tabs([
    "📊 Overview", 
    "👥 Regular Users", 
    "🛡️ Admin Members",
    "📩 Pending Admin Approvals",
    "💬 Portal Feedback",
    "📁 Investigations", 
    "🗄️ Data Management", 
    "📜 Activity Logs"
])

# ------------------------------------------------------------
# TAB 1: OVERVIEW
# ------------------------------------------------------------
with nav_tabs[0]:
    with get_db() as c:
        u_count = c.execute("SELECT COUNT(*) FROM regular_users").fetchone()[0]
        a_u_count = c.execute("SELECT COUNT(*) FROM regular_users WHERE is_active=1").fetchone()[0]
        adm_count = c.execute("SELECT COUNT(*) FROM admin_users").fetchone()[0]
        c_count = c.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        d_count = c.execute("SELECT COUNT(*) FROM dataset_log").fetchone()[0]

    with get_feedback_db() as f_c:
        fb_total = f_c.execute("SELECT COUNT(*) FROM portal_feedback").fetchone()[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Regular Users", u_count, f"{a_u_count} Active")
    c2.metric("Admin Team Members", adm_count)
    c3.metric("Total Cases", c_count)
    c4.metric("Feedback Entries", fb_total)

    st.markdown("---")
    st.markdown("### Recent System Activity")
    with get_db() as c:
        recent_logs = pd.read_sql_query(
            "SELECT timestamp, actor, action, target, details FROM audit_logs ORDER BY id DESC LIMIT 8", c
        )
    if not recent_logs.empty:
        st.dataframe(recent_logs, width="stretch", hide_index=True)

# ------------------------------------------------------------
# TAB 2: SEPARATED REGULAR USER MANAGEMENT
# ------------------------------------------------------------
with nav_tabs[1]:
    st.markdown("### Regular User Accounts (`regular_users`)")
    with get_db() as c:
        users_df = pd.read_sql_query(
            "SELECT id, username, email, dob, is_active, created_at, updated_at FROM regular_users ORDER BY created_at DESC", c
        )

    if users_df.empty:
        st.info("No regular user accounts found.")
    else:
        st.dataframe(users_df, width="stretch", hide_index=True)

        st.markdown("---")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.markdown("**Toggle Active Status**")
            target_user_id = st.number_input("Target User ID", min_value=1, step=1, key="tog_usr_id")
            if st.button("Toggle Status", type="primary", key="btn_tog_usr"):
                with get_db() as c:
                    curr = c.execute("SELECT is_active, username FROM regular_users WHERE id=?", (target_user_id,)).fetchone()
                    if curr:
                        new_st = 0 if curr["is_active"] == 1 else 1
                        c.execute("UPDATE regular_users SET is_active=?, updated_at=? WHERE id=?", 
                                  (new_st, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), target_user_id))
                        c.commit()
                        log_audit_action(st.session_state.admin_user, "USER_STATUS_TOGGLE", curr["username"], f"Set is_active={new_st}")
                        st.success(f"Updated user ID {target_user_id} active state to {new_st}.")
                        st.rerun()

        with col_u2:
            st.markdown("**Delete Regular User**")
            del_user_id = st.number_input("Target User ID to Delete", min_value=1, step=1, key="del_usr_id")
            if st.button("Delete Regular User", type="secondary"):
                with get_db() as c:
                    u_info = c.execute("SELECT username FROM regular_users WHERE id=?", (del_user_id,)).fetchone()
                    if u_info:
                        c.execute("DELETE FROM regular_users WHERE id=?", (del_user_id,))
                        c.commit()
                        log_audit_action(st.session_state.admin_user, "USER_DELETE", u_info["username"], f"Deleted User ID {del_user_id}")
                        st.success(f"User '{u_info['username']}' deleted.")
                        st.rerun()

# ------------------------------------------------------------
# TAB 3: SEPARATED ADMIN MEMBERS LIST
# ------------------------------------------------------------
with nav_tabs[2]:
    st.markdown("### Admin & Team Members (`admin_users`)")
    with get_db() as c:
        admin_df = pd.read_sql_query(
            "SELECT id, full_name, email, dob, approval_status, created_at FROM admin_users WHERE approval_status='APPROVED' ORDER BY created_at DESC", c
        )
    st.dataframe(admin_df, width="stretch", hide_index=True)

# ------------------------------------------------------------
# TAB 4: PENDING ADMIN APPROVALS
# ------------------------------------------------------------
with nav_tabs[3]:
    st.markdown("### Pending Admin Registration Approvals")
    with get_db() as c:
        pending_df = pd.read_sql_query(
            "SELECT id, full_name, email, dob, approval_status, created_at FROM admin_users WHERE approval_status='PENDING' ORDER BY created_at DESC", c
        )

    if pending_df.empty:
        st.info("No pending admin registrations found.")
    else:
        st.dataframe(pending_df, width="stretch", hide_index=True)
        st.markdown("---")
        target_admin_id = st.number_input("Enter Admin Registration ID to Approve", min_value=1, step=1, key="app_admin_id")
        if st.button("Approve & Generate Password Link", type="primary"):
            token = secrets.token_urlsafe(16)
            now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with get_db() as c:
                rec = c.execute("SELECT full_name, email FROM admin_users WHERE id=?", (target_admin_id,)).fetchone()
                if rec:
                    c.execute(
                        "UPDATE admin_users SET reset_token=?, updated_at=? WHERE id=?",
                        (token, now_ts, target_admin_id)
                    )
                    c.commit()
                    send_password_reset_link(rec["email"], token)
                    log_audit_action(st.session_state.admin_user, "ADMIN_APPROVED", rec["email"], f"Token generated: {token}")
                    st.success(f"Approved {rec['full_name']}. Password setup link generated.")
                    st.code(f"http://localhost:8501/?token={token}", language="text")

# ------------------------------------------------------------
# TAB 5: ADMIN FEEDBACK MANAGEMENT
# ------------------------------------------------------------
with nav_tabs[4]:
    st.markdown("### Feedback Received (`voxshield_feedback.sqlite3`)")
    with get_feedback_db() as f_c:
        feedback_df = pd.read_sql_query(
            "SELECT id, user_name, user_email, category, rating, comments, status, created_at FROM portal_feedback ORDER BY created_at DESC", f_c
        )

    if feedback_df.empty:
        st.info("No feedback records submitted yet.")
    else:
        st.dataframe(feedback_df, width="stretch", hide_index=True)
        st.markdown("---")
        col_fb1, col_fb2 = st.columns(2)
        
        with col_fb1:
            st.markdown("**Update Feedback Status**")
            fb_id_up = st.number_input("Feedback ID", min_value=1, step=1, key="fb_id_up_in")
            fb_st_new = st.selectbox("New Status", ["REVIEWED", "IN_PROGRESS", "RESOLVED", "NEW"], key="fb_st_sel")
            if st.button("Update Status", type="primary"):
                with get_feedback_db() as f_c:
                    f_c.execute("UPDATE portal_feedback SET status=? WHERE id=?", (fb_st_new, fb_id_up))
                    f_c.commit()
                log_audit_action(st.session_state.admin_user, "FEEDBACK_STATUS_UPDATE", f"ID {fb_id_up}", f"Status set to {fb_st_new}")
                st.success(f"Updated Feedback ID {fb_id_up} to status '{fb_st_new}'.")
                st.rerun()

        with col_fb2:
            st.markdown("**Delete Feedback Entry**")
            fb_id_del = st.number_input("Feedback ID to Delete", min_value=1, step=1, key="fb_id_del_in")
            if st.button("Delete Entry", type="secondary"):
                with get_feedback_db() as f_c:
                    f_c.execute("DELETE FROM portal_feedback WHERE id=?", (fb_id_del,))
                    f_c.commit()
                log_audit_action(st.session_state.admin_user, "FEEDBACK_DELETE", f"ID {fb_id_del}", "Deleted record")
                st.success(f"Feedback entry ID {fb_id_del} deleted.")
                st.rerun()

# ------------------------------------------------------------
# TAB 6: INVESTIGATIONS
# ------------------------------------------------------------
with nav_tabs[5]:
    st.markdown("### Investigation Case Overview")
    with get_db() as c:
        cases_df = pd.read_sql_query(
            """SELECT c.id AS case_id, u.username AS owner, c.title, c.subject, c.priority, c.created, c.updated_at 
               FROM cases c LEFT JOIN regular_users u ON c.user_id = u.id ORDER BY c.updated_at DESC""", c
        )
    if cases_df.empty:
        st.info("No active investigation cases recorded.")
    else:
        st.dataframe(cases_df, width="stretch", hide_index=True)

# ------------------------------------------------------------
# TAB 7: DATA MANAGEMENT
# ------------------------------------------------------------
with nav_tabs[6]:
    st.markdown("### Dataset Registry")
    with get_db() as c:
        datasets_df = pd.read_sql_query("SELECT * FROM dataset_log ORDER BY created_at DESC", c)
    if datasets_df.empty:
        st.info("No dataset logs recorded.")
    else:
        st.dataframe(datasets_df, width="stretch", hide_index=True)

# ------------------------------------------------------------
# TAB 8: ACTIVITY LOGS
# ------------------------------------------------------------
with nav_tabs[7]:
    st.markdown("### System Audit Trail")
    with get_db() as c:
        all_logs = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC", c)
    if not all_logs.empty:
        st.dataframe(all_logs, width="stretch", hide_index=True)
