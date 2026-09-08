import hashlib
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "server_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "cyber_rakshak.sqlite3"
FEEDBACK_DB_PATH = DATA_DIR / "voxshield_feedback.sqlite3"
TEAM_DB_PATH = DATA_DIR / "team_admin.sqlite3"

st.set_page_config(page_title="Cyber Rakshak · Team Command", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&family=JetBrains+Mono:wght@500;700&display=swap');
.stApp{background:#f5f7fb;color:#172033}.block-container{max-width:1450px;padding:24px 28px 48px!important}
.admin-brand{display:flex;align-items:center;gap:13px;margin:4px 0 25px}.brand-shield{width:48px;height:48px;border-radius:13px;background:linear-gradient(145deg,#0b4c8d,#0f766e);display:grid;place-items:center;color:#fff;font:800 15px 'JetBrains Mono';box-shadow:0 10px 25px rgba(7,59,111,.18)}
.brand-name{font:700 23px 'Libre Baskerville',serif;color:#102238}.brand-name span{display:block;font:700 8px 'JetBrains Mono';letter-spacing:2px;color:#6b7788;margin-top:5px;text-transform:uppercase}
.auth-wrap{max-width:510px;margin:6vh auto 0;background:#fff;border:1px solid #dbe3eb;border-radius:20px;padding:10px 30px 28px;box-shadow:0 22px 60px rgba(20,39,61,.12)}
.auth-bar{height:4px;border-radius:0 0 8px 8px;background:linear-gradient(90deg,#0b4c8d,#0f766e);margin-bottom:22px}.auth-title{text-align:center;font:700 27px 'Libre Baskerville',serif;color:#172033}.auth-sub{text-align:center;color:#6c7888;font:500 12px 'DM Sans';margin:7px 0 22px}
[data-testid='stSidebar']{background:#10283f}.sidebar-title{font:700 17px 'Libre Baskerville',serif;color:#fff}.sidebar-sub{font:700 8px 'JetBrains Mono';letter-spacing:1.5px;color:#9eb3c7;text-transform:uppercase;margin-top:4px}
.stButton>button,.stDownloadButton>button{border-radius:9px!important;font-weight:700!important;min-height:40px}.metric-box{background:#fff;border:1px solid #dde5ec;border-radius:13px;padding:17px 18px}.metric-label{font:700 9px 'JetBrains Mono';letter-spacing:1.2px;text-transform:uppercase;color:#758398}.metric-value{font:700 27px 'DM Sans';color:#102238;margin-top:5px}.panel{background:#fff;border:1px solid #dde5ec;border-radius:14px;padding:18px}.page-kicker{font:700 9px 'JetBrains Mono';letter-spacing:1.8px;text-transform:uppercase;color:#0f766e}.page-title{font:700 31px 'Libre Baskerville',serif;color:#14253a;margin-top:6px}.page-sub{font:500 12px 'DM Sans';color:#68778a;margin-top:5px;margin-bottom:18px}.notice{padding:12px 14px;border-radius:10px;background:#eef6fa;border:1px solid #cde1eb;color:#27445b;font:500 11px 'DM Sans'}.danger{background:#fff4f4;border-color:#f1caca;color:#8c2e38}.stTabs [data-baseweb='tab-list']{gap:5px;background:#eaf0f5;padding:5px;border-radius:11px}.stTabs [data-baseweb='tab']{font-weight:700;color:#526174}.stTabs [aria-selected='true']{background:#0b4c8d!important;color:#fff!important;border-radius:8px}.stDataFrame{border-radius:10px}.footer{margin-top:25px;text-align:center;color:#8995a4;font:500 9px 'JetBrains Mono';letter-spacing:.5px}
@media(max-width:700px){.block-container{padding:16px 12px 35px!important}.auth-wrap{margin-top:2vh;padding:8px 17px 22px}.page-title{font-size:25px}.brand-name{font-size:19px}}
</style>
""", unsafe_allow_html=True)


def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def db(path):
    c=sqlite3.connect(path, timeout=30, check_same_thread=False)
    c.row_factory=sqlite3.Row
    c.execute("PRAGMA busy_timeout=30000")
    c.execute("PRAGMA journal_mode=WAL")
    return c

def hash_password(password, salt=None):
    salt=salt or secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,220000)
    return salt.hex()+":"+digest.hex()

def verify_password(password, stored):
    try:
        salt,digest=stored.split(':',1)
        test=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),220000).hex()
        return secrets.compare_digest(test,digest)
    except Exception: return False

def secret_value(name):
    try: return str(st.secrets.get(name, "")).strip()
    except Exception: return ""

def init_team_db():
    with db(TEAM_DB_PATH) as c:
        c.execute("CREATE TABLE IF NOT EXISTS team_members(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'team_member', status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL, last_login TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS admin_audit(id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER, action TEXT NOT NULL, details TEXT, created_at TEXT NOT NULL)")
        c.commit()

def audit(member_id, action, details=""):
    with db(TEAM_DB_PATH) as c:
        c.execute("INSERT INTO admin_audit(member_id,action,details,created_at) VALUES(?,?,?,?)",(member_id,action,details[:500],now()))
        c.commit()

def team_register(name,email,password,invite):
    name=name.strip(); email=email.strip().lower(); invite=invite.strip()
    if len(name)<2: return False,"Enter your team name."
    if "@" not in email or len(email)<6: return False,"Enter a valid team email."
    if len(password)<8: return False,"Password must contain at least 8 characters."
    member_code=secret_value("team_member_invite_code")
    admin_code=secret_value("team_admin_invite_code")
    if not member_code and not admin_code: return False,"Team registration is locked until an invite code is configured on the server."
    role="admin" if admin_code and secrets.compare_digest(invite,admin_code) else ("team_member" if member_code and secrets.compare_digest(invite,member_code) else "")
    if not role: return False,"Invalid team invitation code."
    with db(TEAM_DB_PATH) as c:
        if c.execute("SELECT id FROM team_members WHERE lower(email)=?",(email,)).fetchone(): return False,"This team email is already registered."
        c.execute("INSERT INTO team_members(name,email,password_hash,role,status,created_at) VALUES(?,?,?,?,?,?)",(name,email,hash_password(password),role,"active",now())); c.commit()
    return True,"Team account created."

def team_login(email,password):
    email=email.strip().lower()
    with db(TEAM_DB_PATH) as c: row=c.execute("SELECT * FROM team_members WHERE lower(email)=?",(email,)).fetchone()
    if row and row['status']=="active" and verify_password(password,row['password_hash']):
        with db(TEAM_DB_PATH) as c:
            c.execute("UPDATE team_members SET last_login=? WHERE id=?",(now(),row['id'])); c.commit()
        audit(row['id'],"team_login","successful password login")
        return dict(row)
    if row: audit(row['id'],"team_login_failed","failed password login")
    return None

def q(path, sql, params=()):
    if not path.exists(): return pd.DataFrame()
    with db(path) as c: return pd.read_sql_query(sql,c,params=params)

def auth_page():
    st.markdown("<div class='auth-wrap'><div class='auth-bar'></div><div class='admin-brand' style='justify-content:center;margin-bottom:8px'><div class='brand-shield'>CR</div><div class='brand-name'>CYBER RAKSHAK<span>TEAM COMMAND CENTER</span></div></div></div>",unsafe_allow_html=True)
    tabs=st.tabs(["TEAM LOGIN","TEAM REGISTER"])
    with tabs[0]:
        st.markdown("<div class='auth-title'>Team Login</div><div class='auth-sub'>Authorized team members only · server database access</div>",unsafe_allow_html=True)
        email=st.text_input("Team email",key="admin_login_email")
        pw=st.text_input("Password",type="password",key="admin_login_pw")
        if st.button("LOGIN TO COMMAND CENTER",type="primary",width="stretch",key="admin_login_btn"):
            user=team_login(email,pw)
            if user:
                st.session_state.team_admin=user; st.rerun()
            st.error("Invalid team credentials or inactive team account.")
    with tabs[1]:
        st.markdown("<div class='auth-title'>Team Registration</div><div class='auth-sub'>Registration requires a private invitation code issued by the project team.</div>",unsafe_allow_html=True)
        name=st.text_input("Full name",key="admin_reg_name")
        email=st.text_input("Team email",key="admin_reg_email")
        pw=st.text_input("Create password",type="password",key="admin_reg_pw")
        confirm=st.text_input("Confirm password",type="password",key="admin_reg_confirm")
        invite=st.text_input("Team invitation code",type="password",key="admin_reg_invite")
        if st.button("REGISTER TEAM ACCOUNT",type="primary",width="stretch",key="admin_reg_btn"):
            if pw!=confirm: st.error("Passwords do not match.")
            else:
                ok,msg=team_register(name,email,pw,invite)
                st.success(msg) if ok else st.error(msg)
    st.markdown("<div class='notice' style='margin-top:14px'>The public Cyber Rakshak user database is not exposed until team authentication succeeds. Team credentials are stored as salted PBKDF2-SHA256 hashes.</div>",unsafe_allow_html=True)


def admin_app(user):
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>CYBER RAKSHAK</div><div class='sidebar-sub'>Team command center</div>",unsafe_allow_html=True)
        st.write("")
        st.caption(f"Signed in: {user['email']}")
        nav=st.radio("ADMIN NAVIGATION",["Overview","Users & Registration","Login Activity","Feedback","Contact Messages","Cases","Evidence","Dataset Activity","Team Members","Audit Log"],key="admin_nav")
        if st.button("Sign out",width="stretch",key="admin_logout"):
            audit(user['id'],"team_logout","signed out")
            st.session_state.team_admin=None; st.rerun()

    st.markdown("<div class='admin-brand'><div class='brand-shield'>CR</div><div class='brand-name'>Cyber Rakshak<span>TEAM COMMAND CENTER · AUTHORIZED ACCESS</span></div></div>",unsafe_allow_html=True)
    users=q(DB_PATH,"SELECT id,username,email,dob,created_at,updated_at FROM users ORDER BY created_at DESC")
    logins=q(DB_PATH,"SELECT id,user_id,identifier,method,status,created_at FROM login_activity ORDER BY created_at DESC")
    cases=q(DB_PATH,"SELECT id,user_id,title,subject,priority,created,updated_at FROM cases ORDER BY updated_at DESC")
    evidence=q(DB_PATH,"SELECT id,case_id,ev_code,type,source,raw,analysis_json,timestamp FROM evidence ORDER BY id DESC")
    datasets=q(DB_PATH,"SELECT id,user_id,case_id,dataset,source,records,columns,evidence_hash,created_at FROM dataset_log ORDER BY created_at DESC")
    feedback=q(FEEDBACK_DB_PATH,"SELECT * FROM feedback ORDER BY created_at DESC")
    contacts=q(FEEDBACK_DB_PATH,"SELECT * FROM contact_notes ORDER BY created_at DESC")
    members=q(TEAM_DB_PATH,"SELECT id,name,email,role,status,created_at,last_login FROM team_members ORDER BY created_at DESC")
    audits=q(TEAM_DB_PATH,"SELECT * FROM admin_audit ORDER BY created_at DESC")

    if nav=="Overview":
        st.markdown("<div class='page-kicker'>SERVER CONTROL</div><div class='page-title'>Central response console.</div><div class='page-sub'>Data submitted from authorized user sessions on the deployed application is organized below by database domain.</div>",unsafe_allow_html=True)
        cols=st.columns(6)
        vals=[("Users",len(users)),("Cases",len(cases)),("Evidence",len(evidence)),("Feedback",len(feedback)),("Contacts",len(contacts)),("Team",len(members))]
        for col,(label,val) in zip(cols,vals): col.markdown(f"<div class='metric-box'><div class='metric-label'>{label}</div><div class='metric-value'>{val:,}</div></div>",unsafe_allow_html=True)
        st.write("")
        st.markdown("<div class='panel'><b>Access rule</b><br><span style='color:#69788a;font-size:12px'>This console is protected by a separate team-authentication database. Public users cannot enter this console unless they possess an authorized team account.</span></div>",unsafe_allow_html=True)
    else:
        title_map={"Users & Registration":"Registered users","Login Activity":"Login activity","Feedback":"Feedback responses","Contact Messages":"Contact messages","Cases":"Investigation cases","Evidence":"Evidence records","Dataset Activity":"Dataset provenance","Team Members":"Authorized team accounts","Audit Log":"Admin audit trail"}
        st.markdown(f"<div class='page-kicker'>DATABASE VIEW</div><div class='page-title'>{title_map[nav]}</div><div class='page-sub'>Read-only administrative view. Use CSV export for authorized analysis.</div>",unsafe_allow_html=True)
        df={"Users & Registration":users,"Login Activity":logins,"Feedback":feedback,"Contact Messages":contacts,"Cases":cases,"Evidence":evidence,"Dataset Activity":datasets,"Team Members":members,"Audit Log":audits}[nav]
        if df.empty: st.info("No records available yet.")
        else:
            search=st.text_input("Search this section",placeholder="Type a name, email, case ID, source or keyword…",key="admin_search")
            view=df
            if search.strip():
                mask=view.astype(str).apply(lambda row: row.str.contains(search.strip(),case=False,na=False).any(),axis=1)
                view=view[mask]
            st.dataframe(view,width="stretch",hide_index=True)
            st.download_button("EXPORT CSV",view.to_csv(index=False).encode("utf-8"),f"cyber_rakshak_{nav.lower().replace(' ','_').replace('&','and')}.csv","text/csv",width="stretch")

    st.markdown("<div class='footer'>CYBER RAKSHAK · TEAM DATA GOVERNANCE · HUMAN REVIEW REQUIRED · KEEP THIS CONSOLE PRIVATE</div>",unsafe_allow_html=True)

init_team_db()
if "team_admin" not in st.session_state: st.session_state.team_admin=None
if not st.session_state.team_admin:
    auth_page()
else:
    admin_app(st.session_state.team_admin)
