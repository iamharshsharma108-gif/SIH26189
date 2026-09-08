import io
import json
import re
import hashlib
import os
import secrets
import sqlite3
import smtplib
from email.message import EmailMessage
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st
import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.ensemble import IsolationForest
    SKLEARN_OK = True
except Exception:
    SKLEARN_OK = False

st.set_page_config(
    page_title="Cyber Rakshak | Intelligence Workspace",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Unified V3.1.1 — refined professional evidence & network workspace
# ============================================================
st.markdown("""
<style>
:root{
  --bg:#f5f7fb; --surface:#ffffff; --surface2:#f8fafc; --line:#e3e8ef;
  --text:#182230; --muted:#667085; --primary:#2563eb; --primary2:#1d4ed8;
  --green:#15803d; --amber:#b45309; --red:#b42318; --blue-soft:#eff6ff;
}
.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:1480px;padding-top:1rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
[data-testid="stSidebar"] > div:first-child{padding-top:1.1rem}

.cr-brand{display:flex;align-items:center;gap:11px;padding:6px 4px 18px}
.cr-shield{width:38px;height:38px;border-radius:10px;background:#eff6ff;border:1px solid #bfdbfe;display:flex;align-items:center;justify-content:center;font-size:20px}
.cr-brand-title{font-size:18px;font-weight:750;line-height:1.1;color:#101828}
.cr-brand-sub{font-size:11px;color:#667085;margin-top:3px}

.workspace-head{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px 24px;margin-bottom:16px;box-shadow:0 1px 2px rgba(16,24,40,.03)}
.workspace-title{font-size:29px;font-weight:760;letter-spacing:-.5px;color:#101828}
.workspace-sub{font-size:14px;color:#667085;margin-top:5px;max-width:900px;line-height:1.5}

.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 18px 16px;margin-bottom:14px;box-shadow:0 1px 2px rgba(16,24,40,.03)}
.card-title{font-size:16px;font-weight:700;color:#101828;margin-bottom:3px}
.card-sub{font-size:12px;color:#667085;line-height:1.45;margin-bottom:13px}
.section-label{font-size:11px;text-transform:uppercase;letter-spacing:.07em;font-weight:750;color:#667085;margin:2px 0 8px}

.step{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid #eef1f5}
.step:last-child{border-bottom:0}
.step-no{width:25px;height:25px;border-radius:50%;background:#eff6ff;color:#1d4ed8;font-size:12px;font-weight:750;display:flex;align-items:center;justify-content:center;flex:0 0 25px}
.step b{font-size:13px;color:#344054}.step span{font-size:12px;color:#667085;display:block;margin-top:2px;line-height:1.4}

.metric-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;min-height:85px}
.metric-label{font-size:11px;color:#667085}.metric-value{font-size:24px;font-weight:760;color:#101828;margin-top:4px}

.match-head{display:flex;align-items:center;justify-content:space-between;padding-bottom:10px;border-bottom:1px solid #eef1f5;margin-bottom:10px}
.match-count{font-size:13px;font-weight:700;color:#344054}
.evidence-tag{display:inline-block;border-radius:999px;padding:3px 8px;background:#f2f4f7;color:#475467;font-size:10px;font-weight:650}

.notice{background:#f8fafc;border:1px solid #e4e7ec;border-radius:10px;padding:11px 12px;font-size:12px;color:#475467;line-height:1.5}
.notice-blue{background:#eff6ff;border-color:#bfdbfe;color:#1e40af}
.notice-green{background:#f0fdf4;border-color:#bbf7d0;color:#166534}

[data-testid="stFileUploaderDropzone"]{background:#fbfcfe;border:1px dashed #b8c2d1;border-radius:11px}
[data-testid="stFileUploaderDropzone"]:hover{border-color:#2563eb;background:#f8fbff}
.stButton>button{border-radius:8px;font-weight:650;border:1px solid #d0d5dd;min-height:38px}
.stButton>button[kind="primary"]{background:#2563eb;border-color:#2563eb;color:#fff}
.stButton>button[kind="primary"]:hover{background:#1d4ed8;border-color:#1d4ed8}
div[data-baseweb="tab-list"]{gap:5px}
button[data-baseweb="tab"]{font-weight:600}

/* Keep native Streamlit widgets clean and compact */
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px 13px}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;overflow:hidden}
hr{border-color:#e4e7ec}
.footer{color:#98a2b3;text-align:center;font-size:11px;margin-top:26px}

/* CYBER RAKSHAK FINAL — Part 2 is visually distinct, not a separate application. */
.part2-banner{display:flex;align-items:center;gap:11px;background:linear-gradient(90deg,#073b6f,#0e7490);color:#fff;border-radius:12px;padding:10px 14px;margin:0 0 16px;box-shadow:0 8px 22px rgba(7,59,111,.10)}
.part2-banner span{font:800 9px 'JetBrains Mono',monospace;letter-spacing:1.2px;color:#8ee8ec;border-right:1px solid rgba(255,255,255,.24);padding-right:10px}
.part2-banner b{font:800 12px 'Space Grotesk',sans-serif;letter-spacing:.5px}
.part2-banner em{margin-left:auto;font:500 9px 'JetBrains Mono',monospace;color:rgba(255,255,255,.68);font-style:normal}
@media(max-width:800px){.part2-banner{flex-wrap:wrap}.part2-banner em{width:100%;margin-left:0}}
</style>
""", unsafe_allow_html=True)

# Unified Part 1 + Part 2 persistence / email layer
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "server_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "cyber_rakshak.sqlite3"
FEEDBACK_DB_PATH = DATA_DIR / "voxshield_feedback.sqlite3"

# Visual language inspired by the supplied reference screenshots:
# warm paper background, editorial serif headings, muted red action color,
# thin rules, compact mono labels and generous whitespace.
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&family=Source+Serif+4:wght@500;600&display=swap');
:root{--paper:#f3f1eb;--paper2:#fbfaf7;--ink:#17201e;--muted:#68716d;--rule:#d8ddd8;--accent:#9b4f3e;--accent2:#b96854;--green:#4f7567;--dark:#26322e}
.stApp{background:var(--paper)!important;color:var(--ink)!important}.block-container{max-width:1280px!important;padding:0 40px 60px!important}
[data-testid="stSidebar"]{background:#f7f3e9!important;border-right:1px solid var(--rule)!important}.cr-brand-title,.workspace-title,.card-title{font-family:'Source Serif 4',Georgia,serif!important;color:var(--ink)!important}
.workspace-head,.card,.metric-card{background:rgba(250,248,240,.72)!important;border:1px solid var(--rule)!important;box-shadow:none!important;border-radius:2px!important}
.workspace-head{padding:28px 30px!important}.workspace-title{font-size:36px!important;font-weight:400!important;letter-spacing:.2px!important}.workspace-sub,.card-sub{color:#77736a!important}.section-label,.section-number,.metric-label,.footer{font-family:'IBM Plex Mono',monospace!important;letter-spacing:.12em!important}
.step{border-bottom:1px solid var(--rule)!important}.step-no{background:#eee7d9!important;color:var(--accent)!important;border-radius:0!important}.notice,.notice-blue,.notice-green{background:rgba(250,248,240,.7)!important;border:1px solid var(--rule)!important;border-radius:2px!important;color:#5f5b52!important}.notice-blue{border-left:3px solid #70829a!important}.notice-green{border-left:3px solid var(--green)!important}
.stButton>button,.stDownloadButton>button{border-radius:2px!important;background:#eee9dc!important;border:1px solid #cfc7b8!important;color:var(--ink)!important;box-shadow:none!important}.stButton>button[kind="primary"]{background:var(--accent)!important;border-color:var(--accent)!important;color:white!important}.stTextInput input,.stTextArea textarea,.stNumberInput input,.stSelectbox div[data-baseweb="select"]>div{background:#faf8f0!important;border:1px solid #cfc8ba!important;border-radius:2px!important;color:var(--ink)!important}.stDataFrame{border:1px solid var(--rule)!important;border-radius:2px!important}.hero-paper{background:linear-gradient(105deg,#f7efe6 0%,#f7f3e8 52%,#eef1e9 100%);border-bottom:1px solid var(--rule);padding:80px 7% 72px;min-height:540px;display:flex;align-items:center}.hero-grid{width:100%;max-width:1150px;margin:auto;display:grid;grid-template-columns:1.02fr .98fr;gap:70px;align-items:center}.eyebrow{font:500 12px 'IBM Plex Mono',monospace;letter-spacing:.16em;text-transform:uppercase;color:#9a5147}.hero-paper h1{font:400 58px/1.02 'Source Serif 4',Georgia,serif;letter-spacing:-1px;margin:14px 0 18px;max-width:650px}.hero-paper p{font:400 16px/1.7 'IBM Plex Sans',sans-serif;color:#6e6a61;max-width:620px}.hero-actions{display:flex;gap:12px;margin-top:25px}.hero-btn{display:inline-block;padding:12px 20px;background:var(--accent);color:#fff;text-decoration:none;font-weight:700;border-radius:2px}.hero-secondary{display:inline-block;padding:12px 20px;background:#eee8db;color:#49453e;text-decoration:none;font-weight:700;border-radius:2px}.graph-card{background:#3d403c;border:7px solid #3d403c;border-radius:4px;padding:24px;min-height:300px;transform:rotate(-1deg);box-shadow:10px 14px 30px rgba(60,55,45,.12)}.graph-inner{height:250px;background:#f7f3e8;position:relative;overflow:hidden}.dot{position:absolute;width:13px;height:13px;border-radius:50%;background:#55708a;border:3px solid #dce5ec}.dot.r{background:#b94437}.line{position:absolute;height:1px;background:#b9b7af;transform-origin:left center}.hero-foot{font:400 11px 'IBM Plex Mono',monospace;color:#8b867b;margin-top:18px}.section-paper{max-width:1080px;margin:0 auto;padding:80px 20px}.section-kicker{font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.16em;color:#9a5147;text-transform:uppercase}.section-paper h2{font:400 40px/1.1 'Source Serif 4',Georgia,serif;margin:12px 0 38px}.cap-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}.cap{padding:26px 22px;border-right:1px solid var(--rule)}.cap:last-child{border-right:0}.cap-no{font:500 11px 'IBM Plex Mono',monospace;color:#b66a60}.cap h3{font:400 19px 'Source Serif 4',Georgia,serif;margin:22px 0 9px}.cap p{font:13px/1.6 'IBM Plex Sans',sans-serif;color:#77736a}.flow-grid{display:grid;grid-template-columns:repeat(5,1fr);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}.flow{padding:22px 14px;border-right:1px solid var(--rule)}.flow:last-child{border-right:0}.flow-no{font:500 10px 'IBM Plex Mono',monospace;color:#a56b62}.flow h3{font:400 19px 'Source Serif 4',Georgia,serif;margin:14px 0 6px}.flow p{font:12px/1.5 'IBM Plex Sans',sans-serif;color:#8a857a}.paper-footer{border-top:1px solid var(--rule);max-width:1080px;margin:auto;padding:28px 20px 50px;display:flex;justify-content:space-between;gap:20px;color:#77736a;font:11px 'IBM Plex Mono',monospace}.auth-page{min-height:calc(100vh - 80px);display:flex;align-items:center;justify-content:center;background:linear-gradient(115deg,#f5eee5,#f8f5eb,#eef0e9);padding:40px 20px}.auth-card{width:440px;background:#faf8f0;border:1px solid #d8d1c3;border-radius:3px;padding:34px 34px 28px;box-shadow:0 18px 45px rgba(55,50,42,.09)}.auth-brand{text-align:center;font:400 25px 'Source Serif 4',Georgia,serif;letter-spacing:.04em}.auth-tag{text-align:center;font:500 9px 'IBM Plex Mono',monospace;letter-spacing:.18em;color:#9b968b;margin-top:5px}.auth-kicker{font:500 10px 'IBM Plex Mono',monospace;letter-spacing:.15em;color:#9a5147;text-transform:uppercase;margin-top:30px}.auth-title{font:400 34px 'Source Serif 4',Georgia,serif;margin:6px 0 8px}.auth-copy{font:13px/1.55 'IBM Plex Sans',sans-serif;color:#77736a;margin-bottom:20px}.auth-divider{display:flex;align-items:center;gap:10px;color:#a39d91;font:10px 'IBM Plex Mono',monospace;margin:18px 0}.auth-divider:before,.auth-divider:after{content:'';height:1px;background:var(--rule);flex:1}.auth-foot{font:11px/1.5 'IBM Plex Sans',sans-serif;color:#8a857b;margin-top:18px;text-align:center}.top-public{height:1px;background:#56564f}.signed-in{font:10px 'IBM Plex Mono',monospace;color:#77736a;padding:5px 0}.ref-quote{font:400 22px/1.35 'Source Serif 4',Georgia,serif;color:#3c3932;border-left:2px solid var(--accent);padding-left:18px}

.public-nav{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--rule);padding:18px 4px 14px;margin-bottom:28px}.pub-logo{font:600 18px 'Source Serif 4',Georgia,serif;letter-spacing:.04em}.pub-sub{font:500 9px 'IBM Plex Mono',monospace;letter-spacing:.12em;color:var(--muted);margin-top:3px}.pub-status{font:500 10px 'IBM Plex Mono',monospace;letter-spacing:.08em;color:var(--green)}
.top-auth-card{background:var(--paper2);border:1px solid var(--rule);padding:18px 18px 15px;margin-bottom:8px}.top-auth-label{font:500 10px 'IBM Plex Mono',monospace;letter-spacing:.12em;color:var(--accent)}.top-auth-copy{font:500 13px 'IBM Plex Sans',sans-serif;color:var(--ink);margin-top:7px;line-height:1.45}
.hero-paper{padding:34px 0 24px}.hero-paper h1{font:600 58px/1.03 'Source Serif 4',Georgia,serif;letter-spacing:-.03em;margin:12px 0 18px;color:var(--ink)}.hero-paper p{font:400 16px/1.65 'IBM Plex Sans',sans-serif;color:var(--muted);max-width:760px}.eyebrow,.panel-kicker,.sidebar-kicker{font:500 10px 'IBM Plex Mono',monospace;letter-spacing:.14em;color:var(--accent);text-transform:uppercase}
.hero-panel{display:grid;grid-template-columns:1.2fr .8fr;gap:30px;align-items:center;background:#e9ece6;border:1px solid #d1d7d0;padding:28px;margin:12px 0 10px}.panel-title{font:600 31px/1.18 'Source Serif 4',Georgia,serif;margin:10px 0;color:var(--dark)}.panel-note{font:400 13px/1.6 'IBM Plex Sans',sans-serif;color:#68716d;max-width:640px}.signal-board{height:250px;background:#26322e;position:relative;overflow:hidden;border-radius:3px}.signal-node{position:absolute;padding:7px 10px;border:1px solid #a8b8ae;background:#f2f4ef;color:#26322e;font:500 9px 'IBM Plex Mono',monospace;letter-spacing:.06em}.n1{left:8%;top:20%}.n2{left:62%;top:28%}.n3{left:15%;top:68%}.n4{left:67%;top:72%}.signal-center{position:absolute;left:42%;top:47%;color:#f2f4ef;font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.14em}.signal-line{position:absolute;height:1px;background:#8da096;transform-origin:left center}.l1{left:23%;top:31%;width:170px;transform:rotate(5deg)}.l2{left:25%;top:72%;width:170px;transform:rotate(-18deg)}.l3{left:68%;top:39%;width:85px;transform:rotate(102deg)}
.responsible-box{border-left:3px solid var(--accent);background:var(--paper2);border-top:1px solid var(--rule);border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:22px}.responsible-title{font:600 28px 'Source Serif 4',Georgia,serif;margin:8px 0}.responsible-box p{font:400 13px/1.6 'IBM Plex Sans',sans-serif;color:var(--muted);max-width:820px}.auth-shell{min-height:calc(100vh - 70px);display:flex;align-items:center;justify-content:center;padding:50px 15px}.auth-card{width:470px;background:var(--paper2);border:1px solid var(--rule);border-radius:8px;padding:34px 34px 26px;box-shadow:0 20px 55px rgba(38,50,46,.10)}.auth-brand{text-align:center;font:600 27px 'Source Serif 4',Georgia,serif;letter-spacing:.03em}.auth-tag{text-align:center;font:500 9px 'IBM Plex Mono',monospace;letter-spacing:.16em;color:var(--muted);margin-top:5px}.auth-kicker{font:500 10px 'IBM Plex Mono',monospace;letter-spacing:.14em;color:var(--accent);margin-top:30px}.auth-title{font:600 36px 'Source Serif 4',Georgia,serif;margin:7px 0 8px}.auth-copy{font:400 13px/1.55 'IBM Plex Sans',sans-serif;color:var(--muted);margin-bottom:20px}.auth-foot{font:400 11px/1.5 'IBM Plex Sans',sans-serif;color:#7d8581;margin-top:14px;text-align:center}.workspace-brandline{display:flex;align-items:center;gap:9px;padding:5px 0 14px;color:#58635f;font:500 10px 'IBM Plex Mono',monospace;letter-spacing:.08em}.brand-mark{display:inline-flex;width:25px;height:25px;align-items:center;justify-content:center;border:1px solid #c6cec7;background:#e9ece6;color:var(--dark);font:600 9px 'IBM Plex Mono',monospace}.brand-divider{color:#a0a8a4}.sidebar-kicker{font-size:9px;margin:8px 0}.sidebar-rule{height:1px;background:var(--rule);margin:14px 0}.signed-in{font:400 10px/1.55 'IBM Plex Mono',monospace;color:#68716d}
@media(max-width:900px){.hero-grid{grid-template-columns:1fr;gap:35px}.hero-paper h1{font-size:44px}.cap-grid,.flow-grid{grid-template-columns:1fr}.cap,.flow{border-right:0;border-bottom:1px solid var(--rule)}.block-container{padding:0 16px 40px!important}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Unified V3.1.1 visual refinement layer
# ============================================================
st.markdown(r"""
<style>
/* Keep the original V3 warm editorial identity; refine spacing, hierarchy and controls. */
.block-container{max-width:1320px!important;padding:18px 44px 64px!important}
[data-testid="stSidebar"]{background:#f6f1e7!important;border-right:1px solid #d9d4ca!important}
[data-testid="stSidebar"] > div:first-child{padding:18px 14px 22px!important}
.cr-brand{padding:4px 8px 20px!important;border-bottom:1px solid #d9d4ca;margin-bottom:14px}
.cr-shield{width:36px!important;height:36px!important;border-radius:3px!important;background:#ece7dc!important;border:1px solid #cfc7b8!important;color:#26322e!important;font-family:'IBM Plex Mono',monospace!important;font-size:15px!important}
.cr-brand-title{font-size:22px!important;letter-spacing:-.02em!important}
.cr-brand-sub{font-family:'IBM Plex Mono',monospace!important;font-size:9px!important;letter-spacing:.08em!important;text-transform:uppercase!important;color:#817c72!important}
.sidebar-section{font:500 9px 'IBM Plex Mono',monospace;color:#918a7d;letter-spacing:.16em;text-transform:uppercase;margin:18px 7px 7px}
.sidebar-case{background:#fbf8f0;border:1px solid #d9d4ca;border-radius:3px;padding:10px 11px;margin:8px 0 12px}
.sidebar-case .case-id{font:500 9px 'IBM Plex Mono',monospace;color:#9b4f3e;letter-spacing:.1em}
.sidebar-case .case-title{font:500 13px 'IBM Plex Sans',sans-serif;color:#373630;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sidebar-rule{background:#d9d4ca!important;margin:15px 0!important}
[data-testid="stSidebar"] div[role="radiogroup"]{gap:2px!important}
[data-testid="stSidebar"] div[role="radiogroup"] label{border-radius:3px!important;padding:5px 8px!important;color:#625f58!important;font-size:12px!important;transition:all .12s ease}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:#ebe5d9!important;color:#302f2b!important}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){background:#e8dfd2!important;color:#8f4638!important;font-weight:700!important}
[data-testid="stSidebar"] .stSelectbox>div>div{background:#fbf8f0!important;border:1px solid #d1c9bb!important;border-radius:3px!important}
[data-testid="stSidebar"] .stButton>button{min-height:34px!important;border-radius:3px!important;background:#eee8dc!important;border-color:#d0c8ba!important;font-size:11px!important}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:#9b4f3e!important;border-color:#9b4f3e!important;color:white!important}
.workspace-brandline{height:34px;margin:0 0 12px!important;border-bottom:1px solid #d8ddd8;padding-bottom:9px!important}
.brand-mark{width:24px!important;height:24px!important;border-radius:2px!important;background:#ece7dc!important}
.workspace-head{margin-bottom:18px!important}
.workspace-title{line-height:1.05!important}
.metric-card{min-height:92px!important;padding:16px 18px!important;position:relative;overflow:hidden}
.metric-card:before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:#9b4f3e}
.metric-label{font-size:10px!important;text-transform:uppercase!important;letter-spacing:.08em!important}
.metric-value{font-family:'IBM Plex Sans',sans-serif!important;font-size:27px!important;font-weight:600!important}
.card{padding:21px 21px 18px!important}
.card-title{font-size:20px!important;line-height:1.2!important}
.section-kicker{margin-bottom:3px!important}
.stButton>button,.stDownloadButton>button{min-height:38px!important;padding:0 15px!important}
.stTextInput input,.stTextArea textarea,.stNumberInput input{min-height:40px!important}
[data-testid="stDataFrame"]{background:#fbf8f0!important}
div[data-baseweb="tab-list"]{border-bottom:1px solid #d8d2c6!important;padding-bottom:2px!important}
button[data-baseweb="tab"]{font-family:'IBM Plex Sans',sans-serif!important;font-size:12px!important;color:#706c63!important}
button[data-baseweb="tab"][aria-selected="true"]{color:#9b4f3e!important}
.stAlert{border-radius:3px!important}
.footer{border-top:1px solid #d8d2c6;padding-top:16px!important}
@media(max-width:900px){.block-container{padding:14px 18px 45px!important}.workspace-title{font-size:30px!important}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FINAL RESPONSIVE / ACCESSIBILITY OVERRIDE
# ============================================================
st.markdown(r"""
<style>
/* Final representative build: one visual system, high contrast, mobile first. */
html, body, [data-testid="stAppViewContainer"]{overflow-x:hidden!important;}
.stApp{color:#17202b!important;}
.block-container{width:100%!important;max-width:1240px!important;margin:0 auto!important;padding:12px 22px 42px!important;}

/* Public page: compact hierarchy and no oversized dead space. */
.public-nav{padding:10px 0 9px!important;margin-bottom:10px!important;min-height:44px;}
.top-auth-card{padding:10px 13px!important;margin-bottom:9px!important;}
.top-auth-copy{font-size:12px!important;margin-top:4px!important;}
.hero-paper{padding:25px 0 20px!important;min-height:0!important;background:linear-gradient(105deg,#f7efe6 0%,#f7f3e8 52%,#eef1e9 100%)!important;}
.hero-paper h1{font-size:46px!important;line-height:1.02!important;margin:8px 0 10px!important;}
.hero-paper p{font-size:14px!important;line-height:1.5!important;margin:0!important;max-width:760px!important;}
.hero-panel{grid-template-columns:minmax(0,1.2fr) minmax(260px,.8fr)!important;gap:20px!important;padding:18px!important;margin:10px 0!important;}
.panel-title{font-size:25px!important;}
.panel-note{font-size:12px!important;}
.signal-board{min-height:210px!important;height:210px!important;}
.section-paper{padding:38px 10px!important;}
.section-paper h2{font-size:30px!important;margin:8px 0 22px!important;}
.cap,.flow{padding:18px 14px!important;}
.paper-footer{padding:20px 10px 30px!important;}

/* Public auth controls: both actions remain obvious in light mode. */
.public-nav + * .stButton>button, .top-auth-card ~ * .stButton>button{min-height:40px!important;}

/* Workspace controls: never use low-contrast beige for the important action. */
.stButton>button[kind="primary"], .stFormSubmitButton>button[kind="primary"],
.stDownloadButton>button[kind="primary"]{background:#0b4c8d!important;border-color:#0b4c8d!important;color:#fff!important;}
.stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primary"]:hover{background:#073b6f!important;color:#fff!important;}
.stButton>button:not([kind="primary"]),.stDownloadButton>button:not([kind="primary"]){background:#ffffff!important;color:#17324d!important;border:1px solid #aebdca!important;}

/* Tabs stay visible on light backgrounds and wrap instead of disappearing. */
div[data-baseweb="tab-list"]{background:#f4f7fa!important;border:1px solid #d7e0e8!important;border-radius:9px!important;padding:4px!important;gap:4px!important;overflow-x:auto!important;scrollbar-width:none!important;}
div[data-baseweb="tab-list"]::-webkit-scrollbar{display:none!important;}
button[data-baseweb="tab"]{color:#425466!important;background:transparent!important;min-height:38px!important;padding:7px 12px!important;border-radius:7px!important;font-weight:700!important;white-space:nowrap!important;}
button[data-baseweb="tab"][aria-selected="true"]{background:#073b6f!important;color:#fff!important;}

/* Auth screen: visible on phones/tablets and light/dark safe. */
.st-key-auth_card{box-sizing:border-box!important;width:min(500px,100%)!important;background:#fff!important;color:#17202b!important;}
.st-key-auth_card [data-baseweb="tab-list"]{display:flex!important;width:100%!important;}
.st-key-auth_card [data-baseweb="tab"]{flex:1 1 50%!important;min-width:0!important;}
.st-key-auth_card button[kind="primary"]{background:#073b6f!important;color:#fff!important;border-color:#073b6f!important;}
.st-key-auth_card button[kind="secondary"]{background:#fff!important;color:#17324d!important;border-color:#aebdca!important;}
.st-key-auth_card input{color:#17202b!important;background:#fff!important;}

/* Prevent wide graphs/cards from forcing a phone into horizontal scrolling. */
.card,.workspace-head,.hero-panel,.metric-card,.notice,.responsible-box{max-width:100%!important;box-sizing:border-box!important;}
[data-testid="stDataFrame"],.stDataFrame{max-width:100%!important;overflow:auto!important;}
img,svg,canvas{max-width:100%;}

@media(max-width:900px){
  .block-container{padding:10px 14px 34px!important;}
  .hero-grid{grid-template-columns:1fr!important;gap:15px!important;}
  .hero-paper h1{font-size:38px!important;}
  .hero-panel{grid-template-columns:1fr!important;gap:14px!important;}
  .signal-board{height:185px!important;min-height:185px!important;}
  .cap-grid,.flow-grid{grid-template-columns:1fr 1fr!important;}
  .workspace-title{font-size:29px!important;}
  .workspace-head{padding:17px 16px!important;}
  .card{padding:16px!important;}
}
@media(max-width:640px){
  .block-container{padding:8px 10px 28px!important;}
  .public-nav{align-items:flex-start!important;}
  .pub-logo{font-size:16px!important;}
  .pub-status{font-size:8px!important;}
  .hero-paper{padding:18px 0 15px!important;}
  .hero-paper h1{font-size:32px!important;letter-spacing:-.02em!important;}
  .hero-paper p{font-size:13px!important;}
  .hero-actions{display:grid!important;grid-template-columns:1fr!important;}
  .hero-panel{padding:13px!important;}
  .panel-title{font-size:22px!important;}
  .signal-board{height:155px!important;min-height:155px!important;}
  .cap-grid,.flow-grid{grid-template-columns:1fr!important;}
  .section-paper{padding:28px 4px!important;}
  .section-paper h2{font-size:26px!important;}
  .paper-footer{display:block!important;}
  .paper-footer span{display:block!important;margin:5px 0!important;}
  .st-key-auth_card{padding:7px 14px 18px!important;border-radius:14px!important;}
  .st-key-auth_card [data-baseweb="tab"]{font-size:11px!important;padding:8px 5px!important;}
  .auth-title{font-size:23px!important;}
  .auth-sub{font-size:11px!important;}
  .head_left,.head_mid,.head_right{min-width:0!important;}
  [data-testid="stHorizontalBlock"]{min-width:0!important;}
  .metric-card{min-height:72px!important;padding:12px!important;}
  .metric-value{font-size:22px!important;}
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Final typography/accessibility refinement — preserve the established classic identity.
st.markdown(r"""
<style>
/* FINAL TYPOGRAPHY: classic editorial headings + clean readable controls */
html,body,[data-testid="stAppViewContainer"],[data-testid="stSidebar"]{
  font-family:"Georgia","Times New Roman","Noto Serif Devanagari","Noto Serif Tamil","Noto Serif Bengali",serif!important;
}
.stApp p,.stApp label,.stApp input,.stApp textarea,.stApp select,.stApp button,.stApp [data-baseweb="select"],.stApp [data-testid="stCaptionContainer"]{
  font-family:"Segoe UI","Noto Sans Devanagari","Noto Sans Tamil","Noto Sans Bengali",Arial,sans-serif!important;
}
.workspace-title,.card-title,.panel-title,.responsible-title,.auth-title,.hero-paper h1{
  font-family:"Georgia","Times New Roman","Noto Serif Devanagari","Noto Serif Tamil","Noto Serif Bengali",serif!important;
  font-weight:700!important;
  letter-spacing:.01em!important;
}
.workspace-title{font-size:34px!important;text-transform:uppercase!important;line-height:1.12!important;color:#182230!important;}
.card-title{font-size:20px!important;text-transform:none!important;}
.section-kicker,.section-label,.sidebar-section,.metric-label,.panel-kicker,.eyebrow{
  font-family:"Segoe UI","Noto Sans Devanagari","Noto Sans Tamil","Noto Sans Bengali",Arial,sans-serif!important;
  font-weight:800!important;letter-spacing:.12em!important;text-transform:uppercase!important;
}
.workspace-head{background:#fbfaf7!important;border:1px solid #d8d1c3!important;border-radius:4px!important;padding:24px 28px!important;box-shadow:0 2px 10px rgba(38,50,46,.035)!important;}
.workspace-sub{font-family:"Segoe UI","Noto Sans Devanagari","Noto Sans Tamil","Noto Sans Bengali",Arial,sans-serif!important;font-size:13px!important;line-height:1.65!important;color:#625f58!important;}
.stButton>button,.stDownloadButton>button{font-family:"Segoe UI","Noto Sans Devanagari","Noto Sans Tamil","Noto Sans Bengali",Arial,sans-serif!important;font-weight:700!important;letter-spacing:.01em!important;}
[data-testid="stSidebar"] div[role="radiogroup"] label{font-family:"Segoe UI","Noto Sans Devanagari","Noto Sans Tamil","Noto Sans Bengali",Arial,sans-serif!important;}
/* Make the language control obvious and ensure the selected language rerenders cleanly. */
[data-testid="stSidebar"] .stSelectbox label{font-weight:800!important;}
/* Better mobile/tablet layout */
@media(max-width:900px){
  .block-container{padding:12px 14px 38px!important;}
  .workspace-head{padding:20px 18px!important;}
  .workspace-title{font-size:28px!important;}
  .workspace-sub{font-size:12px!important;}
}
@media(max-width:600px){
  .workspace-title{font-size:24px!important;}
  .card-title{font-size:18px!important;}
  .stButton>button,.stDownloadButton>button{min-height:42px!important;}
}
</style>
""", unsafe_allow_html=True)



# Utilities / data model
# ============================================================

def norm_phone(v):
    if pd.isna(v): return ""
    digits = re.sub(r"\D", "", str(v).strip())
    if len(digits) == 10: return "+91" + digits
    if digits.startswith("91") and len(digits) >= 12: return "+" + digits
    return "+" + digits if digits else ""


def norm_email(v):
    if pd.isna(v): return ""
    return str(v).strip().lower()


def norm_account(v):
    if pd.isna(v): return ""
    return re.sub(r"[^A-Z0-9_-]", "", str(v).strip().upper())


def norm_ip(v):
    if pd.isna(v): return ""
    return str(v).strip()


def norm_domain(v):
    if pd.isna(v): return ""
    s = str(v).strip().lower()
    if not s: return ""
    if "://" not in s: s = "https://" + s
    try: return urlparse(s).hostname or ""
    except Exception: return s


def norm_url(v):
    if pd.isna(v): return ""
    s = str(v).strip()
    if not s: return ""
    if "://" not in s: s = "https://" + s
    try:
        p = urlparse(s)
        return urlunparse((p.scheme.lower(), (p.hostname or "").lower(), p.path.rstrip("/"), "", "", ""))
    except Exception: return s.lower().rstrip("/")


def canonical_type(col):
    c = re.sub(r"[^a-z0-9]", "", str(col).lower())
    rules = [
        ("phone", ["phone","mobile","msisdn","contact","mobileno","phonenumber"]),
        ("email", ["email","mailid","emailid"]),
        ("account", ["account","accountno","accountnumber","acct","upiaccount"]),
        ("sender", ["sender","fromaccount","payer","debitaccount"]),
        ("receiver", ["receiver","toaccount","payee","creditaccount","beneficiary"]),
        ("ip", ["ip","sourceip","destinationip","srcip","dstip","ipaddress"]),
        ("domain", ["domain","host","hostname"]),
        ("url", ["url","link","uri","website"]),
        ("device", ["device","deviceid","imei","machineid","hostid"]),
        ("timestamp", ["timestamp","time","datetime","eventtime","date","createdat"]),
        ("txid", ["transactionid","txid","paymentid","reference","utr"]),
        ("amount", ["amount","value","transactionamount"]),
        ("hash", ["hash","sha256","md5","filehash"]),
        ("entity", ["entityid","entityidentifier"]),
        ("incident", ["incident","caseid","alertid","eventid"]),
    ]
    for typ, keys in rules:
        if any(k in c for k in keys): return typ
    return "other"


def infer_columns(df):
    return {c: canonical_type(c) for c in df.columns}


def read_upload(upload):
    name = upload.name.lower()
    if name.endswith(".csv"): return pd.read_csv(upload)
    if name.endswith((".xlsx", ".xls")): return pd.read_excel(upload)
    if name.endswith(".json"):
        return pd.DataFrame(json.loads(upload.read()))
    if name.endswith(".txt"):
        return pd.read_csv(upload, sep=None, engine="python")
    raise ValueError("Supported formats: CSV, XLSX, XLS, JSON, TXT")


def synthetic_data():
    entities = [{"entity_id":f"ENT-{i:03d}","label":f"Entity {i:03d}","entity_type":"Entity"} for i in range(1,31)]
    phones = [{"phone":f"+91987654{i:04d}","entity_id":f"ENT-{((i-1)%12)+1:03d}","source":"Synthetic Telecom Export"} for i in range(1,19)]
    emails = [{"email":f"entity{i:03d}@example.invalid","entity_id":f"ENT-{((i-1)%12)+1:03d}","source":"Synthetic Email Export"} for i in range(1,19)]
    accounts = [{"account":f"ACC-{1000+i:04d}","entity_id":f"ENT-{((i-1)%12)+1:03d}","source":"Synthetic Bank Export"} for i in range(1,25)]
    devices = [{"device_id":f"DEV-{100+i:04d}","entity_id":f"ENT-{((i-1)%12)+1:03d}","source":"Synthetic Login Export"} for i in range(1,17)]
    tx=[]
    links=[(1,2,5200),(1,3,7400),(2,4,3100),(3,4,6900),(4,5,2800),(5,6,4100),(2,6,1900),(6,7,8300),(7,8,2700),(8,9,6100),(3,9,2200),(9,10,4700),(10,11,1800),(11,12,3600),(4,12,1500)]
    for n,(a,b,amt) in enumerate(links,1):
        tx.append({"transaction_id":f"TX-{n:04d}","sender":f"ACC-{1000+a:04d}","receiver":f"ACC-{1000+b:04d}","amount":amt,"timestamp":f"2026-09-{10+n//5:02d} {8+(n%10):02d}:{(n*7)%60:02d}:00","phone":phones[(a-1)%len(phones)]["phone"]})
    cyber=[]
    paths=[("10.10.1.12","203.0.113.10","portal-a.example.invalid","INC-001"),("10.10.1.13","203.0.113.10","portal-b.example.invalid","INC-002"),("10.10.1.13","203.0.113.20","portal-c.example.invalid","INC-002"),("10.10.2.44","203.0.113.20","portal-c.example.invalid","INC-003"),("10.10.2.44","203.0.113.30","portal-d.example.invalid","INC-003"),("10.10.3.55","203.0.113.30","portal-d.example.invalid","INC-004")]
    for i,(src,dst,dom,inc) in enumerate(paths,1):
        cyber.append({"source_ip":src,"destination_ip":dst,"domain":dom,"incident_id":inc,"timestamp":f"2026-09-{10+i:02d} {10+i:02d}:15:00","source":"Synthetic Security Logs"})
    return {"entities":pd.DataFrame(entities),"phones":pd.DataFrame(phones),"emails":pd.DataFrame(emails),"accounts":pd.DataFrame(accounts),"devices":pd.DataFrame(devices),"transactions":pd.DataFrame(tx),"cyber":pd.DataFrame(cyber)}


def bundled_demo_data():
    """Load the optional structured synthetic demo pack shipped beside the app."""
    root=APP_DIR / "demo_data"
    if not root.exists(): return {}
    out={}
    for p in sorted(root.glob("*.csv")):
        try: out[p.stem]=pd.read_csv(p)
        except Exception: continue
    return out


def ensure_state():
    if "datasets" not in st.session_state: st.session_state.datasets={}
    if "ledger" not in st.session_state: st.session_state.ledger=[]
    if "loaded_demo" not in st.session_state: st.session_state.loaded_demo=False


def add_dataset(name, df, source="Uploaded Dataset"):
    df=df.copy(); df.columns=[str(c).strip() for c in df.columns]
    st.session_state.datasets[name]=df
    st.session_state.data_revision=st.session_state.get("data_revision",0)+1
    st.session_state.ledger.append({"dataset":name,"source":source,"records":len(df),"ingested_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    if st.session_state.get('keep_session_data', True):
        save_session_data()
    if st.session_state.get("auth_user") and st.session_state.get("case"):
        log_dataset_server(st.session_state.auth_user,st.session_state.case["id"],name,source,df)
        save_case_server(st.session_state.auth_user,st.session_state.case)


def all_frames(): return st.session_state.datasets


def evidence_hash(row):
    return hashlib.sha256(json.dumps(row,sort_keys=True,default=str).encode()).hexdigest()[:12].upper()


def search_identifier(q, mode="Auto"):
    nq=q.strip().lower(); results=[]
    for name,df in all_frames().items():
        for col in df.columns:
            typ=canonical_type(col)
            for idx,val in df[col].items():
                raw=str(val)
                if mode=="Phone normalized" or (mode=="Auto" and typ=="phone"):
                    match=norm_phone(val)==norm_phone(q)
                elif mode=="Email normalized" or (mode=="Auto" and typ=="email"):
                    match=norm_email(val)==norm_email(q)
                elif mode=="Account normalized" or (mode=="Auto" and typ in ("account","sender","receiver")):
                    match=norm_account(val)==norm_account(q)
                elif mode=="IP normalized" or (mode=="Auto" and typ=="ip"):
                    match=norm_ip(val)==norm_ip(q)
                elif mode=="Domain normalized" or (mode=="Auto" and typ=="domain"):
                    match=norm_domain(val)==norm_domain(q)
                else:
                    match=raw.strip().lower()==nq
                if match:
                    results.append({"dataset":name,"record":idx,"field":col,"type":typ,"matched_value":raw,"evidence_id":"EVD-"+evidence_hash({"d":name,"r":idx,"c":col,"v":raw})})
    return pd.DataFrame(results)


def build_graph(kind="all"):
    G=nx.MultiGraph(); ds=all_frames()
    def node(n,typ,label=None):
        if n:
            n=str(n); G.add_node(n,node_type=typ,label=label or n)
    if kind=="all":
        # Generic entity-centric relationships used by structured demo packs and exports.
        for name,df in ds.items():
            mp=infer_columns(df)
            ent_cols=[c for c,t in mp.items() if t=="entity"]
            src_cols=[c for c in df.columns if re.sub(r"[^a-z0-9]","",str(c).lower())=="sourceentity"]
            dst_cols=[c for c in df.columns if re.sub(r"[^a-z0-9]","",str(c).lower())=="targetentity"]
            if src_cols and dst_cols:
                for _,r in df.iterrows():
                    a=str(r[src_cols[0]]).strip(); b=str(r[dst_cols[0]]).strip()
                    if a and b and a.lower()!='nan' and b.lower()!='nan':
                        node(a,"ENTITY"); node(b,"ENTITY")
                        rel=str(r.get(next((c for c in df.columns if re.sub(r"[^a-z0-9]","",str(c).lower())=="relationshiptype"),""),"RELATED"))
                        src=str(r.get(next((c for c in df.columns if re.sub(r"[^a-z0-9]","",str(c).lower())=="source"),""),name))
                        G.add_edge(a,b,rel=rel or "RELATED",source=src or name)
            for _,r in df.iterrows():
                for ec in ent_cols:
                    entity=str(r[ec]).strip()
                    if not entity or entity.lower()=='nan': continue
                    node(entity,"ENTITY")
                    for c,t in mp.items():
                        if c==ec or t in ("other","timestamp","amount","txid","entity"): continue
                        val=str(r[c]).strip()
                        if not val or val.lower()=='nan': continue
                        if t=="phone": val=norm_phone(r[c])
                        elif t=="email": val=norm_email(r[c])
                        elif t in ("account","sender","receiver"): val=norm_account(r[c])
                        elif t=="domain": val=norm_domain(r[c])
                        elif t=="url": val=norm_url(r[c])
                        elif t=="ip": val=norm_ip(r[c])
                        elif t=="device": val=str(r[c]).strip()
                        node(val,t.upper()); G.add_edge(entity,val,rel="ENTITY_ATTRIBUTE",source=name)
    if kind in ("all","financial"):
        for name,df in ds.items():
            mp=infer_columns(df)
            sender=[c for c,t in mp.items() if t=="sender"]; receiver=[c for c,t in mp.items() if t=="receiver"]
            account=[c for c,t in mp.items() if t=="account"]; phone=[c for c,t in mp.items() if t=="phone"]; email=[c for c,t in mp.items() if t=="email"]
            if sender and receiver:
                for _,r in df.iterrows():
                    a=norm_account(r[sender[0]]); b=norm_account(r[receiver[0]])
                    if a and b:
                        node(a,"ACCOUNT"); node(b,"ACCOUNT")
                        G.add_edge(a,b,rel="TRANSACTION",source=name,amount=r.get(next((c for c,t in mp.items() if t=="amount"),""),""))
            if account:
                for _,r in df.iterrows():
                    a=norm_account(r[account[0]])
                    if a:
                        node(a,"ACCOUNT")
                        for c in phone:
                            p=norm_phone(r[c])
                            if p: node(p,"PHONE"); G.add_edge(a,p,rel="ACCOUNT_HAS_PHONE",source=name)
                        for c in email:
                            e=norm_email(r[c])
                            if e: node(e,"EMAIL"); G.add_edge(a,e,rel="ACCOUNT_HAS_EMAIL",source=name)
    if kind in ("all","cyber"):
        for name,df in ds.items():
            mp=infer_columns(df); ips=[c for c,t in mp.items() if t=="ip"]; domains=[c for c,t in mp.items() if t=="domain"]; urls=[c for c,t in mp.items() if t=="url"]; incidents=[c for c,t in mp.items() if t=="incident"]
            src=[c for c in mp if re.sub(r"[^a-z0-9]","",c.lower()) in ("sourceip","srcip")]
            dst=[c for c in mp if re.sub(r"[^a-z0-9]","",c.lower()) in ("destinationip","dstip")]
            if src and dst:
                for _,r in df.iterrows():
                    a=norm_ip(r[src[0]]); b=norm_ip(r[dst[0]])
                    if a and b: node(a,"IP"); node(b,"IP"); G.add_edge(a,b,rel="OBSERVED_FLOW",source=name)
            for _,r in df.iterrows():
                for c in domains:
                    d=norm_domain(r[c])
                    if d:
                        node(d,"DOMAIN")
                        for c2 in ips:
                            ip=norm_ip(r[c2])
                            if ip: node(ip,"IP"); G.add_edge(d,ip,rel="DOMAIN_OBSERVED_WITH_IP",source=name)
                for c in urls:
                    u=norm_url(r[c])
                    if u:
                        node(u,"URL")
                        for c2 in domains:
                            d=norm_domain(r[c2])
                            if d: node(d,"DOMAIN"); G.add_edge(u,d,rel="URL_ON_DOMAIN",source=name)
                for c in incidents:
                    inc=str(r[c]).strip()
                    if inc:
                        node(inc,"INCIDENT")
                        for c2 in domains:
                            d=norm_domain(r[c2])
                            if d: node(d,"DOMAIN"); G.add_edge(inc,d,rel="INCIDENT_OBSERVED_DOMAIN",source=name)
                        for c2 in ips:
                            ip=norm_ip(r[c2])
                            if ip: node(ip,"IP"); G.add_edge(inc,ip,rel="INCIDENT_OBSERVED_IP",source=name)
    return G


@st.cache_resource(show_spinner=False)
def cached_graph(session_key, kind, revision):
    # session_key prevents one user's graph from being reused by another user's session.
    return build_graph(kind)

def get_graph(kind="all"):
    return cached_graph(st.session_state.get("graph_session_key",""), kind, st.session_state.get("data_revision",0))


def graph_fig(G, focus=None, max_nodes=90):
    if G.number_of_nodes()==0: return None
    H=G
    if focus and focus in G:
        keep=set(nx.single_source_shortest_path_length(G,focus,cutoff=3).keys()); H=G.subgraph(keep).copy()
    if H.number_of_nodes()>max_nodes:
        top=sorted(H.degree,key=lambda x:x[1],reverse=True)[:max_nodes]; H=H.subgraph([n for n,_ in top]).copy()
    pos=nx.spring_layout(H,seed=7,k=1.25)
    ex=[]; ey=[]
    for a,b in H.edges():
        x0,y0=pos[a]; x1,y1=pos[b]; ex += [x0,x1,None]; ey += [y0,y1,None]
    edge=go.Scatter(x=ex,y=ey,mode="lines",line=dict(width=1,color="#cbd5e1"),hoverinfo="none")
    symbols={"ACCOUNT":"square","PHONE":"circle","EMAIL":"diamond","IP":"triangle-up","DOMAIN":"hexagon","URL":"star","INCIDENT":"x","ENTITY":"circle","Entity":"circle"}
    ns=sorted(H.nodes()); nxv=[]; ny=[]; labels=[]; hovers=[]; syms=[]
    for n in ns:
        x,y=pos[n]; typ=H.nodes[n].get("node_type","Entity"); nxv.append(x); ny.append(y); labels.append(str(n)[:22]); hovers.append(f"{typ} · {n}<br>Connections: {H.degree(n)}"); syms.append(symbols.get(typ,"circle"))
    node=go.Scatter(x=nxv,y=ny,mode="markers+text",text=labels,textposition="top center",hovertext=hovers,hoverinfo="text",marker=dict(size=15,symbol=syms,color="#2563eb",line=dict(width=2,color="#ffffff")))
    fig=go.Figure([edge,node]); fig.update_layout(height=580,showlegend=False,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(visible=False),yaxis=dict(visible=False))
    return fig


def network_signals(G):
    sig=[]
    if not G or not G.nodes: return sig
    deg=dict(G.degree())
    if deg:
        n,maxd=max(deg.items(),key=lambda x:x[1])
        if maxd>=4: sig.append(("Highly connected node",f"{n} has {maxd} observed relationships in the current evidence graph.","amber"))
    if G.number_of_nodes()>2:
        bc=nx.betweenness_centrality(G); n,score=max(bc.items(),key=lambda x:x[1])
        if score>0.15: sig.append(("Bridge candidate",f"{n} sits between otherwise separated portions of the observed network.","blue"))
    comps=list(nx.connected_components(G))
    if len(comps)>1: sig.append(("Separate evidence components",f"The current evidence forms {len(comps)} disconnected components.","blue"))
    return sig


# ============================================================
# Server account / case / email services (Part 1 foundation)
# ============================================================
def db():
    # One server-side database is shared by every Streamlit user hitting this deployment.
    # WAL + busy timeout reduce lock contention when multiple users submit forms together.
    conn=sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
    conn.row_factory=sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=20000")
        conn.execute("PRAGMA foreign_keys=ON")
    except Exception:
        pass
    return conn

def now_str(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

URGENCY=["urgent","immediately","act now","within 1 hour","today only","last warning"]
SECRECY=["keep this secret","keep this between us","delete this","off the books","do not tell anyone","don't tell anyone"]
FINANCE=["transfer","wire","crypto","usdt","gift card","cash","wallet","account","payment","bank"]
IMPERSONATION=["police","arrest","warrant","tax officer","bank security","investigation agency","official notice"]
CREDENTIAL=["login","verify","kyc","password","otp","credential","secure account","sign in"]
REFERENCE_RISK=["send money immediately and keep the transfer secret","verify your account by entering your password and otp","click the secure login link before your account is suspended","split payments into smaller amounts to avoid reporting","delete the messages after the transaction is confirmed","impersonate an authority and pressure the recipient to pay"]
REFERENCE_NORMAL=["meeting is scheduled for tomorrow at ten","please send the invoice through the normal company process","the payment was received and recorded in the ledger","we can discuss the project during the next review"]

def contains_any(text, words):
    t=text.lower(); return [w for w in words if w in t]

def extract_entities(text):
    out=[]; seen=set()
    patterns=[("EMAIL",r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),("PHONE",r"(?:\+91[-\s]?)?[6-9]\d{9}"),("URL",r"https?://[^\s)]+"),("ACCOUNT",r"\b(?:ACC|ACCT|WALLET|TX)[-_A-Z0-9]{4,}\b")]
    for typ,pat in patterns:
        for value in re.findall(pat,text,flags=re.I):
            k=(typ,value)
            if k not in seen: out.append({"type":typ,"value":value}); seen.add(k)
    return out

def semantic_signal(text):
    if not SKLEARN_OK or not text.strip(): return 0,"Semantic model unavailable; lexical indicators used."
    corpus=REFERENCE_RISK+REFERENCE_NORMAL+[text]
    v=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True)
    X=v.fit_transform(corpus); sims=cosine_similarity(X[-1],X[:-1])[0]
    risk=float(np.max(sims[:len(REFERENCE_RISK)])); normal=float(np.max(sims[len(REFERENCE_RISK):])); gap=max(0,risk-normal)
    return int(np.clip(gap*100,0,24)),f"Semantic similarity: risk-pattern {risk:.2f}; baseline-pattern {normal:.2f}."

def analyze_text(text):
    indicators=[]; score=0; groups=0
    for label,words,weight in [("Pressure / urgency",URGENCY,16),("Secrecy / concealment",SECRECY,20),("Financial-transfer context",FINANCE,13),("Authority / impersonation cues",IMPERSONATION,12),("Credential-harvesting context",CREDENTIAL,15)]:
        found=contains_any(text,words)
        if found:
            groups+=1; score+=weight+min(6,len(found)*2); indicators.append(f"{label}: {', '.join(found[:5])}")
    sem,note=semantic_signal(text); score+=sem
    if len(text.split())<8: score=max(0,score-8); indicators.append("Limited text volume reduces analytical confidence.")
    entities=extract_entities(text)
    strength="Strong" if groups>=3 or score>=60 else "Moderate" if groups>=1 or score>=25 else "Weak"
    return {"score":int(np.clip(score,0,100)),"strength":strength,"indicators":indicators or ["No material content indicators detected."],"entities":entities,"explanation":note,"features":{"indicator_groups":groups}}

def normalize_url(url): return url if re.match(r"^https?://",url.strip(),re.I) else "https://"+url.strip()

def analyze_url(url):
    url=normalize_url(url); low=url.lower(); host=re.sub(r"^https?://","",url,flags=re.I).split("/")[0].split(":")[0].lower(); indicators=[]; score=0
    if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$",host): indicators.append("Raw IPv4 host detected."); score+=25
    if "@" in host: indicators.append("@ appears in URL authority and warrants deceptive-URL review."); score+=20
    if len(url)>90: indicators.append("Unusually long URL."); score+=10
    if host.count(".")>=3: indicators.append("Deep subdomain structure."); score+=8
    if any(x in host for x in [".top",".xyz",".tk",".click",".zip",".mov"]): indicators.append("TLD warrants additional reputation checking."); score+=10
    found=contains_any(low,CREDENTIAL)
    if found: indicators.append(f"Credential/verification terms in URL: {', '.join(found[:5])}."); score+=18
    if low.startswith("http://"): indicators.append("HTTP rather than HTTPS."); score+=10
    return {"score":int(np.clip(score,0,100)),"strength":"Strong" if score>=50 else "Moderate" if score>=25 else "Weak","indicators":indicators or ["No structural URL indicators detected."],"entities":[{"type":"DOMAIN","value":host}] if host else [],"explanation":"Local structural URL analysis. Live reputation, registration and threat-intelligence checks require connected external sources.","features":{"credential_terms":len(found)}}

def analyze_audio(text):
    r=analyze_text(text); r["explanation"]="Transcript content is analyzed; no accent, pitch, gender, appearance or vocal identity inference is used. "+r["explanation"]; return r

def analyze_transactions(df):
    req=["Sender","Receiver","Amount","Timestamp"]; missing=[c for c in req if c not in df.columns]
    if missing: return {"score":0,"strength":"Weak","indicators":[f"Missing columns: {', '.join(missing)}"],"entities":[],"explanation":"Supply the required transaction columns.","features":{}}
    w=df.copy(); w["Amount"]=pd.to_numeric(w["Amount"],errors="coerce"); w=w.dropna(subset=["Amount"])
    if w.empty: return {"score":0,"strength":"Weak","indicators":["No numeric transaction amounts available."],"entities":[],"explanation":"No usable transaction records.","features":{}}
    indicators=[]; score=0
    if len(w)>=8 and SKLEARN_OK:
        X=np.column_stack([np.log1p(np.maximum(w["Amount"].to_numpy(float),0)),np.arange(len(w))])
        try:
            labels=IsolationForest(contamination="auto",random_state=42).fit_predict(X); out=int((labels==-1).sum())
            if out: rate=out/len(w); indicators.append(f"Statistical anomaly model marked {out}/{len(w)} records as unusual."); score+=min(35,int(rate*100))
        except Exception: pass
    fan=w.groupby("Sender")["Receiver"].nunique()
    if not fan.empty and int(fan.max())>=5:
        s=fan.idxmax(); indicators.append(f"High fan-out: {s} connects to {int(fan.max())} receivers in this batch."); score+=25
    if len(w)>=5 and w["Amount"].nunique()<=max(2,int(len(w)*.2)): indicators.append("Transaction amounts have low diversity; inspect for repeated-value behavior."); score+=10
    ents=[]
    for col,typ in [("Sender","ACCOUNT"),("Receiver","ACCOUNT")]:
        for v in w[col].dropna().astype(str).unique()[:100]: ents.append({"type":typ,"value":v})
    return {"score":int(np.clip(score,0,100)),"strength":"Strong" if score>=55 else "Moderate" if score>=25 else "Weak","indicators":indicators or ["No material statistical anomalies detected."],"entities":ents,"explanation":"Statistical anomaly and relationship features are used; unusual activity is not proof of criminal conduct.","features":{"records":len(w)}}

def analyze_public(text):
    r=analyze_text(text); r["explanation"]="Public-source text is treated as corroborating context. Source provenance and attribution must be independently verified. "+r["explanation"]; return r

def reliability(source):
    s=(source or "").lower()
    if any(x in s for x in ["registry","official","court","government","verified"]): return 1.0
    if any(x in s for x in ["user supplied","unknown"]): return .72
    return .82

def fusion(evidence):
    if not evidence: return {"score":0,"risk":"NO EVIDENCE","action":"ADD_EVIDENCE","coverage":0,"correlations":[],"entities":[],"corroborated":[],"breakdown":[]}
    source_types=sorted(set(e["type"] for e in evidence)); entity_sources={}; breakdown=[]; all_entities=[]
    for e in evidence:
        a=e["analysis"]; adj=round(a.get("score",0)*reliability(e["source"]),1); breakdown.append({"type":e["type"],"raw":a.get("score",0),"reliability":reliability(e["source"]),"adjusted":adj})
        for ent in a.get("entities",[]):
            key=(ent["type"],ent["value"]); all_entities.append(key); entity_sources.setdefault(key,set()).add(e["type"])
    corroborated=[(k[0],k[1]) for k,v in entity_sources.items() if len(v)>=2]
    base=float(np.mean([x["adjusted"] for x in breakdown])); coverage_bonus=min(15,max(0,(len(source_types)-1)*5)); corr_bonus=min(18,len(corroborated)*3); single_penalty=10 if len(source_types)==1 else 0
    score=int(np.clip(base+coverage_bonus+corr_bonus-single_penalty,0,100))
    correlations=[]
    for typ,val in corroborated[:10]:
        correlations.append({"title":"Cross-source corroboration","finding":f"{typ} '{val}' appears across {len(entity_sources[(typ,val)])} evidence types.","strength":"Strong" if len(entity_sources[(typ,val)])>=3 else "Moderate"})
    if len(source_types)>=3 and score>=45: correlations.append({"title":"Multi-modal convergence","finding":"Three or more evidence modalities show elevated indicators. This supports deeper human review rather than an automatic criminal conclusion.","strength":"Strong"})
    if score>=70 and len(source_types)>=2: risk,action="HIGH INVESTIGATIVE SIGNAL","NETWORK_REVIEW"
    elif score>=40: risk,action="MODERATE INVESTIGATIVE SIGNAL","HUMAN_REVIEW"
    else: risk,action="LOW / INSUFFICIENT SIGNAL","CONTINUE_REVIEW"
    return {"score":score,"risk":risk,"action":action,"coverage":len(source_types),"correlations":correlations,"entities":sorted(set(all_entities)),"corroborated":corroborated,"breakdown":breakdown}

def add_ev(typ,source,raw,analysis):
    print(f"[CYBER RAKSHAK] ingesting evidence type={typ} source={source or 'User supplied'}")
    n=len(st.session_state.evidence)+1
    st.session_state.evidence.append({"id":f"EVD-{n:03d}","type":typ,"source":source or "User supplied","timestamp":now_str(),"raw":raw,"analysis":analysis})
    st.session_state.analysis_run+=1

def lvl(score): return "high" if score>=70 else "moderate" if score>=40 else "low"

def badge(text,level="info"): return f"<span class='badge badge-{level}'>{text}</span>"


# ---------------- STATE / TRANSLATION ----------------
LANGS={"English":"en","हिन्दी":"hi","தமிழ்":"ta","বাংলা":"bn"}

def init_server_db():
    with db() as c:
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, dob TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, email TEXT DEFAULT '')")
        c.execute("CREATE TABLE IF NOT EXISTS login_activity(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, identifier TEXT, method TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL)")
        c.execute("CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT, subject TEXT, aliases TEXT DEFAULT '', description TEXT, priority TEXT, created TEXT, updated_at TEXT, notes TEXT DEFAULT '', FOREIGN KEY(user_id) REFERENCES users(id))")
        cols={r[1] for r in c.execute("PRAGMA table_info(cases)").fetchall()}
        if 'aliases' not in cols: c.execute("ALTER TABLE cases ADD COLUMN aliases TEXT DEFAULT ''")
        if 'notes' not in cols: c.execute("ALTER TABLE cases ADD COLUMN notes TEXT DEFAULT ''")
        c.execute("CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL, ev_code TEXT NOT NULL, type TEXT, source TEXT, raw TEXT, analysis_json TEXT, timestamp TEXT, FOREIGN KEY(case_id) REFERENCES cases(id))")
        c.execute("CREATE TABLE IF NOT EXISTS dataset_log(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, case_id TEXT NOT NULL, dataset TEXT, source TEXT, records INTEGER, columns TEXT, evidence_hash TEXT, created_at TEXT NOT NULL)")
        c.execute("CREATE TABLE IF NOT EXISTS case_notes(id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(case_id) REFERENCES cases(id))")
        c.commit()
    with sqlite3.connect(FEEDBACK_DB_PATH) as c:
        c.execute("CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, category TEXT, rating INTEGER, message TEXT NOT NULL, created_at TEXT NOT NULL)")
        c.execute("CREATE TABLE IF NOT EXISTS contact_notes(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, topic TEXT, message TEXT NOT NULL, created_at TEXT NOT NULL)")
        c.commit()

def hash_password(password,salt=None):
    salt=salt or secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,180000); return salt.hex()+":"+digest.hex()

def verify_password(password,stored):
    try:
        s,d=stored.split(':',1); test=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(s),180000).hex(); return secrets.compare_digest(test,d)
    except Exception: return False

def valid_email(email): return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",email.strip()))

def create_user(username,email,dob,password):
    username=username.strip(); email=email.strip().lower()
    if len(username)<2: return False,"Use a name with at least 2 characters."
    if not valid_email(email): return False,"Enter a valid email address."
    if len(password)<8: return False,"Use a password of at least 8 characters."
    with db() as c:
        try:
            if c.execute("SELECT id FROM users WHERE lower(email)=lower(?)",(email,)).fetchone(): return False,"That email is already linked to an account."
            ts=now_str(); c.execute("INSERT INTO users(username,dob,password_hash,created_at,updated_at,email) VALUES(?,?,?,?,?,?)",(username,dob,hash_password(password),ts,ts,email)); c.commit(); return True,"Account created."
        except sqlite3.IntegrityError: return False,"That username is already in use."

def log_login_activity(user_id, identifier, method, status):
    try:
        with db() as c:
            c.execute("INSERT INTO login_activity(user_id,identifier,method,status,created_at) VALUES(?,?,?,?,?)",(user_id,identifier[:160],method,status,now_str()))
            c.commit()
    except Exception:
        pass

def login_user(identifier,password):
    ident=identifier.strip().lower()
    with db() as c: row=c.execute("SELECT * FROM users WHERE lower(username)=? OR lower(email)=?",(ident,ident)).fetchone()
    if row and verify_password(password,row['password_hash']):
        user=dict(row); log_login_activity(user.get('id'),ident,'password','success'); return user
    log_login_activity(row['id'] if row else None,ident,'password','failed')
    return None

def google_auth_configured():
    """Return True when the current Streamlit Google/OIDC configuration is complete."""
    try:
        cfg=dict(st.secrets.get("auth", {}))
        required=("client_id","client_secret","redirect_uri","cookie_secret","server_metadata_url")
        return all(str(cfg.get(k, "")).strip() for k in required)
    except Exception:
        return False

def sync_google_identity():
    """Map a successfully authenticated Google identity to the local user record.

    Google authentication never asks Cyber Rakshak to collect a Google password.
    The local database still stores only the Cyber Rakshak password hash.
    """
    try:
        g=st.user
        if not getattr(g, "is_logged_in", False):
            return None
        email=str(getattr(g, "email", "") or "").strip().lower()
        if not valid_email(email):
            return None
        with db() as c:
            row=c.execute("SELECT * FROM users WHERE lower(email)=?",(email,)).fetchone()
            if row:
                return dict(row)
            display=str(getattr(g, "name", "") or email.split("@")[0]).strip()
            username=display[:80] or email.split("@")[0]
            # Avoid collisions without exposing or storing any Google credential.
            if c.execute("SELECT id FROM users WHERE lower(username)=lower(?)",(username,)).fetchone():
                base=username[:70]
                n=2
                while c.execute("SELECT id FROM users WHERE lower(username)=lower(?)",(f"{base} {n}",)).fetchone():
                    n+=1
                username=f"{base} {n}"
            ts=now_str()
            local_password=secrets.token_urlsafe(32)
            c.execute("INSERT INTO users(username,dob,password_hash,created_at,updated_at,email) VALUES(?,?,?,?,?,?)",
                      (username,"not_provided",hash_password(local_password),ts,ts,email))
            c.commit()
            row=c.execute("SELECT * FROM users WHERE id=last_insert_rowid()").fetchone()
            return dict(row) if row else None
    except Exception:
        return None

def update_user_email(user_id,email):
    email=email.strip().lower()
    if not valid_email(email): return False,"Enter a valid email address."
    with db() as c:
        dup=c.execute("SELECT id FROM users WHERE lower(email)=lower(?) AND id<>?",(email,user_id)).fetchone()
        if dup: return False,"That email is already linked to another account."
        c.execute("UPDATE users SET email=?,updated_at=? WHERE id=?",(email,now_str(),user_id)); c.commit()
    st.session_state.auth_user['email']=email; return True,"Email linked to this account."

def save_case_server(user,case):
    if not user: return
    with db() as c:
        c.execute("INSERT INTO cases(id,user_id,title,subject,aliases,description,priority,created,updated_at,notes) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,subject=excluded.subject,aliases=excluded.aliases,description=excluded.description,priority=excluded.priority,updated_at=excluded.updated_at,notes=excluded.notes",(case['id'],user['id'],case.get('title',''),case.get('subject',''),case.get('aliases',''),case.get('description',''),case.get('priority','Medium'),case.get('created',now_str()),now_str(),case.get('notes','')))
        c.commit()

def log_dataset_server(user,case_id,name,source,df):
    if not user: return
    digest=hashlib.sha256(pd.util.hash_pandas_object(df,index=True).values.tobytes()).hexdigest()
    with db() as c:
        c.execute("INSERT INTO dataset_log(user_id,case_id,dataset,source,records,columns,evidence_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",(user['id'],case_id,name,source,len(df),json.dumps(list(map(str,df.columns))),digest,now_str()))
        c.commit()

def save_evidence_server(case_id,evidence):
    with db() as c:
        c.execute("DELETE FROM evidence WHERE case_id=?",(case_id,))
        for e in evidence:
            c.execute("INSERT INTO evidence(case_id,ev_code,type,source,raw,analysis_json,timestamp) VALUES(?,?,?,?,?,?,?)",(case_id,e.get('id',''),e.get('type',''),e.get('source',''),str(e.get('raw','')),json.dumps(e.get('analysis',{}),default=str),e.get('timestamp',now_str())))
        c.commit()

def load_evidence_server(case_id):
    with db() as c: rows=c.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY id",(case_id,)).fetchall()
    out=[]
    for r in rows:
        try: a=json.loads(r['analysis_json'] or '{}')
        except Exception: a={}
        out.append({'id':r['ev_code'],'type':r['type'],'source':r['source'],'raw':r['raw'],'analysis':a,'timestamp':r['timestamp']})
    return out

def save_feedback(user_id,name,category,rating,message):
    with sqlite3.connect(FEEDBACK_DB_PATH, timeout=20, check_same_thread=False) as c:
        c.execute("PRAGMA busy_timeout=20000")
        c.execute("INSERT INTO feedback(user_id,name,category,rating,message,created_at) VALUES(?,?,?,?,?,?)",(user_id,name.strip(),category,int(rating),message.strip(),now_str())); c.commit()

def save_contact_note(user_id,name,topic,message):
    with sqlite3.connect(FEEDBACK_DB_PATH, timeout=20, check_same_thread=False) as c:
        c.execute("PRAGMA busy_timeout=20000")
        c.execute("INSERT INTO contact_notes(user_id,name,topic,message,created_at) VALUES(?,?,?,?,?)",(user_id,name.strip(),topic.strip(),message.strip(),now_str())); c.commit()

def admin_emails():
    try:
        raw=st.secrets.get("admin_emails", "")
        if isinstance(raw, (list,tuple)): return {str(x).strip().lower() for x in raw if str(x).strip()}
        return {x.strip().lower() for x in str(raw).split(",") if x.strip()}
    except Exception:
        return set()

def is_admin_user(user=None):
    user=user or st.session_state.get("auth_user") or {}
    email=str(user.get("email","")).strip().lower()
    return bool(email and email in admin_emails())

def admin_dashboard():
    if not is_admin_user():
        st.error("Admin access is not enabled for this account.")
        return
    st.markdown('<div class="workspace-head"><div class="section-kicker">SERVER ADMIN</div><div class="workspace-title">Central response console.</div><div class="workspace-sub">Registrations, feedback, contact notes and case activity submitted from any computer connected to this deployed server appear here.</div></div>',unsafe_allow_html=True)
    with db() as c:
        users=[dict(r) for r in c.execute("SELECT id,username,email,dob,created_at,updated_at FROM users ORDER BY created_at DESC").fetchall()]
        cases=[dict(r) for r in c.execute("SELECT id,user_id,title,subject,priority,created,updated_at FROM cases ORDER BY updated_at DESC").fetchall()]
        datasets=[dict(r) for r in c.execute("SELECT id,user_id,case_id,dataset,source,records,created_at FROM dataset_log ORDER BY created_at DESC").fetchall()]
    with feedback_db() as c:
        feedback=[dict(r) for r in c.execute("SELECT * FROM feedback ORDER BY created_at DESC").fetchall()]
        contacts=[dict(r) for r in c.execute("SELECT * FROM contact_notes ORDER BY created_at DESC").fetchall()]
    a,b,c,d=st.columns(4)
    a.metric("Registered users",len(users)); b.metric("Cases",len(cases)); c.metric("Feedback",len(feedback)); d.metric("Contact notes",len(contacts))
    tabs=st.tabs(["Registrations","Feedback","Contact","Cases & datasets"])
    with tabs[0]:
        df=pd.DataFrame(users)
        st.dataframe(df,width="stretch",hide_index=True)
        st.download_button("Export registrations CSV",df.to_csv(index=False).encode(),"cyber_rakshak_registrations.csv","text/csv",width="stretch")
    with tabs[1]:
        df=pd.DataFrame(feedback)
        st.dataframe(df,width="stretch",hide_index=True)
        st.download_button("Export feedback CSV",df.to_csv(index=False).encode(),"cyber_rakshak_feedback.csv","text/csv",width="stretch")
    with tabs[2]:
        df=pd.DataFrame(contacts)
        st.dataframe(df,width="stretch",hide_index=True)
        st.download_button("Export contact CSV",df.to_csv(index=False).encode(),"cyber_rakshak_contact.csv","text/csv",width="stretch")
    with tabs[3]:
        st.markdown("**Cases**")
        st.dataframe(pd.DataFrame(cases),width="stretch",hide_index=True)
        st.markdown("**Dataset activity**")
        st.dataframe(pd.DataFrame(datasets),width="stretch",hide_index=True)

def smtp_config():
    try: return dict(st.secrets.get("smtp",{}))
    except Exception: return {}

def smtp_ready():
    cfg=smtp_config(); return bool(cfg.get('host') and cfg.get('port') and cfg.get('username') and cfg.get('password') and cfg.get('from_email'))

def send_case_email(recipient,subject,body,attachment_name=None,attachment_bytes=None):
    """Send an email through the configured SMTP service. Credentials stay in st.secrets."""
    cfg=smtp_config()
    if not smtp_ready():
        return False,"Email service is not configured. Add the SMTP block to .streamlit/secrets.toml."
    try:
        msg=EmailMessage()
        msg['Subject']=subject
        msg['From']=cfg['from_email']
        msg['To']=recipient
        msg.set_content(body)
        if attachment_name and attachment_bytes:
            msg.add_attachment(attachment_bytes,maintype='application',subtype='octet-stream',filename=attachment_name)
        host=str(cfg['host']); port=int(cfg['port'])
        with smtplib.SMTP(host,port,timeout=20) as smtp:
            smtp.ehlo()
            if str(cfg.get('starttls','true')).lower()=='true':
                smtp.starttls(); smtp.ehlo()
            smtp.login(str(cfg['username']),str(cfg['password']))
            smtp.send_message(msg)
        return True,"Email sent successfully."
    except Exception as ex:
        return False,f"Email delivery failed: {ex}"

def send_test_email(recipient):
    subject='Cyber Rakshak · Email service test'
    body=(
        'Cyber Rakshak email service test\n\n'
        'This message confirms that the configured SMTP service can deliver mail.\n'
        f'Time: {now_str()}\n\n'
        'No investigation data is included in this test message.'
    )
    return send_case_email(recipient,subject,body)

TR={
"en":{
"home":"Home","account":"My Account","invest":"Investigation","intake":"Evidence Intake","analysis":"AI Analysis","risk":"Risk Assessment","report":"Report","faq":"FAQ","about":"About Us","feedback":"Feedback & Reviews","contact":"Contact","safety":"Safety & Response","login":"Login","register":"Register","logout":"Logout","welcome":"Welcome to Cyber Rakshak","manual":"How it works","new":"New Investigation","save":"Save Case","profile":"Profile completion","workflow":"Investigation completion","tagline":"Evidence. Intelligence. Human judgment.","hero_eyebrow":"AI-ASSISTED CYBER INVESTIGATION PLATFORM","hero_title":"Turn scattered evidence into clear investigative insight.","hero_sub":"Cyber Rakshak helps organize authorized evidence, connect technical signals, explain analytical findings and prepare a traceable brief — without replacing human judgment.","learn":"Explore the platform","start":"Start an investigation","secure":"Secure workspace","features":"Built for evidence-led investigation","features_sub":"A clean workflow for collecting, analyzing, correlating and reporting authorized evidence.","about_title":"A smarter way to review complex evidence","about_sub":"Designed by Team Voxshield as an academic prototype for explainable cyber investigation.","cta_title":"Ready to investigate with clarity?","cta_sub":"Create a workspace, add authorized evidence and review every signal before making a decision.","email":"Email address","email_hint":"Use an email you control for account access and report delivery.","signin_hint":"Sign in with your registered email or username.","send_email":"Email report & case data","recipient":"Recipient email","email_status":"Email delivery is configured on the server.","not_configured":"Email delivery is not configured yet. Add SMTP settings to the server environment before sending.","translation_note":"Language changes apply to the page content, navigation and forms.",
},
"hi":{
"home":"होम","account":"मेरा अकाउंट","invest":"जांच","intake":"साक्ष्य संग्रह","analysis":"AI विश्लेषण","risk":"जोखिम आकलन","report":"रिपोर्ट","faq":"सामान्य प्रश्न","about":"हमारे बारे में","feedback":"फीडबैक और समीक्षा","contact":"संपर्क","safety":"साइबर सुरक्षा","login":"लॉगिन","register":"रजिस्टर","logout":"लॉगआउट","welcome":"Cyber Rakshak में आपका स्वागत है","manual":"यह कैसे काम करता है","new":"नई जांच","save":"केस सेव करें","profile":"प्रोफाइल पूर्णता","workflow":"जांच पूर्णता","tagline":"साक्ष्य। इंटेलिजेंस। मानव निर्णय।","hero_eyebrow":"AI-सहायित साइबर जांच प्लेटफॉर्म","hero_title":"बिखरे हुए साक्ष्य को स्पष्ट जांच-योग्य जानकारी में बदलें।","hero_sub":"Cyber Rakshak अधिकृत साक्ष्य व्यवस्थित करने, तकनीकी संकेत जोड़ने, विश्लेषण समझाने और ट्रेस करने योग्य रिपोर्ट तैयार करने में मदद करता है — मानव निर्णय का स्थान नहीं लेता।","learn":"प्लेटफॉर्म देखें","start":"जांच शुरू करें","secure":"सुरक्षित कार्यक्षेत्र","features":"साक्ष्य-आधारित जांच के लिए बनाया गया","features_sub":"अधिकृत साक्ष्य को एकत्र करने, विश्लेषण करने, जोड़ने और रिपोर्ट करने का सरल वर्कफ्लो।","about_title":"जटिल साक्ष्य की समीक्षा का बेहतर तरीका","about_sub":"Team Voxshield द्वारा explainable cyber investigation के academic prototype के रूप में बनाया गया।","cta_title":"क्या आप स्पष्टता के साथ जांच शुरू करना चाहते हैं?","cta_sub":"वर्कस्पेस बनाएं, अधिकृत साक्ष्य जोड़ें और निर्णय से पहले हर संकेत की समीक्षा करें।","email":"ईमेल पता","email_hint":"अकाउंट एक्सेस और रिपोर्ट भेजने के लिए अपना ईमेल इस्तेमाल करें।","signin_hint":"अपने रजिस्टर्ड ईमेल या यूज़रनेम से लॉगिन करें।","send_email":"रिपोर्ट और केस डेटा ईमेल करें","recipient":"प्राप्तकर्ता ईमेल","email_status":"ईमेल डिलीवरी सर्वर पर कॉन्फ़िगर है।","not_configured":"ईमेल डिलीवरी अभी कॉन्फ़िगर नहीं है। भेजने से पहले सर्वर में SMTP सेटिंग जोड़ें।","translation_note":"भाषा बदलने पर पेज की सामग्री, नेविगेशन और फॉर्म भी बदलते हैं।"
},
"ta":{
"home":"முகப்பு","account":"என் கணக்கு","invest":"விசாரணை","intake":"சான்றுகள்","analysis":"AI பகுப்பாய்வு","risk":"ஆபத்து மதிப்பீடு","report":"அறிக்கை","faq":"கேள்விகள்","about":"எங்களை பற்றி","feedback":"கருத்துகள் மற்றும் மதிப்புரைகள்","contact":"தொடர்பு","safety":"சைபர் பாதுகாப்பு","login":"உள்நுழைவு","register":"பதிவு","logout":"வெளியேறு","welcome":"Cyber Rakshak-க்கு வரவேற்கிறோம்","manual":"இது எப்படி செயல்படுகிறது","new":"புதிய விசாரணை","save":"வழக்கை சேமி","profile":"சுயவிவர நிறைவு","workflow":"விசாரணை நிறைவு","tagline":"சான்றுகள். நுண்ணறிவு. மனித முடிவு.","hero_eyebrow":"AI உதவியுடன் சைபர் விசாரணை தளம்","hero_title":"சிதறிய சான்றுகளை தெளிவான விசாரணை நுண்ணறிவாக மாற்றுங்கள்.","hero_sub":"Cyber Rakshak அங்கீகரிக்கப்பட்ட சான்றுகளை ஒழுங்குபடுத்தவும், தொழில்நுட்ப சிக்னல்களை இணைக்கவும், பகுப்பாய்வை விளக்கவும், தடமறியக்கூடிய அறிக்கையை உருவாக்கவும் உதவுகிறது — மனித முடிவை மாற்றாது.","learn":"தளத்தை பார்க்க","start":"விசாரணையை தொடங்கு","secure":"பாதுகாப்பான பணியிடம்","features":"சான்று அடிப்படையிலான விசாரணைக்காக உருவாக்கப்பட்டது","features_sub":"அங்கீகரிக்கப்பட்ட சான்றுகளை சேகரித்து, பகுப்பாய்வு செய்து, இணைத்து, அறிக்கையிடும் எளிய நடைமுறை.","about_title":"சிக்கலான சான்றுகளை மதிப்பாய்வு செய்ய சிறந்த வழி","about_sub":"Team Voxshield உருவாக்கிய explainable cyber investigation கல்வி prototype.","cta_title":"தெளிவுடன் விசாரணையை தொடங்க தயாரா?","cta_sub":"பணியிடத்தை உருவாக்கி, அங்கீகரிக்கப்பட்ட சான்றுகளை சேர்த்து, முடிவுக்கு முன் ஒவ்வொரு சிக்னலையும் மதிப்பாய்வு செய்யுங்கள்.","email":"மின்னஞ்சல் முகவரி","email_hint":"கணக்கு அணுகல் மற்றும் அறிக்கை அனுப்ப நீங்கள் பயன்படுத்தும் மின்னஞ்சலை உள்ளிடுங்கள்.","signin_hint":"பதிவு செய்த மின்னஞ்சல் அல்லது பயனர் பெயருடன் உள்நுழையுங்கள்.","send_email":"அறிக்கை மற்றும் வழக்கு தரவை மின்னஞ்சல் செய்யவும்","recipient":"பெறுநர் மின்னஞ்சல்","email_status":"மின்னஞ்சல் அனுப்புதல் server-ல் அமைக்கப்பட்டுள்ளது.","not_configured":"மின்னஞ்சல் அனுப்புதல் இன்னும் அமைக்கப்படவில்லை. அனுப்புவதற்கு முன் server-ல் SMTP அமைப்புகளை சேர்க்கவும்.","translation_note":"மொழியை மாற்றும்போது பக்க உள்ளடக்கம், navigation மற்றும் forms மாற்றப்படும்."
},
"bn":{
"home":"হোম","account":"আমার অ্যাকাউন্ট","invest":"তদন্ত","intake":"প্রমাণ গ্রহণ","analysis":"AI বিশ্লেষণ","risk":"ঝুঁকি মূল্যায়ন","report":"রিপোর্ট","faq":"প্রশ্নোত্তর","about":"আমাদের সম্পর্কে","feedback":"ফিডব্যাক ও রিভিউ","contact":"যোগাযোগ","safety":"সাইবার নিরাপত্তা","login":"লগইন","register":"রেজিস্টার","logout":"লগআউট","welcome":"Cyber Rakshak-এ স্বাগতম","manual":"কীভাবে কাজ করে","new":"নতুন তদন্ত","save":"কেস সংরক্ষণ","profile":"প্রোফাইল সম্পূর্ণতা","workflow":"তদন্ত সম্পূর্ণতা","tagline":"প্রমাণ। ইন্টেলিজেন্স। মানব সিদ্ধান্ত।","hero_eyebrow":"AI-সহায়িত সাইবার তদন্ত প্ল্যাটফর্ম","hero_title":"বিচ্ছিন্ন প্রমাণকে পরিষ্কার তদন্ত-যোগ্য তথ্যতে রূপান্তর করুন।","hero_sub":"Cyber Rakshak অনুমোদিত প্রমাণ সংগঠিত করতে, প্রযুক্তিগত সংকেত যুক্ত করতে, বিশ্লেষণ ব্যাখ্যা করতে এবং ট্রেসযোগ্য রিপোর্ট তৈরি করতে সাহায্য করে — মানব সিদ্ধান্তকে প্রতিস্থাপন করে না।","learn":"প্ল্যাটফর্ম দেখুন","start":"তদন্ত শুরু করুন","secure":"নিরাপদ ওয়ার্কস্পেস","features":"প্রমাণ-ভিত্তিক তদন্তের জন্য তৈরি","features_sub":"অনুমোদিত প্রমাণ সংগ্রহ, বিশ্লেষণ, সংযোগ এবং রিপোর্ট করার সহজ workflow।","about_title":"জটিল প্রমাণ পর্যালোচনার আরও ভালো উপায়","about_sub":"Team Voxshield-এর explainable cyber investigation academic prototype.","cta_title":"স্বচ্ছতার সঙ্গে তদন্ত শুরু করতে প্রস্তুত?","cta_sub":"একটি workspace তৈরি করুন, অনুমোদিত প্রমাণ যোগ করুন এবং সিদ্ধান্তের আগে প্রতিটি সংকেত পর্যালোচনা করুন।","email":"ইমেইল ঠিকানা","email_hint":"অ্যাকাউন্ট অ্যাক্সেস ও রিপোর্ট পাঠানোর জন্য আপনার ইমেইল দিন।","signin_hint":"আপনার নিবন্ধিত ইমেইল বা username দিয়ে লগইন করুন।","send_email":"রিপোর্ট ও কেস ডেটা ইমেইল করুন","recipient":"প্রাপকের ইমেইল","email_status":"ইমেইল ডেলিভারি server-এ configured.","not_configured":"ইমেইল ডেলিভারি এখনও configured নয়। পাঠানোর আগে server environment-এ SMTP settings যোগ করুন।","translation_note":"ভাষা বদলালে পেজের content, navigation এবং forms-ও বদলাবে।"
}}

def t(k): return TR.get(st.session_state.get('lang','en'),TR['en']).get(k,TR['en'].get(k,k))

WORKSPACE_TEXT={
"en":{
"case_config":"Case Configuration","set_context":"Set The Investigation Context.","case_meta":"Case metadata is linked to your signed-in account and can be saved to the local server database.","case_title":"Case Title","subject":"Primary Subject / Identifier","aliases":"Known Aliases / Identifiers","priority":"Priority","investigation_note":"Investigation Note","analyst_notes":"Analyst Notes","save_context":"Save Case Context","persistence":"Persistence Boundary","persistence_note":"Case metadata and dataset provenance are stored server-side. Raw uploaded files remain in the active Streamlit session in this prototype.","home_title":"Evidence Intelligence Desk","home_sub":"A focused workspace for loading authorized records, resolving identifiers, tracing relationships and preserving the evidence trail.","data_sources":"Data Sources","records":"Records","graph_nodes":"Graph Nodes","graph_relationships":"Graph Relationships"},
"hi":{
"case_config":"केस कॉन्फ़िगरेशन","set_context":"जांच का संदर्भ निर्धारित करें।","case_meta":"केस मेटाडेटा आपके साइन-इन अकाउंट से जुड़ा है और सर्वर डेटाबेस में सेव किया जा सकता है।","case_title":"केस शीर्षक","subject":"मुख्य विषय / पहचानकर्ता","aliases":"ज्ञात उपनाम / पहचानकर्ता","priority":"प्राथमिकता","investigation_note":"जांच नोट","analyst_notes":"विश्लेषक नोट्स","save_context":"केस संदर्भ सेव करें","persistence":"डेटा संग्रह सीमा","persistence_note":"केस मेटाडेटा और डेटासेट प्रोवेनेंस सर्वर पर सेव होते हैं। इस प्रोटोटाइप में कच्ची अपलोड की गई फाइलें सक्रिय Streamlit session में रहती हैं।","home_title":"साक्ष्य इंटेलिजेंस डेस्क","home_sub":"अधिकृत रिकॉर्ड लोड करने, पहचानकर्ताओं को मिलाने, संबंधों का पता लगाने और साक्ष्य ट्रेल सुरक्षित रखने के लिए केंद्रित कार्यक्षेत्र।","data_sources":"डेटा स्रोत","records":"रिकॉर्ड","graph_nodes":"ग्राफ नोड्स","graph_relationships":"ग्राफ संबंध"},
"ta":{
"case_config":"வழக்கு கட்டமைப்பு","set_context":"விசாரணை சூழலை அமைக்கவும்.","case_meta":"வழக்கு மெட்டாடேட்டா உங்கள் உள்நுழைந்த கணக்குடன் இணைக்கப்பட்டுள்ளது; இது server database-ல் சேமிக்கலாம்.","case_title":"வழக்கு தலைப்பு","subject":"முக்கிய பொருள் / அடையாளம்","aliases":"அறியப்பட்ட மாற்றுப்பெயர்கள் / அடையாளங்கள்","priority":"முன்னுரிமை","investigation_note":"விசாரணை குறிப்பு","analyst_notes":"ஆய்வாளர் குறிப்புகள்","save_context":"வழக்கு சூழலை சேமிக்கவும்","persistence":"தரவு சேமிப்பு எல்லை","persistence_note":"வழக்கு மெட்டாடேட்டா மற்றும் dataset provenance server-ல் சேமிக்கப்படும். இந்த prototype-ல் raw uploads active Streamlit session-ல் இருக்கும்.","home_title":"சான்று நுண்ணறிவு மேசை","home_sub":"அங்கீகரிக்கப்பட்ட பதிவுகளை ஏற்ற, அடையாளங்களை பொருத்த, உறவுகளை கண்டறிந்து சான்று தடத்தை பாதுகாக்கும் பணியிடம்.","data_sources":"தரவு மூலங்கள்","records":"பதிவுகள்","graph_nodes":"வரைபட முனைகள்","graph_relationships":"வரைபட உறவுகள்"},
"bn":{
"case_config":"কেস কনফিগারেশন","set_context":"তদন্তের প্রসঙ্গ নির্ধারণ করুন।","case_meta":"কেস মেটাডেটা আপনার সাইন-ইন করা অ্যাকাউন্টের সঙ্গে যুক্ত এবং সার্ভার ডেটাবেসে সংরক্ষণ করা যায়।","case_title":"কেস শিরোনাম","subject":"প্রধান বিষয় / পরিচয়","aliases":"পরিচিত উপনাম / পরিচয়","priority":"অগ্রাধিকার","investigation_note":"তদন্ত নোট","analyst_notes":"বিশ্লেষকের নোট","save_context":"কেস প্রসঙ্গ সংরক্ষণ করুন","persistence":"ডেটা সংরক্ষণ সীমা","persistence_note":"কেস মেটাডেটা ও dataset provenance server-এ সংরক্ষিত হয়। এই prototype-এ raw uploads সক্রিয় Streamlit session-এ থাকে।","home_title":"প্রমাণ ইন্টেলিজেন্স ডেস্ক","home_sub":"অনুমোদিত রেকর্ড লোড, পরিচয় মিল, সম্পর্ক অনুসরণ এবং প্রমাণের ট্রেল সংরক্ষণের জন্য কেন্দ্রীভূত workspace।","data_sources":"ডেটা উৎস","records":"রেকর্ড","graph_nodes":"গ্রাফ নোড","graph_relationships":"গ্রাফ সম্পর্ক"}
}

def wt(k):
    lang=st.session_state.get("lang","en")
    return WORKSPACE_TEXT.get(lang,WORKSPACE_TEXT["en"]).get(k,WORKSPACE_TEXT["en"].get(k,k))
def tr(k, fallback=''): return t(k) if k in TR.get(st.session_state.get('lang','en'),{}) or k in TR['en'] else fallback

COMMON={
"en":{"password":"Password","name":"Name / Username","dob":"Date of birth","case_setup":"CASE SETUP","define_question":"Define the investigation question","evidence_intake":"EVIDENCE INTAKE","add_authorized":"Add authorized evidence","run_analysis":"Run the intelligence pass","explainable":"What does the evidence currently support?","safeguards":"Safeguards","email_delivery":"Email the report + whole case data","send_note":"Send a note","share_experience":"Share your experience"},
"hi":{"password":"पासवर्ड","name":"नाम / यूज़रनेम","dob":"जन्म तिथि","case_setup":"केस सेटअप","define_question":"जांच का प्रश्न निर्धारित करें","evidence_intake":"साक्ष्य संग्रह","add_authorized":"अधिकृत साक्ष्य जोड़ें","run_analysis":"इंटेलिजेंस विश्लेषण चलाएं","explainable":"वर्तमान साक्ष्य क्या समर्थन करता है?","safeguards":"सुरक्षा उपाय","email_delivery":"रिपोर्ट + पूरा केस डेटा ईमेल करें","send_note":"नोट भेजें","share_experience":"अपना अनुभव साझा करें"},
"ta":{"password":"கடவுச்சொல்","name":"பெயர் / பயனர் பெயர்","dob":"பிறந்த தேதி","case_setup":"வழக்கு அமைப்பு","define_question":"விசாரணை கேள்வியை வரையறுக்கவும்","evidence_intake":"சான்றுகள் சேகரிப்பு","add_authorized":"அங்கீகரிக்கப்பட்ட சான்றுகளைச் சேர்க்கவும்","run_analysis":"நுண்ணறிவு பகுப்பாய்வை இயக்கவும்","explainable":"தற்போதைய சான்றுகள் எதை ஆதரிக்கின்றன?","safeguards":"பாதுகாப்பு நடவடிக்கைகள்","email_delivery":"அறிக்கை + முழு வழக்கு தரவை மின்னஞ்சல் செய்யவும்","send_note":"குறிப்பு அனுப்பவும்","share_experience":"உங்கள் அனுபவத்தை பகிரவும்"},
"bn":{"password":"পাসওয়ার্ড","name":"নাম / ইউজারনেম","dob":"জন্মতারিখ","case_setup":"কেস সেটআপ","define_question":"তদন্তের প্রশ্ন নির্ধারণ করুন","evidence_intake":"প্রমাণ গ্রহণ","add_authorized":"অনুমোদিত প্রমাণ যোগ করুন","run_analysis":"ইন্টেলিজেন্স বিশ্লেষণ চালান","explainable":"বর্তমান প্রমাণ কী সমর্থন করে?","safeguards":"নিরাপত্তা ব্যবস্থা","email_delivery":"রিপোর্ট + সম্পূর্ণ কেস ডেটা ইমেইল করুন","send_note":"নোট পাঠান","share_experience":"আপনার অভিজ্ঞতা শেয়ার করুন"}
}


def default_case(): return {'id':f"INV-{datetime.now().year}-{secrets.randbelow(900)+100}",'title':'','subject':'','aliases':'','description':'','priority':'Medium','created':now_str(),'notes':''}

def init_state_unified():
    ensure_state()
    defaults={'auth_user':None,'auth_mode':'login','public_nav':'Home','case':default_case(),'case_notes':'','datasets':{},'ledger':[],'loaded_demo':False,'evidence':[],'analysis_run':0,'selected_ev':None,'lang':'en','notes':'','keep_session_data':True,'session_saved_at':None,'data_revision':0,'graph_session_key':secrets.token_hex(12)}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v

def persist_server_state():
    if st.session_state.auth_user:
        st.session_state.case['notes']=st.session_state.get('notes',st.session_state.get('case_notes',''))
        save_case_server(st.session_state.auth_user,st.session_state.case)
        save_evidence_server(st.session_state.case['id'],st.session_state.get('evidence',[]))

def save_session_data():
    """Keep the active investigation in Streamlit Session State.
    This is intentionally in-memory/session-scoped; the server DB is used
    separately when the user explicitly saves or when case/evidence is persisted.
    """
    st.session_state.session_saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.case['notes'] = st.session_state.get('notes', st.session_state.get('case_notes',''))
    return True

def clear_session_data():
    st.session_state.datasets = {}
    st.session_state.ledger = []
    st.session_state.loaded_demo = False
    st.session_state.evidence = []
    st.session_state.analysis_run = 0
    st.session_state.selected_ev = None
    st.session_state.session_saved_at = None
    st.session_state.case = default_case()
    st.session_state.notes = ''
    st.session_state.case_notes = ''

def public_landing():
    """Public product page. The visual direction is original: calm archive/operations aesthetic."""
    lang_options={"English":"en","Hindi":"hi","Tamil":"ta","Bengali":"bn"}
    current=st.session_state.get("lang","en")
    lang_name=next((k for k,v in lang_options.items() if v==current),"English")
    st.selectbox("Language / भाषा / மொழி",list(lang_options),index=list(lang_options).index(lang_name),key="public_language",label_visibility="collapsed",on_change=set_language_from_widget,args=("public_language",lang_options))
    top_left, top_signin, top_register = st.columns([7.2,1.35,1.35], gap="small")
    with top_left:
        st.markdown('<div class="public-nav"><div><div class="pub-logo">CYBER RAKSHAK</div><div class="pub-sub">evidence intelligence / 02</div></div><div class="pub-status">● SYSTEM READY</div></div>', unsafe_allow_html=True)
    with top_signin:
        if st.button(t('login'), key='public_signin', type='primary', width='stretch'):
            st.session_state.auth_mode='login'; st.session_state.public_nav='auth'; st.rerun()
    with top_register:
        if st.button(t('register'), key='public_register', width='stretch'):
            st.session_state.auth_mode='register'; st.session_state.public_nav='auth'; st.rerun()
    st.markdown(f"<div class='top-auth-card'><div class='top-auth-label'>{t('secure')}</div><div class='top-auth-copy'>{t('signin_hint')}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-paper'><div class='eyebrow'>{t('hero_eyebrow')}</div><h1>{t('hero_title')}</h1><p>{t('hero_sub')}</p></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="hero-panel"><div class="panel-copy"><div class="panel-kicker">{t("features")}</div><div class="panel-title">{t("hero_title")}</div><div class="panel-note">{t("hero_sub")}</div></div><div class="signal-board"><div class="signal-node n1">PHONE</div><div class="signal-node n2">ACCOUNT</div><div class="signal-node n3">DOMAIN</div><div class="signal-node n4">INCIDENT</div><div class="signal-line l1"></div><div class="signal-line l2"></div><div class="signal-line l3"></div><div class="signal-center">TRACE</div></div></div>', unsafe_allow_html=True)

    st.markdown(f"""<div id="capabilities" class="section-paper"><div class="section-kicker">{t('features')}</div><h2>{t('features_sub')}</h2><div class="cap-grid"><div class="cap"><div class="cap-no">A1</div><h3>Match & provenance</h3><p>Search phones, emails, accounts, IPs and domains while retaining dataset and record context.</p></div><div class="cap"><div class="cap-no">A2</div><h3>Network analysis</h3><p>Move from direct relationships to paths, clusters, bridges and transaction routes.</p></div><div class="cap"><div class="cap-no">A3</div><h3>Temporal review</h3><p>Put timestamped observations into sequence and compare events across sources.</p></div><div class="cap"><div class="cap-no">A4</div><h3>Evidence reporting</h3><p>Keep an auditable ledger and generate a concise case brief for authorized recipients.</p></div></div></div>""", unsafe_allow_html=True)
    st.markdown('<div class="section-paper flow-paper"><div class="section-kicker">HOW IT OPERATES</div><h2>Source → match → network → explanation.</h2><div class="flow-grid"><div class="flow"><div class="flow-no">01</div><h3>Load</h3><p>Import authorized exports.</p></div><div class="flow"><div class="flow-no">02</div><h3>Normalize</h3><p>Standardize common identifiers.</p></div><div class="flow"><div class="flow-no">03</div><h3>Connect</h3><p>Build observed relationships.</p></div><div class="flow"><div class="flow-no">04</div><h3>Inspect</h3><p>Trace paths and patterns.</p></div><div class="flow"><div class="flow-no">05</div><h3>Preserve</h3><p>Export the evidence trail.</p></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-paper"><div class="responsible-box"><div class="section-kicker">ANALYSIS BOUNDARY</div><div class="responsible-title">Signals are not verdicts.</div><p>Cyber Rakshak connects evidence that an investigator is authorized to possess. It does not secretly access private records, actively probe systems, or decide guilt or criminality.</p></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="paper-footer"><span>CYBER RAKSHAK / 2026</span><span>Evidence analysis · human verification · source traceability</span></div>', unsafe_allow_html=True)

def auth_screen():
    """Minimal, centered classic authentication page."""
    lang_options={"English":"en","Hindi":"hi","Tamil":"ta","Bengali":"bn"}
    current=st.session_state.get("lang","en")
    lang_name=next((k for k,v in lang_options.items() if v==current),"English")
    st.selectbox("Language / भाषा / மொழி",list(lang_options),index=list(lang_options).index(lang_name),key="auth_language",label_visibility="collapsed",on_change=set_language_from_widget,args=("auth_language",lang_options))
    st.markdown(r"""
    <style>
    /* V14 — authentication-only entry screen.  Widgets live inside a keyed
       Streamlit container so the visual card actually wraps the form. */
    .stApp{background:
        radial-gradient(circle at 15% 15%, rgba(25,167,184,.16), transparent 28%),
        radial-gradient(circle at 85% 80%, rgba(37,99,235,.18), transparent 30%),
        linear-gradient(135deg,#071b2b 0%,#0a3045 52%,#09233a 100%) !important;
        min-height:100vh;
    }
    .block-container{max-width:1180px!important;padding:42px 24px 55px!important;}
    .st-key-auth_brand{text-align:center;margin:12px auto 24px;}
    .auth-brand-logo{width:62px;height:62px;display:block;margin:0 auto 11px;filter:drop-shadow(0 12px 24px rgba(0,0,0,.28));}
    .auth-brand-name{font:800 30px/1 'Space Grotesk',sans-serif;letter-spacing:-1.1px;color:#fff;}
    .auth-brand-name span{color:#35d3d1;}
    .auth-brand-tag{margin-top:8px;font:700 9px 'JetBrains Mono',monospace;letter-spacing:2.2px;color:rgba(255,255,255,.58);text-transform:uppercase;}
    .st-key-auth_card{width:min(470px,100%);margin:0 auto!important;background:rgba(255,255,255,.98);border:1px solid rgba(255,255,255,.72);border-radius:20px;padding:9px 28px 25px;box-shadow:0 28px 75px rgba(0,0,0,.34),0 1px 0 rgba(255,255,255,.8) inset;}
    .st-key-auth_card:before{content:"";display:block;height:3px;margin:0 0 18px;border-radius:0 0 8px 8px;background:linear-gradient(90deg,#19a7b8,#073b6f,#f56b58);}
    .st-key-auth_card [data-baseweb='tab-list']{display:flex!important;gap:4px!important;background:#f1f5f8!important;padding:5px!important;border:1px solid #e0e7ed!important;border-radius:12px!important;margin-bottom:21px!important;}
    .st-key-auth_card [data-baseweb='tab']{flex:1!important;justify-content:center!important;border-radius:8px!important;padding:10px!important;color:#64748b!important;font:800 12px 'DM Sans',sans-serif!important;}
    .st-key-auth_card [data-baseweb='tab']:hover{background:#fff!important;color:#073b6f!important;}
    .st-key-auth_card [aria-selected='true']{background:#073b6f!important;color:#fff!important;box-shadow:0 7px 17px rgba(7,59,111,.20)!important;}
    .st-key-auth_card [data-baseweb='tab-highlight']{display:none!important;}
    .st-key-auth_card input{background:#fff!important;border:1px solid #d5dee7!important;border-radius:9px!important;color:#17202b!important;min-height:43px!important;}
    .st-key-auth_card input:hover{border-color:#8ad9df!important;}
    .st-key-auth_card input:focus{border-color:#19a7b8!important;box-shadow:0 0 0 3px rgba(25,167,184,.12)!important;}
    .st-key-auth_card label{font-size:11px!important;color:#334155!important;font-weight:700!important;}
    .st-key-auth_card button[kind='primary']{min-height:44px!important;border-radius:9px!important;background:#073b6f!important;border:1px solid #073b6f!important;color:#fff!important;font-weight:800!important;box-shadow:0 10px 22px rgba(7,59,111,.18)!important;}
    .st-key-auth_card button[kind='secondary']{min-height:42px!important;border-radius:9px!important;background:#fff!important;border:1px solid #d5dee7!important;color:#334155!important;font-weight:800!important;}
    .st-key-auth_card button[kind='secondary']:hover{border-color:#19a7b8!important;color:#073b6f!important;background:#f8fcfd!important;}
    .st-key-auth_card button[kind='primary']:hover{transform:translateY(-1px);box-shadow:0 14px 28px rgba(7,59,111,.25)!important;background:#0b4c8d!important;}
    .auth-title{text-align:center;font:800 25px/1.1 'Space Grotesk',sans-serif;color:#17202b;letter-spacing:-.6px;margin:1px 0 7px;}
    .auth-sub{text-align:center;font:400 11px/1.5 'DM Sans',sans-serif;color:#7a8796;margin:0 auto 21px;max-width:350px;}
    .auth-security{text-align:center;border-top:1px solid #edf1f4;margin-top:16px;padding-top:12px;color:#8a97a7;font:500 9px/1.5 'DM Sans',sans-serif;}
    .auth-security b{color:#607084;}
    .st-key-auth_card .strength-track{margin-top:3px;}
    @media(max-width:600px){.block-container{padding:28px 14px 42px!important}.auth-brand-name{font-size:27px}.st-key-auth_card{padding:8px 18px 21px;border-radius:17px;}}
    </style>
    """, unsafe_allow_html=True)

    with st.container(key="auth_brand"):
        st.markdown(r"""
        <svg class='auth-brand-logo' viewBox='0 0 64 64' fill='none' aria-hidden='true'>
          <path d='M32 3L56 12V29C56 45 46 56 32 61C18 56 8 45 8 29V12L32 3Z' fill='#19A7B8'/>
          <path d='M32 12L48 18V29C48 40 42 48 32 53C22 48 16 40 16 29V18L32 12Z' fill='#073B6F'/>
          <path d='M22 31L28 37L43 23' stroke='white' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/>
        </svg>
        <div class='auth-brand-name'>Cyber <span>Rakshak</span></div>
        <div class='auth-brand-tag'>Evidence Intelligence Platform</div>
        """, unsafe_allow_html=True)

    with st.container(key="auth_card"):
        auth_mode = st.session_state.get("auth_mode", "login")
        mode_options=[t('login'),t('register')]
        current_mode = t('login') if auth_mode=='login' else t('register')
        selected_mode=st.radio("Authentication", mode_options, index=mode_options.index(current_mode), horizontal=True, key="auth_mode_choice", label_visibility="collapsed")
        st.session_state.auth_mode='login' if selected_mode==t('login') else 'register'

        if st.session_state.auth_mode=='login':
            st.markdown(f"<div class='auth-title'>{t('welcome')}</div><div class='auth-sub'>{t('signin_hint')}</div>",unsafe_allow_html=True)
            with st.form('login_form'):
                identifier=st.text_input(t('email')+' / Username',placeholder='you@gmail.com or username',autocomplete='username')
                password=st.text_input(ctext('password'),type='password',placeholder='Enter your Cyber Rakshak password',autocomplete='current-password')
                remember=st.checkbox('Keep me signed in on this browser session',value=True)
                ok=st.form_submit_button(t('login'),type='primary',width="stretch")
            if ok:
                user=login_user(identifier,password)
                if user:
                    st.session_state.auth_user=user; st.session_state.remember_session=remember
                    cases=get_cases(user['id'])
                    if cases:
                        st.session_state.case={k:cases[0].get(k,'') for k in ['id','title','subject','aliases','description','priority','created']}
                        st.session_state.notes=cases[0].get('notes','') or ''; st.session_state.evidence=load_evidence(st.session_state.case['id'])
                    else:
                        st.session_state.case=default_case(); st.session_state.evidence=[]
                    st.session_state.nav='Home'; st.rerun()
                else:
                    st.error('We could not sign you in. Check your Gmail/email/username and Cyber Rakshak password.')
            st.markdown("<div class='auth-or'><span></span><b>OR</b><span></span></div>",unsafe_allow_html=True)
            if google_auth_configured():
                if st.button('Continue with Google',key='google_login',width='stretch'):
                    st.login()
            else:
                st.button('Continue with Google',key='google_login_disabled',width='stretch',disabled=True)
                st.caption('Add [auth] client_id, client_secret, cookie_secret, redirect_uri and server_metadata_url to .streamlit/secrets.toml to enable Google sign-in.')
            st.markdown("<div class='auth-security'>🔒 <b>Secure access</b> · Your Cyber Rakshak password is protected with salted PBKDF2-SHA256 hashing. Google sign-in uses OpenID Connect and never asks Cyber Rakshak to collect your Google password.</div>",unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='auth-title'>{t('register')}</div><div class='auth-sub'>Set up your secure investigation workspace.</div>",unsafe_allow_html=True)
            with st.form('register_form'):
                name=st.text_input('Full name / Username',placeholder='e.g. Analyst One',autocomplete='name')
                email=st.text_input(t('email'),placeholder='name@example.com',autocomplete='email')
                dob=st.date_input(ctext('dob'),value=date(2000,1,1),min_value=date(1900,1,1),max_value=date.today())
                password=st.text_input('Create password',type='password',placeholder='Minimum 8 characters',autocomplete='new-password')
                confirm=st.text_input('Confirm password',type='password',placeholder='Re-enter your password',autocomplete='new-password')
                agree=st.checkbox('I understand this is an investigative-support prototype and I will not use it to make unsupported criminality decisions.')
                ok=st.form_submit_button(t('register'),type='primary',width="stretch")
            if password:
                pct,label=password_strength(password)
                fill='#b4233b' if pct==25 else '#0e7490' if pct==55 else '#087f5b'
                st.markdown(f"<div class='strength-track'><div class='strength-fill' style='width:{pct}%;background:{fill}'></div></div><div class='strength-text'>Password strength: <b>{label}</b></div>",unsafe_allow_html=True)
            if ok:
                if not name.strip(): st.error('Please enter your name.')
                elif not valid_email(email): st.error('Please enter a valid email address.')
                elif len(password)<8: st.error('Please use a password of at least 8 characters.')
                elif password!=confirm: st.error('Passwords do not match.')
                elif not agree: st.error('Please accept the responsible-use statement.')
                else:
                    good,msg=create_user(name,email,dob.isoformat(),password)
                    if good:
                        st.success(msg+' You can now sign in with your email or username.')
                        st.session_state.auth_mode='login'
                        st.session_state.auth_mode_choice=t('login')
                        st.rerun()
                    else: st.error(msg)
            st.markdown("<div class='auth-security'>✦ <b>Privacy by design</b> · SMTP credentials are never collected in this form.</div>",unsafe_allow_html=True)

def feedback_db():
    conn=sqlite3.connect(FEEDBACK_DB_PATH, timeout=20, check_same_thread=False)
    conn.row_factory=sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=20000")
    except Exception:
        pass
    return conn

def init_db():
    init_server_db()

def init_feedback_db():
    init_server_db()

def get_cases(user_id):
    with db() as c: return [dict(r) for r in c.execute("SELECT * FROM cases WHERE user_id=? ORDER BY updated_at DESC",(user_id,)).fetchall()]

def save_case(case,user_id,notes=""):
    case=dict(case); case['notes']=notes; save_case_server({'id':user_id},case)

def save_evidence(case_id,evidence):
    save_evidence_server(case_id,evidence)

def load_evidence(case_id):
    return load_evidence_server(case_id)

def init_state():
    init_state_unified()

def persist_current():
    persist_server_state()

def reset_case():
    st.session_state.case=default_case(); st.session_state.evidence=[]; st.session_state.notes=''; st.session_state.analysis_run=0; persist_server_state()

def workflow_completion():
    c=st.session_state.case; e=st.session_state.get('evidence',[]); F=current_fusion()
    checks=[bool(c.get('title')),bool(c.get('description')),bool(e),F.get('coverage',0)>=1,F.get('score',0)>=40,bool(st.session_state.get('notes')),len(e)>=2]
    return int(round(sum(checks)/len(checks)*100))

def profile_completion():
    u=st.session_state.auth_user
    if not u: return 0
    checks=[bool(u.get('username')),bool(u.get('email')),bool(u.get('dob'))]
    return int(sum(checks)/len(checks)*100)

def ctext(k):
    return COMMON.get(st.session_state.get('lang','en'),COMMON['en']).get(k,COMMON['en'].get(k,k))

NAV_LABEL_KEYS={
    "Home":"home","Case Setup":"case_setup","Evidence Intake":"intake","AI Analysis":"analysis",
    "Risk Assessment":"risk","Report":"report","Report & Email":"send_email","My Account":"account",
    "Feedback & Reviews":"feedback","Contact":"contact","Safety & Response":"safety",
    "FAQ":"faq","About Team":"about",
    "Data & Match":"data_match","Financial Network":"financial","Cyber Network":"cyber",
    "Relationship Graph":"relationship","Multi-Hop Paths":"paths","Clusters":"clusters",
    "Centrality & Bridges":"centrality","Transaction Flow":"transactions","Entity Similarity":"similarity",
    "Timeline":"timeline","AI Correlation":"correlation","Evidence Chain":"evidence_chain","Evidence Ledger":"ledger",
}
NAV_EXTRA_TRANSLATIONS={
    "hi":{"data_match":"डेटा और मैच","financial":"वित्तीय नेटवर्क","cyber":"साइबर नेटवर्क","relationship":"रिलेशनशिप ग्राफ","paths":"मल्टी-हॉप पाथ्स","clusters":"क्लस्टर","centrality":"केंद्रीयता और ब्रिज","transactions":"लेनदेन प्रवाह","similarity":"एंटिटी समानता","timeline":"समयरेखा","correlation":"AI सहसंबंध","evidence_chain":"साक्ष्य श्रृंखला","ledger":"साक्ष्य लेजर","case_setup":"केस सेटअप"},
    "ta":{"data_match":"தரவு மற்றும் பொருத்தம்","financial":"நிதி வலைப்பின்னல்","cyber":"சைபர் வலைப்பின்னல்","relationship":"உறவு வரைபடம்","paths":"பல-தாவல் பாதைகள்","clusters":"கிளஸ்டர்கள்","centrality":"மையத்தன்மை மற்றும் பாலங்கள்","transactions":"பரிவர்த்தனை ஓட்டம்","similarity":"Entity ஒற்றுமை","timeline":"காலவரிசை","correlation":"AI தொடர்பு","evidence_chain":"சான்று சங்கிலி","ledger":"சான்று லெட்ஜர்","case_setup":"வழக்கு அமைப்பு"},
    "bn":{"data_match":"ডেটা ও ম্যাচ","financial":"আর্থিক নেটওয়ার্ক","cyber":"সাইবার নেটওয়ার্ক","relationship":"সম্পর্ক গ্রাফ","paths":"মাল্টি-হপ পাথস","clusters":"ক্লাস্টার","centrality":"কেন্দ্রিকতা ও ব্রিজ","transactions":"লেনদেন প্রবাহ","similarity":"এনটিটি সাদৃশ্য","timeline":"টাইমলাইন","correlation":"AI সম্পর্ক","evidence_chain":"প্রমাণ চেইন","ledger":"প্রমাণ লেজার","case_setup":"কেস সেটআপ"},
}

def nav_label(item):
    key=NAV_LABEL_KEYS.get(item)
    if not key: return item
    extra=NAV_EXTRA_TRANSLATIONS.get(st.session_state.get('lang','en'),{})
    if key in extra: return extra[key]
    return t(key)

def set_language_from_widget(widget_key, options):
    selected=st.session_state.get(widget_key)
    if selected in options:
        new_lang=options[selected]
        if st.session_state.get('lang') != new_lang:
            st.session_state.lang=new_lang

def add_evidence_item(ev_type,source,raw,analysis):
    code=f"EV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.randbelow(900)+100}"
    item={'id':code,'type':ev_type,'source':source,'raw':raw,'analysis':analysis,'timestamp':now_str()}
    st.session_state.evidence.append(item)
    st.session_state.analysis_run += 1
    if st.session_state.get('keep_session_data', True):
        save_session_data()
    persist_server_state()
    return item

def current_fusion():
    return fusion(st.session_state.get('evidence',[]))

def password_strength(password):
    score=0
    if len(password)>=8: score+=1
    if len(password)>=12: score+=1
    if re.search(r'[A-Z]',password): score+=1
    if re.search(r'[a-z]',password): score+=1
    if re.search(r'\d',password): score+=1
    if re.search(r'[^A-Za-z0-9]',password): score+=1
    return (25,'Weak') if score<=2 else (55,'Fair') if score<=4 else (85,'Strong')

def report_text_full():
    F=current_fusion(); G=get_graph('all'); case=st.session_state.case
    lines=['CYBER RAKSHAK — INVESTIGATION REPORT','='*72,f'Case ID: {case.get("id")}',f'Title: {case.get("title") or "Untitled"}',f'Subject / entity: {case.get("subject") or "Not specified"}',f'Priority: {case.get("priority")}',f'Generated: {now_str()}','', 'EXECUTIVE SIGNAL', f'Combined evidence score: {F.get("score",0)}/100', f'Coverage: {F.get("coverage",0)} evidence categories', f'Risk level: {F.get("risk", "Low")}', '', 'EVIDENCE INVENTORY']
    for e in st.session_state.get('evidence',[]):
        a=e.get('analysis',{}) or {}
        lines += [f'- {e.get("id")} | {e.get("type")} | {e.get("source")} | {e.get("timestamp")}', f'  Score: {a.get("score","")} | {a.get("strength","")} | {str(a.get("indicators",[]))[:500]}']
    lines += ['', 'NETWORK', f'Graph nodes: {G.number_of_nodes()}', f'Graph relationships: {G.number_of_edges()}']
    if G.number_of_nodes():
        deg=dict(G.degree()); top=sorted(deg.items(),key=lambda x:x[1],reverse=True)[:10]
        lines.append('Key high-connectivity nodes: '+', '.join(f'{n} ({d})' for n,d in top))
    lines += ['', 'LIMITATIONS', 'Observed records and analytical signals require source verification. Connectivity is not proof of criminality, identity, intent or legal responsibility.']
    return '\n'.join(lines)

def account_page():
    u=st.session_state.auth_user
    st.markdown('<div class="workspace-head"><div class="section-kicker">Account / server</div><div class="workspace-title">Your investigation identity.</div><div class="workspace-sub">The account is stored in the local server database. The linked email can receive authorized case reports when SMTP is configured.</div></div>',unsafe_allow_html=True)
    a,b=st.columns([1.15,.85])
    with a:
        st.markdown('<div class="card"><div class="card-title">Profile & email link</div>',unsafe_allow_html=True)
        st.write('**Username:**',u.get('username','')); st.write('**Linked email:**',u.get('email','') or 'Not linked')
        with st.form('link_email'):
            em=st.text_input('Email address',value=u.get('email',''),type='email')
            save=st.form_submit_button('Save linked email',type='primary',width='stretch')
        if save:
            ok,msg=update_user_email(u['id'],em); st.success(msg) if ok else st.error(msg)
        st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><div class="card-title">Server status</div><div class="notice notice-green"><b>SQLite server data</b><br>Accounts, cases and dataset provenance metadata are stored under <code>server_data/</code>.</div><br><div class="notice"><b>SMTP delivery</b><br>'+('Configured and ready.' if smtp_ready() else 'Not configured yet. The app still works without email delivery.')+'</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">Email setup boundary</div><div class="card-sub">Keep SMTP credentials out of the Python file. Streamlit supports project secrets for credentials.</div><pre>[smtp]\nhost = "smtp.example.com"\nport = 587\nusername = "your-mailbox"\npassword = "YOUR_SECRET"\nfrom_email = "your-mailbox@example.com"\nstarttls = "true"</pre></div>',unsafe_allow_html=True)
    with st.form('smtp_test_form'):
        test_recipient=st.text_input('Test recipient email',value=u.get('email',''),type='email',placeholder='recipient@example.com')
        test_send=st.form_submit_button('Test email service',width='stretch',disabled=not smtp_ready())
    if test_send:
        if not valid_email(test_recipient): st.error('Enter a valid recipient email.')
        else:
            ok,msg=send_test_email(test_recipient)
            st.success(msg) if ok else st.error(msg)

def report_email_page():
    u=st.session_state.auth_user; case=st.session_state.case
    st.markdown('<div class="workspace-head"><div class="section-kicker">Report / delivery</div><div class="workspace-title">Preserve the trail. Send the brief.</div><div class="workspace-sub">Generate a traceable investigation brief and send it through the configured email service. SMTP credentials never appear in the interface.</div></div>',unsafe_allow_html=True)
    G=get_graph('all')
    lines=['CYBER RAKSHAK — INVESTIGATION BRIEF','='*64,f'Case: {case["id"]}',f'Title: {case.get("title") or "Untitled"}',f'Subject/entity: {case.get("subject") or "Not specified"}',f'Generated: {now_str()}','',f'Datasets: {len(all_frames())}',f'Records: {sum(len(x) for x in all_frames().values())}',f'Graph nodes: {G.number_of_nodes()}',f'Graph relationships: {G.number_of_edges()}','','Evidence discipline: observed records and analytical graph signals require human verification.','']
    for row in st.session_state.ledger: lines.append(f'- {row.get("dataset")} | {row.get("source")} | {row.get("records")} records | {row.get("evidence_id","")}')
    report='\n'.join(lines)
    st.text_area('Generated brief',report,height=360)
    st.download_button('Download brief',report.encode(),'cyber_rakshak_investigation_brief.txt','text/plain',width='stretch')

    configured=smtp_ready()
    st.markdown('<div class="card"><div class="card-title">Email delivery service</div><div class="card-sub">'+('SMTP service is configured and ready to send.' if configured else 'SMTP service is not configured yet. Add the SMTP block to Streamlit secrets.')+'</div></div>',unsafe_allow_html=True)
    recipient=st.text_input('Recipient email',value=u.get('email',''),type='email',placeholder='recipient@example.com')
    subject=st.text_input('Email subject',value=f'Cyber Rakshak · {case.get("title") or case["id"]}')
    attach=st.checkbox('Attach the investigation brief (.txt)',value=True)
    c1,c2=st.columns(2)
    with c1:
        if st.button('Send investigation brief',type='primary',width='stretch',disabled=not configured):
            if not valid_email(recipient):
                st.error('Enter a valid recipient email.')
            else:
                attachment=report.encode('utf-8') if attach else None
                ok,msg=send_case_email(recipient,subject,report,'cyber_rakshak_investigation_brief.txt',attachment) if attach else send_case_email(recipient,subject,report)
                st.success(msg) if ok else st.error(msg)
    with c2:
        if st.button('Send test email',width='stretch',disabled=not configured):
            if not valid_email(recipient):
                st.error('Enter a valid recipient email.')
            else:
                ok,msg=send_test_email(recipient)
                st.success(msg) if ok else st.error(msg)



st.markdown(r"""
<style>
/* FINAL V4 — high-contrast authentication, responsive light workspace, faster navigation */
.auth-or{display:flex;align-items:center;gap:10px;margin:14px 0 12px;color:#94a3b8;font:700 9px 'DM Sans',sans-serif;letter-spacing:1.4px;text-transform:uppercase}.auth-or span{height:1px;background:#e8edf2;flex:1}.auth-or b{font-weight:800}
.st-key-auth_card [data-baseweb='tab-list']{display:grid!important;grid-template-columns:1fr 1fr!important;gap:6px!important;background:#eef3f7!important;padding:6px!important;border:1px solid #d8e1e9!important;border-radius:12px!important}
.st-key-auth_card div[role='radiogroup']{display:grid!important;grid-template-columns:1fr 1fr!important;gap:6px!important;background:#eef3f7!important;padding:6px!important;border:1px solid #d8e1e9!important;border-radius:12px!important}.st-key-auth_card div[role='radiogroup'] label{justify-content:center!important;background:#073b6f!important;color:#fff!important;border:1px solid #073b6f!important;border-radius:9px!important;padding:11px 8px!important;font-weight:800!important}.st-key-auth_card div[role='radiogroup'] label:nth-child(2){background:#0f766e!important;border-color:#0f766e!important}.st-key-auth_card div[role='radiogroup'] label:has(input:checked){box-shadow:0 7px 18px rgba(7,59,111,.20)!important;filter:brightness(1.08)}.st-key-auth_card div[role='radiogroup'] label p{color:#fff!important}
.st-key-auth_card [data-baseweb='tab']{min-height:46px!important;border-radius:9px!important;font-weight:800!important;opacity:1!important}
.st-key-auth_card [data-baseweb='tab']:nth-child(1){background:#073b6f!important;color:#fff!important;border:1px solid #073b6f!important}
.st-key-auth_card [data-baseweb='tab']:nth-child(2){background:#0f766e!important;color:#fff!important;border:1px solid #0f766e!important}
.st-key-auth_card [data-baseweb='tab'][aria-selected='true']:nth-child(1){background:#0b4c8d!important;color:#fff!important;box-shadow:0 7px 18px rgba(7,59,111,.25)!important}
.st-key-auth_card [data-baseweb='tab'][aria-selected='true']:nth-child(2){background:#0d9488!important;color:#fff!important;box-shadow:0 7px 18px rgba(15,118,110,.25)!important}
.st-key-auth_card [data-baseweb='tab']:hover{filter:brightness(1.06)!important;color:#fff!important}
.st-key-auth_card button[kind='primary']{background:#073b6f!important;color:#fff!important;border-color:#073b6f!important}
.st-key-auth_card button[kind='secondary']{background:#f8fafc!important;color:#073b6f!important;border-color:#cbd5e1!important}
.stButton>button,.stDownloadButton>button{transition:background .08s ease,border-color .08s ease,transform .08s ease!important}
[data-testid='stSidebar'] div[role='radiogroup'] label{transition:background .08s ease,color .08s ease!important}
@media(max-width:900px){.block-container{padding-left:12px!important;padding-right:12px!important}.hero-panel{grid-template-columns:1fr!important;padding:20px!important}.signal-board{height:210px!important}.public-nav{gap:8px!important;flex-wrap:wrap}.hero-paper h1{font-size:42px!important}.st-key-auth_card{width:100%!important}}
@media(max-width:600px){.hero-paper{padding:24px 0 16px!important}.hero-paper h1{font-size:34px!important}.hero-paper p{font-size:14px!important}.hero-panel{gap:16px!important}.signal-board{height:180px!important}.auth-shell,.st-key-auth_card{box-shadow:none!important}.st-key-auth_card{padding:8px 14px 18px!important}.st-key-auth_card [data-baseweb='tab']{min-height:42px!important;padding:8px 4px!important;font-size:11px!important}}
</style>
""", unsafe_allow_html=True)

init_server_db(); init_state_unified()

# Optional Google/OIDC login. If configured and authenticated, bridge the
# Google identity into the same local case/evidence workspace.
if st.session_state.auth_user is None:
    google_user=sync_google_identity()
    if google_user:
        st.session_state.auth_user=google_user
        st.session_state.auth_mode='login'
        st.session_state.public_nav='Home'
        st.session_state.nav='Home'

if st.session_state.auth_user and not st.session_state.get("_server_loaded",False):
    saved=load_evidence_server(st.session_state.case["id"])
    if saved: st.session_state.evidence=saved
    st.session_state._server_loaded=True

# Gate public/auth pages before the analysis workspace.
if st.session_state.auth_user is None:
    if st.session_state.public_nav == 'Home': public_landing()
    else: auth_screen()
    st.stop()

# ============================================================
# Workspace navigation / top utility bar
# ============================================================
WORKSPACE_NAV = [
    "Home", "Case Setup", "Evidence Intake", "AI Analysis", "Risk Assessment", "Data & Match",
    "Financial Network", "Cyber Network", "Relationship Graph", "Multi-Hop Paths", "Clusters",
    "Centrality & Bridges", "Transaction Flow", "Entity Similarity", "Timeline", "AI Correlation",
    "Evidence Chain", "Evidence Ledger", "Report", "Report & Email", "My Account", "FAQ",
    "About Team", "Feedback & Reviews", "Contact", "Safety & Response"
]
if is_admin_user():
    WORKSPACE_NAV.append("Admin Console")

if "nav" not in st.session_state:
    st.session_state.nav = "Home"
if st.session_state.nav not in WORKSPACE_NAV:
    st.session_state.nav = "Home"

with st.sidebar:
    st.markdown('<div class="cr-brand"><div class="cr-shield">CR</div><div><div class="cr-brand-title">Cyber Rakshak</div><div class="cr-brand-sub">Evidence intelligence workspace</div></div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="sidebar-section">{"WORKSPACE LANGUAGE" if st.session_state.get("lang","en")=="en" else ("कार्यस्थल भाषा" if st.session_state.get("lang")=="hi" else ("பணியிட மொழி" if st.session_state.get("lang")=="ta" else "ওয়ার্কস্পেস ভাষা"))}</div>', unsafe_allow_html=True)
    st.selectbox('Language / भाषा / மொழி', ['English','Hindi','Tamil','Bengali'], index=['en','hi','ta','bn'].index(st.session_state.get('lang','en')), key='language_choice', label_visibility='collapsed', on_change=set_language_from_widget, args=('language_choice', {'English':'en','Hindi':'hi','Tamil':'ta','Bengali':'bn'}))

    st.markdown(f'<div class="sidebar-section">{"CURRENT CASE" if st.session_state.get("lang","en")=="en" else ("वर्तमान केस" if st.session_state.get("lang")=="hi" else ("தற்போதைய வழக்கு" if st.session_state.get("lang")=="ta" else "বর্তমান কেস"))}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-case"><div class="case-id">{st.session_state.case.get("id", "NO CASE")}</div><div class="case-title">{st.session_state.case.get("title") or "Untitled investigation"}</div></div>', unsafe_allow_html=True)

    groups = [
        ("PART 1 · INVESTIGATION", ["Home", "Case Setup", "Evidence Intake", "AI Analysis", "Risk Assessment", "Report", "Report & Email"]),
        ("PART 2 · NETWORK INTELLIGENCE", ["Data & Match", "Financial Network", "Cyber Network", "Relationship Graph", "Multi-Hop Paths", "Clusters", "Centrality & Bridges", "Transaction Flow", "Entity Similarity", "Timeline", "AI Correlation", "Evidence Chain", "Evidence Ledger"]),
        ("WORKSPACE", ["My Account", "FAQ", "About Team", "Feedback & Reviews", "Contact", "Safety & Response"]),
    ]
    if is_admin_user():
        groups.append(("SERVER", ["Admin Console"]))
    st.markdown(f'<div class="sidebar-section">{"CASE NAVIGATION" if st.session_state.get("lang","en")=="en" else ("केस नेविगेशन" if st.session_state.get("lang")=="hi" else ("வழக்கு வழிசெலுத்தல்" if st.session_state.get("lang")=="ta" else "কেস নেভিগেশন"))}</div>', unsafe_allow_html=True)
    nav = st.session_state.nav
    for gi,(label,items) in enumerate(groups):
        current = nav if nav in items else None
        display_items=[nav_label(x) for x in items]
        current_display=nav_label(current) if current else None
        chosen_display = st.radio(label, display_items, index=(display_items.index(current_display) if current_display in display_items else None), key=f"nav_group_{gi}", label_visibility="visible")
        if chosen_display in display_items:
            chosen = items[display_items.index(chosen_display)]
            if chosen != nav:
                nav = chosen
    st.session_state.nav = nav

    st.markdown('<div class="sidebar-rule"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-section">{"SESSION DATA" if st.session_state.get("lang","en")=="en" else ("सेशन डेटा" if st.session_state.get("lang")=="hi" else ("அமர்வு தரவு" if st.session_state.get("lang")=="ta" else "সেশন ডেটা"))}</div>', unsafe_allow_html=True)
    st.checkbox('Keep investigation data in this session', key='keep_session_data', help='Keeps uploaded datasets, evidence, graph inputs, notes and the current case available while this browser session remains connected.')
    if st.session_state.get('keep_session_data', True):
        saved_label = st.session_state.get('session_saved_at') or 'active'
        st.caption(f'✓ Session data active · last state {saved_label}')
    else:
        st.caption('Session retention is off. New data will not be intentionally retained in session state.')
    if st.button('Clear session data', width='stretch', key='sidebar_clear_session'):
        clear_session_data()
        st.toast('Session investigation data cleared.')
        st.rerun()

    st.markdown('<div class="sidebar-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Demo & case controls</div>', unsafe_allow_html=True)
    if st.button("Load bundled demo pack", width="stretch", key="sidebar_bundled_demo"):
        pack=bundled_demo_data()
        if pack:
            for n,df in pack.items(): add_dataset(n,df,"Bundled structured synthetic demo")
            st.session_state.loaded_demo=True; st.session_state.nav="Data & Match"; st.rerun()
        else:
            st.warning("The bundled demo pack is not present in this installation.")
    if st.button("Load quick demo", width="stretch", key="sidebar_demo"):
        for n,df in synthetic_data().items(): add_dataset(n,df,"Built-in quick synthetic demo")
        st.session_state.loaded_demo=True; st.session_state.nav="Data & Match"; st.rerun()
    if st.button("Save case to server", width="stretch", key="sidebar_save"):
        persist_server_state(); st.success("Case metadata saved.")
    if st.button("Clear current data", width="stretch", key="sidebar_clear"):
        st.session_state.datasets={}; st.session_state.ledger=[]; st.session_state.loaded_demo=False; st.session_state.session_saved_at=None; st.session_state.data_revision=st.session_state.get("data_revision",0)+1; st.rerun()

    st.markdown('<div class="sidebar-rule"></div>', unsafe_allow_html=True)
    u=st.session_state.auth_user
    st.markdown(f'<div class="signed-in"><b>Signed in</b><br>{u.get("email") or u.get("username")}</div>', unsafe_allow_html=True)
    q1,q2=st.columns(2, gap="small")
    with q1:
        if st.button("Account", width="stretch", key="sidebar_account"):
            st.session_state.nav="My Account"; st.rerun()
    with q2:
        if st.button("Sign out", width="stretch", key="sidebar_signout"):
            st.session_state.auth_user=None; st.session_state.public_nav="Home"; st.session_state.auth_mode="login"; st.rerun()

# Small utility row on every authenticated page.
head_left, head_mid, head_right = st.columns([5.8, 2.0, 1.6], gap="small")
with head_left:
    st.markdown('<div class="workspace-brandline"><span class="brand-mark">CR</span><span>CYBER RAKSHAK</span><span class="brand-divider">/</span><span>INVESTIGATION WORKSPACE</span></div>', unsafe_allow_html=True)
with head_mid:
    if st.button("Save case", width="stretch", key="top_save"):
        persist_server_state(); st.toast("Case metadata saved to server.")
with head_right:
    if st.button("Account", width="stretch", key="top_account"):
        st.session_state.nav="My Account"; st.rerun()

# ============================================================
# Main workspace
# ============================================================
PART2_NAV = {"Data & Match", "Financial Network", "Cyber Network", "Relationship Graph", "Multi-Hop Paths", "Clusters", "Centrality & Bridges", "Transaction Flow", "Entity Similarity", "Timeline", "AI Correlation", "Evidence Chain", "Evidence Ledger"}
if nav in PART2_NAV:
    st.markdown(f'<div class="part2-banner"><span>PART 2</span><b>{part2_map.get(st.session_state.get("lang","en"),part2_map["en"])}</b><em>{"Evidence correlation · entity resolution · graph analysis" if st.session_state.get("lang","en")=="en" else ("साक्ष्य सहसंबंध · पहचान समाधान · ग्राफ विश्लेषण" if st.session_state.get("lang")=="hi" else ("சான்று தொடர்பு · அடையாள தீர்வு · வரைபட பகுப்பாய்வு" if st.session_state.get("lang")=="ta" else "প্রমাণ সম্পর্ক · পরিচয় সমাধান · গ্রাফ বিশ্লেষণ"))}</em></div>', unsafe_allow_html=True)

if nav=="Home":
    st.markdown(f'<div class="workspace-head"><div class="workspace-title">{wt("home_title")}</div><div class="workspace-sub">{wt("home_sub")}</div></div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    for c,label,value in [(c1,wt("data_sources"),len(all_frames())),(c2,wt("records"),sum(len(x) for x in all_frames().values())),(c3,wt("graph_nodes"),get_graph("all").number_of_nodes()),(c4,wt("graph_relationships"),get_graph("all").number_of_edges())]:
        with c: st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value:,}</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    left,right=st.columns([1.15,.85])
    with left:
        st.markdown('<div class="card"><div class="card-title">A practical investigation loop</div><div class="card-sub">Start with the evidence you already have and move one question at a time.</div><div class="step"><div class="step-no">1</div><div><b>Add your authorized data</b><span>Upload CSV, Excel, JSON or text exports from the systems you are allowed to investigate.</span></div></div><div class="step"><div class="step-no">2</div><div><b>Search an identifier</b><span>Enter a phone, email, account, IP, domain or other identifier. The system normalizes common formats.</span></div></div><div class="step"><div class="step-no">3</div><div><b>Review matching evidence</b><span>See which source and record produced each match instead of treating a match as a conclusion.</span></div></div><div class="step"><div class="step-no">4</div><div><b>Explore the network</b><span>Follow supported connections, timelines and analytical signals for deeper review.</span></div></div></div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card"><div class="card-title">What the system can connect</div><div class="card-sub">Examples of relationships reconstructed from supplied records.</div><div class="notice notice-blue"><b>Identity</b><br>Phone ↔ Email ↔ Account ↔ Device</div><br><div class="notice"><b>Financial</b><br>Account → Transaction → Account</div><br><div class="notice"><b>Cyber infrastructure</b><br>Client IP → Domain → IP → Incident</div><br><div class="notice notice-green"><b>Important</b><br>Observed connections are evidence to review. They are not automatic proof of identity, intent or guilt.</div></div>',unsafe_allow_html=True)
    G=get_graph("all")
    if G.number_of_nodes():
        st.markdown('<div class="card"><div class="card-title">Evidence network preview</div><div class="card-sub">A visual summary of relationships already present in your loaded data.</div></div>',unsafe_allow_html=True)
        st.plotly_chart(graph_fig(G),width="stretch",config={"displayModeBar":False})

# ============================================================
# Data & Match — key redesign: side-by-side
# ============================================================
elif nav=="Case Setup":
    st.markdown(f'<div class="workspace-head"><div class="section-kicker">{wt("case_config")}</div><div class="workspace-title">{wt("set_context")}</div><div class="workspace-sub">{wt("case_meta")}</div></div>',unsafe_allow_html=True)
    with st.form("case_setup_form"):
        title=st.text_input(wt("case_title"),value=st.session_state.case.get("title", ""),placeholder="e.g. Cross-source identifier review")
        subject=st.text_input(wt("subject"),value=st.session_state.case.get("subject", ""),placeholder="Optional — phone, account, domain, incident…")
        aliases=st.text_input(wt("aliases"),value=st.session_state.case.get("aliases", ""),placeholder="Optional alternate identifiers")
        priority=st.selectbox(wt("priority"),["Low","Medium","High","Critical"],index=["Low","Medium","High","Critical"].index(st.session_state.case.get("priority","Medium")))
        description=st.text_area(wt("investigation_note"),value=st.session_state.case.get("description", ""),placeholder="What question are you trying to answer?",height=130)
        notes=st.text_area(wt("analyst_notes"),value=st.session_state.get("notes", ""),placeholder="Record observations, provenance checks or follow-up questions.",height=100)
        submitted=st.form_submit_button(wt("save_context"),type="primary",width="stretch")
    if submitted:
        st.session_state.case.update({"title":title.strip(),"subject":subject.strip(),"aliases":aliases.strip(),"priority":priority,"description":description.strip(),"notes":notes.strip()})
        st.session_state.notes=notes.strip(); persist_server_state(); st.success("Case context saved to the server database.")
    a,b,c=st.columns(3)
    a.metric("Case ID",st.session_state.case["id"])
    b.metric("Loaded datasets",len(all_frames()))
    c.metric("Evidence records",sum(len(df) for df in all_frames().values()))
    st.markdown(f'<div class="notice notice-green"><b>{wt("persistence")}:</b> {wt("persistence_note")}</div>',unsafe_allow_html=True)

elif nav=="Data & Match":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Data & Match</div><div class="workspace-sub">Upload evidence on the left. Search and review matching records on the right. This keeps the most common investigation workflow on one screen.</div></div>',unsafe_allow_html=True)

    left,right=st.columns([1.05,1],gap="large")
    with left:
        st.markdown('<div class="card"><div class="card-title">1. Add authorized data</div><div class="card-sub">Start with the files you already have permission to analyze.</div>',unsafe_allow_html=True)
        upload=st.file_uploader("Drop files here or choose from your computer",type=["csv","xlsx","xls","json","txt"],accept_multiple_files=True,help="CSV, Excel, JSON and TXT are supported.")
        if upload:
            for up in upload:
                try:
                    if up.name not in all_frames():
                        df=read_upload(up); add_dataset(up.name,df,"Computer Upload")
                        st.success(f"Added {up.name} · {len(df):,} records")
                    else:
                        st.info(f"{up.name} is already loaded")
                except Exception as e: st.error(f"Could not read {up.name}: {e}")
        st.markdown('<div class="section-label">Other ways to add data</div>',unsafe_allow_html=True)
        t1,t2,t3=st.tabs(["Data URL","Import profile","Loaded sources"])
        with t1:
            url=st.text_input("Public / authorized CSV or JSON URL",placeholder="https://example.org/export.csv",label_visibility="visible")
            if st.button("Fetch data",type="primary",key="fetch_url") and url:
                try:
                    import requests
                    r=requests.get(url,timeout=12); r.raise_for_status(); ct=r.headers.get("content-type","")
                    df=pd.DataFrame(r.json()) if "json" in ct or url.lower().endswith(".json") else pd.read_csv(io.StringIO(r.text))
                    add_dataset("url_import_"+datetime.now().strftime("%H%M%S"),df,"Data URL")
                    st.success(f"Added {len(df):,} records")
                except Exception as e: st.error(f"URL import failed: {e}")
        with t2:
            profile=st.selectbox("What kind of export is this?",["Generic Dataset","Bank / UPI Transaction Export","Telecom / Mobile Event Export","Email / Login Export","Security / Firewall Log","Custom Mapping"])
            desc={"Generic Dataset":"Automatic column detection.","Bank / UPI Transaction Export":"Account, sender, receiver, amount, timestamp, transaction ID and phone/UPI fields.","Telecom / Mobile Event Export":"Phone, timestamp, device, IP and event fields.","Email / Login Export":"Email, username, device, IP and timestamp fields.","Security / Firewall Log":"Source IP, destination IP, domain/URL, timestamp and incident fields.","Custom Mapping":"Use this when your organization's column names do not follow common conventions."}[profile]
            st.markdown(f'<div class="notice">{desc}</div>',unsafe_allow_html=True)
        with t3:
            if st.session_state.ledger:
                st.dataframe(pd.DataFrame(st.session_state.ledger),width="stretch",hide_index=True,height=220)
            else: st.info("No data has been added yet.")
        if all_frames():
            st.markdown('<div class="section-label">Loaded datasets</div>',unsafe_allow_html=True)
            for name,df in all_frames().items():
                with st.expander(f"{name}  ·  {len(df):,} records"):
                    st.dataframe(df.head(6),width="stretch",hide_index=True)
                    st.caption("Detected fields: " + ", ".join(f"{k} → {v}" for k,v in infer_columns(df).items()))
        st.markdown('</div>',unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card"><div class="card-title">2. Find matching records</div><div class="card-sub">Enter one identifier. Cyber Rakshak searches every loaded source and shows where the value appeared.</div>',unsafe_allow_html=True)
        q=st.text_input("Identifier",placeholder="Try: +91-70000-00001  ·  email  ·  account  ·  IP  ·  domain",key="match_query")
        mode=st.selectbox("How should it match?",["Auto","Phone normalized","Email normalized","Account normalized","IP normalized","Domain normalized","Exact raw value"],key="match_mode")
        if q:
            results=search_identifier(q,mode)
            st.markdown(f'<div class="match-head"><div class="match-count">{len(results):,} observed match(es)</div><span class="evidence-tag">SOURCE-TRACEABLE</span></div>',unsafe_allow_html=True)
            if not results.empty:
                st.dataframe(results,width="stretch",hide_index=True,height=310,column_config={"evidence_id":"Evidence ID","matched_value":"Matched value"})
                st.markdown('<div class="notice notice-green"><b>What this means:</b> these records contain a value that matched your search rule. Open the original source record before drawing conclusions.</div>',unsafe_allow_html=True)
            else:
                st.info("No supplied record matched this identifier. Try another format or check whether the relevant source has been loaded.")
        else:
            st.markdown('<div class="notice notice-blue"><b>Example</b><br>Search a phone number such as <b>+91-70000-00001</b>, an email, an account ID, an IP address or a domain. Normalized matching helps common formatting differences line up.</div>',unsafe_allow_html=True)
            st.markdown('<div class="section-label" style="margin-top:16px">What happens after a match?</div>',unsafe_allow_html=True)
            st.markdown('<div class="step"><div class="step-no">A</div><div><b>Confirm the source</b><span>Which organization/dataset supplied the record?</span></div></div><div class="step"><div class="step-no">B</div><div><b>See related identifiers</b><span>Move from the matched record to accounts, devices, domains or incidents that are actually present.</span></div></div><div class="step"><div class="step-no">C</div><div><b>Open the network view</b><span>Use Financial Network or Cyber Network for multi-hop relationships.</span></div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="notice" style="margin-top:2px"><b>Simple rule:</b> Cyber Rakshak connects evidence that you supply or are authorized to use. It does not secretly discover private records, probe a person’s computer, or decide that a person is a criminal.</div>',unsafe_allow_html=True)

# ============================================================
# Financial
# ============================================================
elif nav=="Financial Network":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Financial Network</div><div class="workspace-sub">Follow observed account, phone/email and transaction relationships from authorized financial exports.</div></div>',unsafe_allow_html=True)
    G=get_graph("financial")
    a,b,c=st.columns(3)
    a.metric("Accounts / identifiers",sum(1 for n in G if G.nodes[n].get("node_type") in ("ACCOUNT","PHONE","EMAIL")))
    b.metric("Relationships",G.number_of_edges())
    c.metric("Connected components",nx.number_connected_components(G) if G.number_of_nodes() else 0)
    st.markdown("<br>",unsafe_allow_html=True)
    left,right=st.columns([1.8,1])
    with right:
        focus=st.text_input("Focus identifier",placeholder="Account / phone / email")
        hops=st.slider("Show connections up to",1,3,2)
        if focus and focus in G:
            reachable=nx.single_source_shortest_path_length(G,focus,cutoff=hops)
            st.metric(f"Nodes within {hops} hop(s)",len(reachable)-1)
            st.write("Direct connections:",G.degree(focus))
            st.write("Examples:",list(G.neighbors(focus))[:12])
        elif focus: st.info("That identifier is not a node in the current financial graph.")
        st.markdown('<div class="notice">A transaction relationship shows that the supplied records contain that transaction. It does not establish intent or wrongdoing by itself.</div>',unsafe_allow_html=True)
    with left:
        fig=graph_fig(G,focus=focus if focus else None,max_nodes=110)
        if fig: st.plotly_chart(fig,width="stretch",config={"displayModeBar":False})
        else: st.info("Add financial/account data or load the synthetic demo.")

# ============================================================
# Cyber
# ============================================================
elif nav=="Cyber Network":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Cyber Network</div><div class="workspace-sub">Reconstruct observed relationships from security logs, DNS/proxy exports, domains, IPs, URLs and incident records — without active probing.</div></div>',unsafe_allow_html=True)
    G=get_graph("cyber")
    left,right=st.columns([1.8,1])
    with right:
        focus=st.text_input("Focus IP / domain / incident",placeholder="e.g. 10.10.1.13")
        hops=st.slider("Relationship depth",1,3,2)
        if focus and focus in G:
            reachable=nx.single_source_shortest_path_length(G,focus,cutoff=hops)
            st.metric(f"Nodes within {hops} hop(s)",len(reachable)-1)
            rows=[]
            for n in G.neighbors(focus):
                for _,_,d in G.edges(focus,n,data=True): rows.append({"connected_node":n,"relationship":d.get("rel"),"source":d.get("source")})
            if rows: st.dataframe(pd.DataFrame(rows),width="stretch",hide_index=True)
        elif focus: st.info("That value is not present in the current cyber evidence graph.")
        st.markdown('<div class="notice notice-blue"><b>Network note</b><br>DNS evidence can show observed domain queries/resolution, but DNS alone usually does not reveal the exact search text entered inside an HTTPS website.</div>',unsafe_allow_html=True)
    with left:
        fig=graph_fig(G,focus=focus if focus else None,max_nodes=110)
        if fig: st.plotly_chart(fig,width="stretch",config={"displayModeBar":False})
        else: st.info("Add security/network evidence or load the synthetic demo.")


# ============================================================
# Relationship Graph
# ============================================================
elif nav=="Relationship Graph":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Relationship Graph</div><div class="workspace-sub">Explore the full evidence graph reconstructed only from supplied records. Each edge retains its relationship type and source.</div></div>',unsafe_allow_html=True)
    G=get_graph("all")
    a,b,c=st.columns(3)
    a.metric("Entities",G.number_of_nodes()); b.metric("Observed relationships",G.number_of_edges()); c.metric("Components",nx.number_connected_components(G) if G.number_of_nodes() else 0)
    focus=st.text_input("Focus entity (optional)",placeholder="Phone, account, IP, domain, incident…",key="rg_focus")
    max_nodes=st.slider("Maximum visible nodes",20,180,100,key="rg_nodes")
    fig=graph_fig(G,focus=focus if focus else None,max_nodes=max_nodes)
    if fig: st.plotly_chart(fig,width="stretch",config={"displayModeBar":False})
    else: st.info("Load evidence or the synthetic demo to build the graph.")

# ============================================================
# Multi-Hop Paths
# ============================================================
elif nav=="Multi-Hop Paths":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Multi-Hop Path Finder</div><div class="workspace-sub">Trace how two supplied identifiers are connected through one, two or three observed relationships.</div></div>',unsafe_allow_html=True)
    G=get_graph("all")
    a,b=st.columns(2)
    with a: start=st.text_input("Start entity",key="path_start")
    with b: end=st.text_input("Destination entity",key="path_end")
    hops=st.slider("Maximum hops",1,3,3)
    if st.button("Find observed paths",type="primary",key="find_paths") and start and end:
        if start in G and end in G:
            paths=[]
            try:
                for path in nx.all_simple_paths(G,start,end,cutoff=hops): paths.append(path)
                paths=paths[:20]
            except nx.NetworkXNoPath: paths=[]
            if paths:
                st.success(f"Found {len(paths)} observed path(s) within {hops} hop(s).")
                for i,path in enumerate(paths,1):
                    st.markdown(f'<div class="card"><div class="card-title">Path {i}</div><div class="card-sub">'+' → '.join(path)+'</div></div>',unsafe_allow_html=True)
            else: st.warning("No observed path within the selected depth.")
        else: st.warning("Both identifiers must exist in the supplied evidence graph.")
    st.markdown('<div class="notice notice-blue"><b>Interpretation:</b> a path is an analytical reconstruction of supplied relationships. It is not proof that every intermediate entity belongs to the same person or acted together.</div>',unsafe_allow_html=True)

# ============================================================
# Clusters
# ============================================================
elif nav=="Clusters":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Communities & Clusters</div><div class="workspace-sub">Group densely connected portions of the observed graph so investigators can review evidence communities separately.</div></div>',unsafe_allow_html=True)
    G=get_graph("all")
    if G.number_of_nodes()>1:
        communities=list(nx.community.greedy_modularity_communities(G)) if G.number_of_edges() else [{n} for n in G.nodes()]
        st.metric("Detected communities",len(communities))
        rows=[]
        for i,comm in enumerate(sorted(communities,key=len,reverse=True),1): rows.append({"cluster":f"C-{i:02d}","entities":len(comm),"sample_entities":", ".join(list(comm)[:8])})
        st.dataframe(pd.DataFrame(rows),width="stretch",hide_index=True)
        st.caption("Clusters are graph-structure groupings, not criminal organizations or identity conclusions.")
    else: st.info("Add more connected evidence to detect clusters.")

# ============================================================
# Centrality & Bridges
# ============================================================
elif nav=="Centrality & Bridges":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Centrality & Bridge Analysis</div><div class="workspace-sub">Rank entities by network position. These are prioritization signals for review, not guilt scores.</div></div>',unsafe_allow_html=True)
    G=get_graph("all")
    if G.number_of_nodes()>0:
        deg=nx.degree_centrality(G); btw=nx.betweenness_centrality(G) if G.number_of_nodes()>2 else {n:0 for n in G}
        rows=[{"entity":n,"degree_centrality":round(deg.get(n,0),4),"betweenness":round(btw.get(n,0),4),"degree":G.degree(n),"type":G.nodes[n].get("node_type","")} for n in G.nodes()]
        df=pd.DataFrame(rows).sort_values(["betweenness","degree"],ascending=False)
        st.dataframe(df.head(50),width="stretch",hide_index=True)
        st.markdown('<div class="notice">A bridge candidate is an entity that structurally connects otherwise separated parts of the supplied network. Investigators should inspect the underlying evidence before interpreting why that bridge exists.</div>',unsafe_allow_html=True)
    else: st.info("No network available yet.")

# ============================================================
# Transaction Flow
# ============================================================
elif nav=="Transaction Flow":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Transaction Flow</div><div class="workspace-sub">Inspect observed sender → receiver movement from transaction exports, with amount and time preserved when available.</div></div>',unsafe_allow_html=True)
    rows=[]
    for name,df in all_frames().items():
        mp=infer_columns(df); send=[c for c,t in mp.items() if t=="sender"]; recv=[c for c,t in mp.items() if t=="receiver"]; amt=[c for c,t in mp.items() if t=="amount"]; ts=[c for c,t in mp.items() if t=="timestamp"]
        if send and recv:
            for _,r in df.iterrows(): rows.append({"source_dataset":name,"sender":str(r[send[0]]),"receiver":str(r[recv[0]]),"amount":str(r[amt[0]]) if amt else "","timestamp":str(r[ts[0]]) if ts else ""})
    if rows:
        tf=pd.DataFrame(rows)
        st.metric("Observed transfers",len(tf))
        st.dataframe(tf,width="stretch",hide_index=True,height=420)
        agg=tf.groupby(["sender","receiver"],dropna=False).size().reset_index(name="observed_transactions").sort_values("observed_transactions",ascending=False)
        st.markdown('<div class="section-label">Repeated observed routes</div>',unsafe_allow_html=True)
        st.dataframe(agg.head(30),width="stretch",hide_index=True)
    else: st.info("No sender/receiver transaction fields were detected in the supplied data.")

# ============================================================
# Entity Similarity
# ============================================================
elif nav=="Entity Similarity":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Entity Similarity</div><div class="workspace-sub">Compare entities using shared observed attributes in the supplied datasets. Similarity is a lead for review, not identity proof.</div></div>',unsafe_allow_html=True)
    G=get_graph("all")
    a,b=st.columns(2)
    with a: ea=st.text_input("Entity A",key="sim_a")
    with b: eb=st.text_input("Entity B",key="sim_b")
    if st.button("Compare entities",type="primary",key="compare_entities") and ea and eb:
        if ea in G and eb in G:
            na=set(G.neighbors(ea)); nb=set(G.neighbors(eb)); inter=na & nb; union=na | nb
            score=(len(inter)/len(union)) if union else 0
            st.metric("Jaccard neighborhood similarity",f"{score:.2%}")
            st.write("Shared observed neighbors:",sorted(inter)[:30] or "None")
            st.markdown('<div class="notice notice-blue">Shared graph neighbors can have many legitimate explanations. Use the underlying source records and timestamps for corroboration.</div>',unsafe_allow_html=True)
        else: st.warning("Both entities must be present in supplied evidence.")

# ============================================================
# Timeline
# ============================================================
elif nav=="Timeline":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Investigation Timeline</div><div class="workspace-sub">Put observations in time order so you can inspect sequences instead of isolated rows.</div></div>',unsafe_allow_html=True)
    rows=[]
    for name,df in all_frames().items():
        mp=infer_columns(df); ts=[c for c,t in mp.items() if t=="timestamp"]
        if not ts: continue
        for i,r in df.iterrows(): rows.append({"time":r[ts[0]],"dataset":name,"record":i,"event":json.dumps({k:str(r[k]) for k in df.columns if k!=ts[0]},default=str)[:240]})
    if rows:
        td=pd.DataFrame(rows); td["time_parsed"]=pd.to_datetime(td["time"],errors="coerce"); td=td.sort_values("time_parsed")
        st.line_chart(td.assign(events=1).set_index("time_parsed")["events"].resample("D").sum())
        st.dataframe(td.drop(columns=["time_parsed"]),width="stretch",hide_index=True,height=460)
    else: st.info("No timestamped records are available yet.")

# ============================================================
# AI Correlation
# ============================================================
elif nav=="AI Correlation":
    st.markdown('<div class="workspace-head"><div class="workspace-title">AI-Assisted Correlation</div><div class="workspace-sub">Graph and evidence signals help an investigator decide what to review next. They are not an automated criminality decision.</div></div>',unsafe_allow_html=True)
    G=get_graph("all"); signals=network_signals(G)
    if signals:
        for title,text,t in signals:
            cls="notice" if t=="amber" else "notice notice-blue"
            st.markdown(f'<div class="card"><div class="card-title">{title}</div><div class="card-sub">{text}</div><div class="{cls}">Basis: observed graph structure from supplied datasets.</div></div>',unsafe_allow_html=True)
    else: st.info("No prototype network signal crossed the current thresholds.")
    st.markdown('<div class="card"><div class="card-title">Explain a connection</div><div class="card-sub">Choose two nodes. Cyber Rakshak will show an observed shortest path and the source attached to each relationship.</div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a: node_a=st.text_input("Node A")
    with b: node_b=st.text_input("Node B")
    if st.button("Explain connection",type="primary") and node_a and node_b:
        if node_a in G and node_b in G:
            try:
                path=nx.shortest_path(G,node_a,node_b); st.success("Observed path found")
                st.markdown(" → ".join(path))
                ev=[]
                for x,y in zip(path,path[1:]):
                    for _,_,d in G.edges(x,y,data=True): ev.append({"from":x,"to":y,"relationship":d.get("rel"),"source":d.get("source")})
                st.dataframe(pd.DataFrame(ev),width="stretch",hide_index=True)
            except nx.NetworkXNoPath: st.warning("No observed path exists in the current evidence graph.")
        else: st.warning("One or both nodes are not present in supplied evidence.")
    st.markdown('</div>',unsafe_allow_html=True)


# ============================================================
# Evidence Chain
# ============================================================
elif nav=="Evidence Chain":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Evidence Chain · Why Connected?</div><div class="workspace-sub">Choose two entities and inspect the shortest observed relationship chain together with the source attached to each edge.</div></div>',unsafe_allow_html=True)
    G=get_graph("all")
    a,b=st.columns(2)
    with a: ca=st.text_input("Entity A",key="chain_a")
    with b: cb=st.text_input("Entity B",key="chain_b")
    if st.button("Explain why connected",type="primary",key="why_connected") and ca and cb:
        if ca in G and cb in G:
            try:
                path=nx.shortest_path(G,ca,cb)
                st.success("Observed relationship chain found.")
                st.markdown('<div class="card"><div class="card-title">Chain</div><div class="card-sub">'+' → '.join(path)+'</div></div>',unsafe_allow_html=True)
                ev=[]
                for x,y in zip(path,path[1:]):
                    for _,_,d in G.edges(x,y,data=True): ev.append({"from":x,"to":y,"relationship":d.get("rel",""),"source":d.get("source",""),"evidence_class":"Observed"})
                st.dataframe(pd.DataFrame(ev),width="stretch",hide_index=True)
            except nx.NetworkXNoPath: st.warning("No observed connection exists in the current evidence graph.")
        else: st.warning("Both entities must be present in supplied evidence.")
    st.markdown('<div class="notice notice-green"><b>Evidence discipline:</b> every connection shown here comes from supplied records or graph reconstruction over those records. The system does not infer criminality from connectivity alone.</div>',unsafe_allow_html=True)

# ============================================================
# Ledger
# ============================================================
elif nav=="Evidence Ledger":
    st.markdown('<div class="workspace-head"><div class="workspace-title">Evidence Ledger</div><div class="workspace-sub">A simple record of what was imported, where it came from and when it entered the workspace.</div></div>',unsafe_allow_html=True)
    if st.session_state.ledger:
        ledger=pd.DataFrame(st.session_state.ledger); ledger["evidence_class"]="Observed"
        st.dataframe(ledger,width="stretch",hide_index=True)
        st.download_button("Export provenance CSV",ledger.to_csv(index=False).encode(),"cyber_rakshak_provenance.csv","text/csv",type="primary")
    else: st.info("No evidence sources have been added yet.")
    st.markdown('<div class="notice" style="margin-top:14px"><b>Responsible analysis</b><br>Keep observed facts, corroborated evidence and analytical signals separate. Identity attribution, private-data access and investigative action remain subject to appropriate authorization and human review.</div>',unsafe_allow_html=True)


elif nav=="Evidence Intake":
    st.markdown('<div class="workspace-head"><div class="section-kicker">Evidence intake</div><div class="workspace-title">Add authorized evidence.</div><div class="workspace-sub">Each item receives an evidence ID, timestamp, source label and analytical result. Raw material is not treated as a verdict.</div></div>',unsafe_allow_html=True)
    tabs=st.tabs(["Text / complaint","URL","Transactions","Public-source context","Audio / transcript"])
    with tabs[0]:
        txt=st.text_area("Evidence text",height=180,placeholder="Paste an authorized complaint, incident note, message text or transcript excerpt.")
        src=st.text_input("Source",value="Investigator-provided text",key="text_source")
        if st.button("Analyze & add text evidence",type="primary",key="add_text_ev"):
            if txt.strip():
                add_evidence_item("Text",src,txt,analyze_text(txt)); st.success("Text evidence added to the current case.")
            else: st.warning("Enter evidence text first.")
    with tabs[1]:
        url=st.text_input("URL / domain",placeholder="https://example.org/path")
        src=st.text_input("Source",value="Investigator-provided URL",key="url_source")
        if st.button("Analyze & add URL evidence",type="primary",key="add_url_ev"):
            if url.strip(): add_evidence_item("URL",src,url,analyze_url(url)); st.success("URL evidence added.")
            else: st.warning("Enter a URL or domain first.")
    with tabs[2]:
        up=st.file_uploader("Transaction CSV / Excel",type=["csv","xlsx","xls"],key="ev_tx_upload")
        if up is not None:
            try:
                df=read_upload(up); result=analyze_transactions(df); st.dataframe(df.head(20),width="stretch",hide_index=True)
                if st.button("Add transaction evidence",type="primary",key="add_tx_ev"):
                    add_evidence_item("Transactions",up.name,df.to_json(orient="records",date_format="iso"),result); st.success("Transaction analysis added.")
            except Exception as e: st.error(f"Could not analyze transaction file: {e}")
    with tabs[3]:
        public=st.text_area("Authorized public-source notes / excerpt",height=160,placeholder="Record the public source context you are authorized to analyze.")
        src=st.text_input("Source URL / publication",key="public_source")
        if st.button("Analyze & add public-source evidence",type="primary",key="add_public_ev"):
            if public.strip(): add_evidence_item("Public source",src or "Public source",public,analyze_public(public)); st.success("Public-source evidence added.")
            else: st.warning("Enter source context first.")
    with tabs[4]:
        audio=st.file_uploader("Audio file",type=["wav","mp3","m4a","ogg"],key="audio_ev")
        transcript=st.text_area("Optional authorized transcript",height=120,key="audio_transcript")
        if st.button("Add audio / transcript baseline",type="primary",key="add_audio_ev"):
            if transcript.strip():
                result=analyze_audio(transcript); add_evidence_item("Audio / transcript",audio.name if audio else "Investigator-provided transcript",transcript,result); st.success("Transcript baseline added. Acoustic model validation is not claimed.")
            elif audio: st.info("Audio file received, but this prototype uses a clearly marked baseline and requires a transcript for content analysis.")
            else: st.warning("Provide an authorized transcript or audio file.")
    st.markdown('<div class="notice">Evidence handling boundary: use only data you are authorized to possess and analyze. Do not use this workspace to probe external systems or access private communications.</div>',unsafe_allow_html=True)

elif nav=="AI Analysis":
    st.markdown('<div class="workspace-head"><div class="section-kicker">Part 1 intelligence engine</div><div class="workspace-title">Review explainable evidence signals.</div><div class="workspace-sub">Text, URL, transaction and public-source analyses are preserved alongside their source and evidence ID.</div></div>',unsafe_allow_html=True)
    F=current_fusion(); a,b,c,d=st.columns(4)
    for col,label,val in [(a,"Combined signal",F.get("score",0)),(b,"Coverage",F.get("coverage",0)),(c,"Evidence items",len(st.session_state.evidence)),(d,"Analysis runs",st.session_state.analysis_run)]:
        col.metric(label,val)
    for e in st.session_state.evidence:
        a=e.get('analysis',{}) or {}; score=int(a.get('score',0) or 0); cls='notice-green' if score<40 else 'notice' if score<70 else 'notice-blue'
        with st.expander(f"{e.get('id')} · {e.get('type')} · {e.get('source')}"):
            st.write(f"Timestamp: {e.get('timestamp')}")
            st.markdown(f'<div class="{cls}"><b>Signal score:</b> {score}/100 · <b>Strength:</b> {a.get("strength", "")}</div>',unsafe_allow_html=True)
            if a.get('indicators'): st.write("Indicators:",a.get('indicators'))
            if a.get('entities'): st.write("Extracted entities:",a.get('entities'))
            if a.get('explanation'): st.caption(a.get('explanation'))
            st.code(str(e.get('raw',''))[:1200])
    if not st.session_state.evidence: st.info("Add evidence from Evidence Intake or load the demo data first.")

elif nav=="Risk Assessment":
    F=current_fusion(); st.markdown('<div class="workspace-head"><div class="section-kicker">Risk assessment</div><div class="workspace-title">What does the current evidence support?</div><div class="workspace-sub">This score summarizes analytical indicators; it is not a probability of guilt and does not identify a criminal.</div></div>',unsafe_allow_html=True)
    a,b=st.columns([1,2]);
    with a:
        st.metric("Combined signal",f"{F.get('score',0)}/100")
        st.metric("Risk band",F.get('risk','Low'))
    with b:
        st.markdown('<div class="card"><div class="card-title">Evidence coverage</div>',unsafe_allow_html=True)
        st.write(F.get('coverage_details',{}))
        st.markdown('<div class="notice">Higher signal means more review-worthy indicators in the supplied evidence. It does not establish identity, intent, criminality or legal responsibility.</div></div>',unsafe_allow_html=True)

elif nav=="Report":
    st.markdown('<div class="workspace-head"><div class="section-kicker">Investigation dossier</div><div class="workspace-title">Generate the complete evidence brief.</div><div class="workspace-sub">The report separates observed records from analytical signals and includes limitations.</div></div>',unsafe_allow_html=True)
    report=report_text_full(); st.text_area("Report preview",report,height=520)
    st.download_button("Download TXT report",report.encode(),f"{st.session_state.case['id']}_report.txt","text/plain",type="primary",width="stretch")
    payload={"case":st.session_state.case,"evidence":st.session_state.evidence,"datasets":{k:{"records":len(v),"columns":list(map(str,v.columns))} for k,v in all_frames().items()},"generated_at":now_str()}
    st.download_button("Download complete case JSON",json.dumps(payload,indent=2,default=str).encode(),f"{st.session_state.case['id']}_case.json","application/json",width="stretch")

elif nav=="My Account":
    account_page()

elif nav=="FAQ":
    st.markdown('<div class="workspace-head"><div class="section-kicker">Help / safeguards</div><div class="workspace-title">Frequently asked questions.</div></div>',unsafe_allow_html=True)
    faqs=[
        ("Does the system decide who is a criminal?","No. It produces evidence-supported signals and network associations that require human verification."),
        ("What does a match mean?","A supplied record contains a value that matched the selected normalization rule. It is not proof of ownership or identity."),
        ("What is stored on the server?","Accounts, case metadata, evidence records and dataset provenance metadata are stored in the local SQLite database in this prototype."),
        ("Are passwords stored?","No. Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes."),
        ("Can reports be emailed?","Yes, when SMTP is configured through Streamlit secrets rather than hardcoded credentials."),
        ("Does the graph probe the internet?","No. Network analysis is reconstructed from supplied or authorized records."),
        ("What is the demo identifier?","The bundled synthetic dataset includes +91-70000-00001 for local testing."),
    ]
    for q,a in faqs:
        with st.expander(q): st.write(a)

elif nav=="About Team":
    st.markdown('<div class="workspace-head"><div class="section-kicker">Team Voxshield</div><div class="workspace-title">About Cyber Rakshak.</div><div class="workspace-sub">An academic investigative-support prototype focused on explainable evidence and network analysis.</div></div>',unsafe_allow_html=True)
    members=[("Harsh Sharma","Technical","Application architecture and system integration."),("Avinash Kumar","Research","Evidence methodology and investigation workflow."),("Devansh Gocher","Research","Data interpretation and research workflow."),("Manish Meena","Innovation","Product and feature innovation."),("Krish Pareek","Innovation","Workflow and prototype experience."),("Mahak Gurumukhani","Innovation","User experience and presentation.")]
    for n,r,d in members: st.markdown(f'<div class="card"><b>{n}</b> · <span class="evidence-tag">{r}</span><div class="card-sub">{d}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="notice notice-green"><b>Principle:</b> evidence first, explain every signal, preserve provenance and keep a human decision-maker in the loop.</div>',unsafe_allow_html=True)

elif nav=="Feedback & Reviews":
    st.markdown('<div class="workspace-head"><div class="section-kicker">Product feedback</div><div class="workspace-title">Tell us what to improve.</div><div class="workspace-sub">Feedback is stored separately from investigative case data.</div></div>',unsafe_allow_html=True)
    name=st.text_input("Name",value=st.session_state.auth_user.get('username',''))
    category=st.selectbox("Feedback type",["General review","Feature request","Bug / problem","User experience","Performance","Other"])
    rating=st.slider("Overall rating",1,5,5)
    message=st.text_area("Feedback / review",height=180)
    if st.button("Submit feedback",type="primary",width="stretch"):
        if message.strip(): save_feedback(st.session_state.auth_user['id'],name,category,rating,message); st.success("Feedback saved separately from case data.")
        else: st.warning("Write some feedback first.")

elif nav=="Contact":
    st.markdown('<div class="workspace-head"><div class="section-kicker">Contact</div><div class="workspace-title">Send a project note.</div></div>',unsafe_allow_html=True)
    name=st.text_input("Your name",value=st.session_state.auth_user.get('username',''))
    topic=st.text_input("Topic",placeholder="Support, suggestion, bug, collaboration…")
    message=st.text_area("Message",height=180)
    if st.button("Save note",type="primary",width="stretch"):
        if message.strip(): save_contact_note(st.session_state.auth_user['id'],name,topic,message); st.success("Note saved in the separate feedback database.")
        else: st.warning("Enter a message first.")

elif nav=="Safety & Response":
    st.markdown('<div class="workspace-head"><div class="section-kicker">Safety & official response</div><div class="workspace-title">If the incident is real.</div><div class="workspace-sub">Cyber Rakshak is an analysis aid. Official reporting channels should be used for actual cybercrime complaints.</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="notice notice-blue"><b>Evidence preservation:</b> keep original files/messages, preserve timestamps and source context, record transaction references where relevant, and do not confront anyone based only on an analytical signal.</div>',unsafe_allow_html=True)
    st.link_button('India National Cyber Crime Reporting Portal ↗','https://www.cybercrime.gov.in/',width='stretch')

elif nav=="Report & Email":
    report_email_page()

elif nav=="Admin Console":
    admin_dashboard()


st.markdown('<div class="footer">Cyber Rakshak · Unified Part 1 + Part 2 · Evidence intelligence + network analysis · Server-linked accounts · Human verification required</div>',unsafe_allow_html=True)
