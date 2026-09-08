import os
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "server_data"
DB_PATH = DATA_DIR / "cyber_rakshak.sqlite3"
FEEDBACK_DB_PATH = DATA_DIR / "voxshield_feedback.sqlite3"

st.set_page_config(page_title="Cyber Rakshak · Server Admin", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.stApp{background:#f5f7fb}.block-container{max-width:1400px;padding:28px 28px 50px}.admin-head{background:#fff;border:1px solid #dfe5ec;border-radius:14px;padding:22px 24px;margin-bottom:18px}.admin-title{font-size:30px;font-weight:800;color:#172033}.admin-sub{color:#667085;margin-top:5px}.stButton>button{border-radius:8px;font-weight:700}.stDownloadButton>button{border-radius:8px;font-weight:700}
</style>
""", unsafe_allow_html=True)


def admin_password():
    try:
        return str(st.secrets.get("admin_portal_password", "")).strip()
    except Exception:
        return ""

if not admin_password():
    st.error("Admin portal is locked. Add admin_portal_password to .streamlit/secrets.toml on the server.")
    st.stop()

with st.sidebar:
    st.markdown("### 🛡️ Cyber Rakshak")
    st.caption("Separate server response portal")
    password = st.text_input("Admin password", type="password")
    if password != admin_password():
        st.info("Enter the configured admin password to view server data.")
        st.stop()
    st.success("Authenticated")

st.markdown('<div class="admin-head"><div class="admin-title">Central Server Response Console</div><div class="admin-sub">This separate portal reads the same server-side databases used by the Cyber Rakshak Streamlit application. Data submitted from other computers appears here when they connect to the same deployment.</div></div>', unsafe_allow_html=True)

if not DB_PATH.exists():
    st.warning("No server database has been created yet. Start the main Cyber Rakshak application and receive a registration or case submission first.")
    st.stop()

with sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False) as c:
    users = pd.read_sql_query("SELECT id,username,email,dob,created_at,updated_at FROM users ORDER BY created_at DESC", c)
    cases = pd.read_sql_query("SELECT id,user_id,title,subject,priority,created,updated_at FROM cases ORDER BY updated_at DESC", c)
    datasets = pd.read_sql_query("SELECT id,user_id,case_id,dataset,source,records,created_at FROM dataset_log ORDER BY created_at DESC", c)

if FEEDBACK_DB_PATH.exists():
    with sqlite3.connect(FEEDBACK_DB_PATH, timeout=20, check_same_thread=False) as c:
        feedback = pd.read_sql_query("SELECT * FROM feedback ORDER BY created_at DESC", c)
        contacts = pd.read_sql_query("SELECT * FROM contact_notes ORDER BY created_at DESC", c)
else:
    feedback = pd.DataFrame()
    contacts = pd.DataFrame()

a,b,c,d = st.columns(4)
a.metric("Registered users", len(users)); b.metric("Cases", len(cases)); c.metric("Feedback", len(feedback)); d.metric("Contact notes", len(contacts))

t1,t2,t3,t4 = st.tabs(["Registrations","Feedback","Contact notes","Cases & datasets"])
with t1:
    st.dataframe(users, width="stretch", hide_index=True)
    st.download_button("Export registrations CSV", users.to_csv(index=False).encode(), "cyber_rakshak_registrations.csv", "text/csv", width="stretch")
with t2:
    st.dataframe(feedback, width="stretch", hide_index=True)
    st.download_button("Export feedback CSV", feedback.to_csv(index=False).encode(), "cyber_rakshak_feedback.csv", "text/csv", width="stretch")
with t3:
    st.dataframe(contacts, width="stretch", hide_index=True)
    st.download_button("Export contact CSV", contacts.to_csv(index=False).encode(), "cyber_rakshak_contact.csv", "text/csv", width="stretch")
with t4:
    st.markdown("**Cases**")
    st.dataframe(cases, width="stretch", hide_index=True)
    st.markdown("**Dataset activity**")
    st.dataframe(datasets, width="stretch", hide_index=True)

st.caption("Keep this admin portal private. It exposes registration and investigation metadata to the authorized administrator.")
