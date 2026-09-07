"""
CYBER RAKSHAK — PART 1 V5
AI-Powered Investigation & Evidence Intelligence
Team Voxshield

V5 adds:
- Public-style Home / User Manual
- Login + Register with secure password hashing
- Persistent SQLite account/case/evidence storage on the server
- Account dashboard + profile/workflow completion percentage
- FAQ, About Team, Contact, Safety & Response
- Multi-language interface: English, Hindi, Tamil, Bengali
- Cleaner navigation and robust evidence Inspect workflow
- Existing local evidence-analysis engine retained

IMPORTANT:
This is an investigative-support prototype. It does NOT determine that a real
person is a criminal. AI signals require evidence validation and human review.
"""
import os
import re
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import streamlit as st

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_OK = True
except Exception:
    SKLEARN_OK = False

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "server_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "cyber_rakshak.sqlite3"

st.set_page_config(page_title="Cyber Rakshak | Voxshield", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');
:root{--bg:#f5f7fa;--surface:#fff;--surface2:#f8fafc;--line:#e4e9ef;--text:#17202b;--muted:#657386;--cyan:#0e7490;--blue:#2563eb;--green:#087f5b;--amber:#a16207;--red:#b4233b}
html,body,[class*="css"]{font-family:Inter,sans-serif}.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:1450px;padding:24px 34px 60px}section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
section[data-testid="stSidebar"]>div{padding:20px 15px}.brand{display:flex;align-items:center;gap:10px}.shield{width:38px;height:38px;border:1px solid #cbd5e1;border-radius:10px;display:flex;align-items:center;justify-content:center;background:#f1f5f9;font-size:19px}.brand-name{font-weight:800;font-size:17px;letter-spacing:.3px}.brand-sub{font:600 9px 'JetBrains Mono';letter-spacing:1px;color:#64748b;margin:4px 0 20px 48px}
.nav-note{font-size:10px;color:#7b8797;line-height:1.45;padding:9px 10px;background:#f8fafc;border:1px solid var(--line);border-radius:9px;margin:10px 0}.hero{background:linear-gradient(135deg,#ffffff,#f0f7fb);border:1px solid #dce5ec;border-radius:18px;padding:30px;margin-bottom:18px}.kicker{font:700 10px 'JetBrains Mono';letter-spacing:1.4px;color:var(--cyan);text-transform:uppercase}.hero-title{font-size:35px;line-height:1.1;font-weight:800;margin-top:7px}.hero-sub{color:#607086;font-size:14px;margin-top:9px;line-height:1.6}.hero-meta{font:600 10px 'JetBrains Mono';color:#64748b}.panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:21px;margin-bottom:16px;box-shadow:0 4px 18px rgba(20,30,45,.035)}.panel-title{font-size:18px;font-weight:800}.panel-sub{font-size:12px;color:var(--muted);margin-top:4px;line-height:1.55}.section-number{font:700 10px 'JetBrains Mono';color:#748297;letter-spacing:.8px}.metric-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px;min-height:98px}.metric-label{font-size:10px;color:#7a8798;text-transform:uppercase;letter-spacing:.7px}.metric-value{font:800 25px 'JetBrains Mono';margin-top:8px}.metric-note{font-size:10px;color:#7a8798;margin-top:3px}.badge{display:inline-flex;padding:5px 9px;border-radius:999px;font:700 10px 'JetBrains Mono';border:1px solid}.badge-low{color:#087f5b;background:#ecfdf5;border-color:#a7f3d0}.badge-med{color:#92400e;background:#fffbeb;border-color:#fde68a}.badge-high{color:#9f1239;background:#fff1f2;border-color:#fecdd3}.badge-info{color:#075985;background:#f0f9ff;border-color:#bae6fd}
.card-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.feature-card{background:#fff;border:1px solid var(--line);border-radius:13px;padding:17px}.feature-icon{font-size:20px}.feature-card b{display:block;margin-top:8px;font-size:13px}.feature-card span{display:block;margin-top:5px;color:#68778b;font-size:11px;line-height:1.55}.step-row{display:flex;border:1px solid var(--line);border-radius:11px;overflow:hidden;background:#f8fafc}.step{flex:1;padding:13px;border-right:1px solid var(--line)}.step:last-child{border-right:0}.step-no{font:700 10px 'JetBrains Mono';color:#8290a2}.step-name{font-size:11px;font-weight:800;margin-top:5px}.step-state{font-size:10px;color:#758296;margin-top:3px}.step.active{background:#eff9fc}.step.active .step-no,.step.active .step-state{color:var(--cyan)}
.finding{background:#f8fafc;border:1px solid #e5eaf0;border-left:3px solid #0e7490;padding:11px 13px;border-radius:8px;margin:8px 0;line-height:1.55;font-size:12px}.finding.warn{border-left-color:#d97706}.finding.danger{border-left-color:#c0264a}.finding.ok{border-left-color:#059669}.evidence-card{background:#f8fafc;border:1px solid var(--line);border-radius:11px;padding:14px;margin-bottom:9px}.ev-top{display:flex;align-items:center;justify-content:space-between;gap:10px}.ev-id{font:700 10px 'JetBrains Mono';color:#718096}.ev-type{font-size:13px;font-weight:800;margin-top:4px}.ev-source{font-size:10px;color:#718096;margin-top:3px}.progress{height:8px;background:#e8edf2;border-radius:99px;overflow:hidden;margin:9px 0}.progress>div{height:100%;border-radius:99px;background:linear-gradient(90deg,#0e7490,#2563eb)}.score-ring{border:1px solid var(--line);border-radius:14px;background:#f8fafc;padding:20px;text-align:center}.score{font:800 40px 'JetBrains Mono'}.score-label{font-size:10px;color:#748297;letter-spacing:1px}.tip{border-left:3px solid #059669;background:#effcf7;padding:12px 14px;border-radius:8px;font-size:12px;line-height:1.55}.danger-note{border-left:3px solid #c0264a;background:#fff3f5;padding:12px 14px;border-radius:8px;font-size:12px;line-height:1.55}.console{background:#101820;color:#e7f2f6;border-radius:12px;padding:14px 16px;margin:12px 0}.console-label{font:700 9px 'JetBrains Mono';letter-spacing:1.3px;color:#71d9ee}.console-text{font-size:12px;margin-top:6px;line-height:1.5}.footer{color:#8995a5;font:500 9px 'JetBrains Mono';text-align:center;margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,.stSelectbox div[data-baseweb="select"]>div{background:#fff!important;color:#17202b!important;border:1px solid #d8e0e8!important;border-radius:9px!important}.stButton>button,.stDownloadButton>button,.stLinkButton a{border-radius:9px!important;border:1px solid #d4dde7!important;background:#fff!important;color:#17202b!important;font-weight:700!important;min-height:40px}.stButton>button:hover,.stDownloadButton>button:hover,.stLinkButton a:hover{border-color:#0e7490!important;background:#f3fafc!important}.stButton>button[kind="primary"]{background:#0e7490!important;color:#fff!important;border-color:#0e7490!important}.stTabs [data-baseweb="tab-list"]{gap:4px;border-bottom:1px solid var(--line)}.stDataFrame{border:1px solid var(--line);border-radius:10px;overflow:hidden}.faq-q{font-weight:800;font-size:13px}.small{font-size:11px;color:#6d7a8c;line-height:1.55}.completion-box{background:#f8fafc;border:1px solid var(--line);border-radius:12px;padding:14px}.login-wrap{max-width:720px;margin:25px auto}.pill{display:inline-block;padding:4px 8px;border-radius:99px;background:#eef6f8;color:#0e6478;font-size:10px;font-weight:800}
@media(max-width:900px){.block-container{padding:18px 14px 40px}.card-grid{grid-template-columns:1fr}.hero-title{font-size:28px}}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE / AUTH ----------------
def db():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def init_db():
    with db() as c:
        c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, dob TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
        c.execute("CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT, subject TEXT, aliases TEXT, description TEXT, priority TEXT, created TEXT, updated_at TEXT, notes TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")
        c.execute("CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL, ev_code TEXT NOT NULL, type TEXT, source TEXT, raw TEXT, analysis_json TEXT, timestamp TEXT, FOREIGN KEY(case_id) REFERENCES cases(id))")
        c.commit()

def hash_password(password, salt=None):
    salt=salt or secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,180000)
    return salt.hex()+":"+digest.hex()

def verify_password(password, stored):
    try:
        s,d=stored.split(':',1); test=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(s),180000).hex(); return secrets.compare_digest(test,d)
    except Exception: return False

def create_user(username,dob,password):
    username=username.strip()
    if len(username)<2: return False,"Name must contain at least 2 characters."
    if len(password)<8: return False,"Use a password of at least 8 characters."
    # Do not require DOB/name inside passwords: predictable credentials are unsafe.
    with db() as c:
        try:
            now=now_str(); c.execute("INSERT INTO users(username,dob,password_hash,created_at,updated_at) VALUES(?,?,?,?,?)",(username,dob,hash_password(password),now,now)); c.commit(); return True,"Account created successfully."
        except sqlite3.IntegrityError: return False,"An account with this name already exists."

def login_user(username,password):
    with db() as c:
        row=c.execute("SELECT * FROM users WHERE lower(username)=lower(?)",(username.strip(),)).fetchone()
    if row and verify_password(password,row['password_hash']): return dict(row)
    return None

def get_cases(user_id):
    with db() as c: return [dict(x) for x in c.execute("SELECT * FROM cases WHERE user_id=? ORDER BY updated_at DESC",(user_id,)).fetchall()]

def save_case(case,user_id,notes=""):
    now=now_str()
    with db() as c:
        c.execute("INSERT INTO cases(id,user_id,title,subject,aliases,description,priority,created,updated_at,notes) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,subject=excluded.subject,aliases=excluded.aliases,description=excluded.description,priority=excluded.priority,updated_at=excluded.updated_at,notes=excluded.notes",(case['id'],user_id,case.get('title',''),case.get('subject',''),case.get('aliases',''),case.get('description',''),case.get('priority','Medium'),case.get('created',now),now,notes)); c.commit()

def save_evidence(case_id,evidence):
    with db() as c:
        c.execute("DELETE FROM evidence WHERE case_id=?",(case_id,))
        for e in evidence: c.execute("INSERT INTO evidence(case_id,ev_code,type,source,raw,analysis_json,timestamp) VALUES(?,?,?,?,?,?,?)",(case_id,e['id'],e['type'],e['source'],str(e['raw']),json.dumps(e['analysis'],default=str),e['timestamp']))
        c.commit()

def load_evidence(case_id):
    with db() as c: rows=c.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY id",(case_id,)).fetchall()
    out=[]
    for r in rows:
        try: analysis=json.loads(r['analysis_json'])
        except Exception: analysis={}
        out.append({'id':r['ev_code'],'type':r['type'],'source':r['source'],'raw':r['raw'],'analysis':analysis,'timestamp':r['timestamp']})
    return out

def now_str(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

init_db()

# ------------------------------ ANALYSIS ENGINE ----------------------------
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
TR={
"en":{"home":"Home","account":"My Account","invest":"Investigation","intake":"Evidence Intake","analysis":"AI Analysis","risk":"Risk Assessment","report":"Report","faq":"FAQ","about":"About Team","contact":"Contact","safety":"Safety & Response","login":"Login","register":"Register","logout":"Logout","welcome":"Welcome to Cyber Rakshak","manual":"User Manual","new":"New Investigation","save":"Save Case","profile":"Profile completion","workflow":"Investigation completion"},
"hi":{"home":"होम","account":"मेरा अकाउंट","invest":"जांच","intake":"साक्ष्य संग्रह","analysis":"AI विश्लेषण","risk":"जोखिम आकलन","report":"रिपोर्ट","faq":"सामान्य प्रश्न","about":"टीम के बारे में","contact":"संपर्क","safety":"साइबर सुरक्षा","login":"लॉगिन","register":"रजिस्टर","logout":"लॉगआउट","welcome":"Cyber Rakshak में आपका स्वागत है","manual":"उपयोगकर्ता मैनुअल","new":"नई जांच","save":"केस सेव करें","profile":"प्रोफाइल पूर्णता","workflow":"जांच पूर्णता"},
"ta":{"home":"முகப்பு","account":"என் கணக்கு","invest":"விசாரணை","intake":"சான்றுகள்","analysis":"AI பகுப்பாய்வு","risk":"ஆபத்து மதிப்பீடு","report":"அறிக்கை","faq":"கேள்விகள்","about":"குழு பற்றி","contact":"தொடர்பு","safety":"சைபர் பாதுகாப்பு","login":"உள்நுழைவு","register":"பதிவு","logout":"வெளியேறு","welcome":"Cyber Rakshak-க்கு வரவேற்கிறோம்","manual":"பயனர் கையேடு","new":"புதிய விசாரணை","save":"வழக்கை சேமி","profile":"சுயவிவர நிறைவு","workflow":"விசாரணை நிறைவு"},
"bn":{"home":"হোম","account":"আমার অ্যাকাউন্ট","invest":"তদন্ত","intake":"প্রমাণ গ্রহণ","analysis":"AI বিশ্লেষণ","risk":"ঝুঁকি মূল্যায়ন","report":"রিপোর্ট","faq":"প্রশ্নোত্তর","about":"টিম সম্পর্কে","contact":"যোগাযোগ","safety":"সাইবার নিরাপত্তা","login":"লগইন","register":"রেজিস্টার","logout":"লগআউট","welcome":"Cyber Rakshak-এ স্বাগতম","manual":"ব্যবহারকারী নির্দেশিকা","new":"নতুন তদন্ত","save":"কেস সংরক্ষণ","profile":"প্রোফাইল সম্পূর্ণতা","workflow":"তদন্ত সম্পূর্ণতা"}}

def t(k): return TR.get(st.session_state.get('lang','en'),TR['en']).get(k,k)

def default_case(): return {"id":f"INV-{datetime.now().year}-{np.random.randint(100,999)}","title":"","subject":"","aliases":"","description":"","priority":"Medium","created":now_str()}

def init_state():
    if 'lang' not in st.session_state: st.session_state.lang='en'
    if 'auth_user' not in st.session_state: st.session_state.auth_user=None
    if 'case' not in st.session_state: st.session_state.case=default_case()
    if 'evidence' not in st.session_state: st.session_state.evidence=[]
    if 'nav' not in st.session_state: st.session_state.nav='Home'
    if 'analysis_run' not in st.session_state: st.session_state.analysis_run=0
    if 'notes' not in st.session_state: st.session_state.notes=''
    if 'selected_ev' not in st.session_state: st.session_state.selected_ev=None
    if 'auth_mode' not in st.session_state: st.session_state.auth_mode='login'

def persist_current():
    u=st.session_state.auth_user
    if u:
        save_case(st.session_state.case,u['id'],st.session_state.notes)
        save_evidence(st.session_state.case['id'],st.session_state.evidence)

def reset_case():
    st.session_state.case=default_case(); st.session_state.evidence=[]; st.session_state.notes=''; st.session_state.selected_ev=None
    if st.session_state.auth_user: persist_current()
    print('[CYBER RAKSHAK] new investigation created:',st.session_state.case['id'])

def workflow_completion():
    c=st.session_state.case; e=st.session_state.evidence; F=fusion(e)
    checks=[bool(c.get('title')),bool(c.get('description')),bool(e),F['coverage']>=1,F['score']>=40, bool(st.session_state.notes), len(e)>=2]
    return int(round(sum(checks)/len(checks)*100))

def profile_completion():
    u=st.session_state.auth_user
    if not u:return 0
    checks=[bool(u.get('username')),bool(u.get('dob'))]
    return int(sum(checks)/len(checks)*100)

def lvl(score): return 'high' if score>=70 else 'moderate' if score>=40 else 'low'
def badge(text,level='info'): return f"<span class='badge badge-{level}'>{text}</span>"

init_state()


# ---------------- LOGIN / REGISTER ----------------
def auth_screen():
    st.markdown("<div class='login-wrap'>",unsafe_allow_html=True)
    st.markdown("<div class='hero'><div class='kicker'>TEAM VOXSHIELD · SECURE WORKSPACE</div><div class='hero-title'>🛡️ Cyber Rakshak</div><div class='hero-sub'>AI-assisted evidence intelligence for structured cyber investigation and human-led review.</div></div>",unsafe_allow_html=True)
    tabs=st.tabs(["🔐 Login","📝 Register"])
    with tabs[0]:
        with st.form('login_form'):
            name=st.text_input('Username / Name',placeholder='Enter the name used during registration')
            password=st.text_input('Password',type='password',placeholder='Enter your password')
            ok=st.form_submit_button('Login',type='primary',use_container_width=True)
        if ok:
            user=login_user(name,password)
            if user:
                st.session_state.auth_user=user
                cases=get_cases(user['id'])
                if cases:
                    st.session_state.case={k:cases[0].get(k,'') for k in ['id','title','subject','aliases','description','priority','created']}
                    st.session_state.notes=cases[0].get('notes','') or ''
                    st.session_state.evidence=load_evidence(st.session_state.case['id'])
                else: st.session_state.case=default_case(); st.session_state.evidence=[]
                st.session_state.nav='Home'; st.rerun()
            else: st.error('Login failed. Check the registered name and password.')
        st.markdown("<div class='tip'><b>Login guidance:</b> Use the exact name and password you created during registration. Your case information is restored from the server-side SQLite database when available.</div>",unsafe_allow_html=True)
    with tabs[1]:
        with st.form('register_form'):
            name=st.text_input('Name / Username',placeholder='e.g. Analyst One')
            dob=st.date_input('Date of birth',value=date(2000,1,1),min_value=date(1900,1,1),max_value=date.today())
            password=st.text_input('Create password',type='password',help='Use 8+ characters with a mix of letters, numbers and symbols. Do not use a predictable DOB-only password.')
            confirm=st.text_input('Confirm password',type='password')
            st.caption('For security, Cyber Rakshak stores a salted password hash—not the plain password. A predictable password made from name + DOB is not recommended.')
            ok=st.form_submit_button('Create account',type='primary',use_container_width=True)
        if ok:
            if password!=confirm: st.error('Passwords do not match.')
            else:
                good,msg=create_user(name,dob.isoformat(),password)
                if good: st.success(msg+' You can now use the Login tab.'); print('[CYBER RAKSHAK] new user account created')
                else: st.error(msg)
    st.markdown("</div>",unsafe_allow_html=True)

if not st.session_state.auth_user:
    auth_screen(); st.stop()

USER=st.session_state.auth_user

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("<div class='brand'><div class='shield'>🛡️</div><div class='brand-name'>CYBER RAKSHAK</div></div><div class='brand-sub'>TEAM VOXSHIELD · PART 1</div>",unsafe_allow_html=True)
    st.selectbox('Language / भाषा',list(LANGS.keys()),index=list(LANGS.values()).index(st.session_state.lang),key='language_select')
    st.session_state.lang=LANGS[st.session_state.language_select]
    pages=['Home','My Account','Investigation','Evidence Intake','AI Analysis','Risk Assessment','Report','FAQ','About Team','Contact','Safety & Response']
    labels=[t('home'),t('account'),t('invest'),t('intake'),t('analysis'),t('risk'),t('report'),t('faq'),t('about'),t('contact'),t('safety')]
    # Radio values are stable English internal names.
    current_idx=pages.index(st.session_state.nav) if st.session_state.nav in pages else 0
    chosen_label=st.radio('Navigation',labels,index=current_idx,label_visibility='collapsed')
    selected=pages[labels.index(chosen_label)]
    st.session_state.nav=selected
    st.divider()
    C=st.session_state.case; F=fusion(st.session_state.evidence)
    st.markdown(f"<div class='small'><b>ACCOUNT</b><br>{USER['username']}<br><span class='pill'>{workflow_completion()}% investigation complete</span></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='nav-note'>Current case: <b>{C['id']}</b><br>Evidence: <b>{len(st.session_state.evidence)}</b> · Signal: <b>{F['score']}/100</b></div>",unsafe_allow_html=True)
    if st.button('＋ '+t('new'),use_container_width=True):
        persist_current(); st.session_state.case=default_case(); st.session_state.evidence=[]; st.session_state.notes=''; st.session_state.nav='Investigation'; st.rerun()
    if st.button('💾 Save to server',use_container_width=True): persist_current(); st.success('Saved to server database.')
    if st.button('↪ '+t('logout'),use_container_width=True): persist_current(); st.session_state.auth_user=None; st.rerun()

# ---------------- TOP BAR ----------------
C=st.session_state.case; F=fusion(st.session_state.evidence)
if selected not in ['Home','FAQ','About Team','Contact','Safety & Response','My Account']:
    st.markdown(f"<div class='hero'><div style='display:flex;justify-content:space-between;gap:20px'><div><div class='kicker'>CYBER RAKSHAK · EVIDENCE INTELLIGENCE</div><div class='hero-title'>{C['title'] or 'Investigation Workspace'}</div><div class='hero-sub'>Evidence-led analysis, explainable signals and human verification.</div></div><div style='text-align:right'><div class='hero-meta'>{C['id']}</div>{badge(F['risk'],lvl(F['score']))}</div></div></div>",unsafe_allow_html=True)

# ---------------- HOME ----------------
if selected=='Home':
    st.markdown("<div class='hero'><div class='kicker'>AI-ASSISTED CYBER INVESTIGATION PLATFORM · TEAM VOXSHIELD</div><div class='hero-title'>🛡️ Cyber Rakshak</div><div class='hero-sub'>A simple workspace for collecting authorized evidence, analyzing multiple signals, correlating technical identifiers and preparing a traceable investigation brief.</div><div style='margin-top:15px'>"+badge('HUMAN VERIFICATION REQUIRED','info')+"</div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='panel'><div class='section-number'>01 · {t('manual').upper()}</div><div class='panel-title'>{t('welcome')} — how to use the platform</div><div class='panel-sub'>Start with the investigation question, add evidence, run analysis, review the explanation, and generate a report. The system supports investigation; it does not decide criminal guilt.</div></div>",unsafe_allow_html=True)
    steps=[('01','Create account','Register with your name, date of birth and a strong password.'),('02','Create case','Define the investigation title, subject/entity and question.'),('03','Add evidence','Add message text, URLs, transcripts, transaction CSVs or public-source context.'),('04','Run AI analysis','Review local NLP, URL and transaction anomaly signals.'),('05','Correlate','Check repeated identifiers and independent evidence types.'),('06','Report','Review limitations, analyst notes and export the investigation brief.')]
    st.markdown("<div class='step-row'>"+''.join(f"<div class='step'><div class='step-no'>{a}</div><div class='step-name'>{b}</div><div class='step-state'>{c}</div></div>" for a,b,c in steps)+"</div>",unsafe_allow_html=True)
    st.markdown("<div class='card-grid'>"+''.join([
        "<div class='feature-card'><div class='feature-icon'>📥</div><b>Evidence Intake</b><span>Organize text, URLs, transcripts and transaction evidence with source labels.</span></div>",
        "<div class='feature-card'><div class='feature-icon'>🧠</div><b>Explainable AI</b><span>See indicators, entities and analytical explanations instead of a black-box verdict.</span></div>",
        "<div class='feature-card'><div class='feature-icon'>🔗</div><b>Cross-source correlation</b><span>Identify technical identifiers repeated across independent evidence types.</span></div>",
        "<div class='feature-card'><div class='feature-icon'>📊</div><b>Risk / signal view</b><span>Review investigative signal strength separately from factual criminality.</span></div>",
        "<div class='feature-card'><div class='feature-icon'>📝</div><b>Traceable report</b><span>Generate a concise evidence-led brief with provenance and limitations.</span></div>",
        "<div class='feature-card'><div class='feature-icon'>🇮🇳</div><b>Cyber safety</b><span>Quick access to India's official cybercrime reporting information.</span></div>"])+"</div>",unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a:
        if st.button('🚀 Start / Continue Investigation',type='primary',use_container_width=True): st.session_state.nav='Investigation'; st.rerun()
    with b:
        if st.button('📘 Open User Manual',use_container_width=True): st.session_state.nav='FAQ'; st.rerun()
    with c:
        if st.button('🛡️ Safety & Reporting',use_container_width=True): st.session_state.nav='Safety & Response'; st.rerun()
    st.markdown("<div class='console'><div class='console-label'>ANALYST CONSOLE</div><div class='console-text'>Good investigators do not rush to a conclusion — they strengthen the evidence chain. Preserve sources, timestamps and context.</div></div>",unsafe_allow_html=True)

# ---------------- ACCOUNT ----------------
elif selected=='My Account':
    st.markdown(f"<div class='hero'><div class='kicker'>ACCOUNT CENTER</div><div class='hero-title'>{t('account')}</div><div class='hero-sub'>Your account and saved investigation workspace.</div></div>",unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        st.markdown(f"<div class='completion-box'><b>{t('profile')}</b><div class='progress'><div style='width:{profile_completion()}%'></div></div><b>{profile_completion()}%</b><div class='small'>Name and date of birth are stored with your account. Passwords are stored as salted hashes.</div></div>",unsafe_allow_html=True)
    with b:
        wc=workflow_completion(); st.markdown(f"<div class='completion-box'><b>{t('workflow')}</b><div class='progress'><div style='width:{wc}%'></div></div><b>{wc}%</b><div class='small'>Based on case definition, evidence coverage, analysis signal, corroboration, notes and investigation depth.</div></div>",unsafe_allow_html=True)
    st.markdown("<div class='panel'><div class='panel-title'>Account details</div>",unsafe_allow_html=True)
    st.write(f"**Name / Username:** {USER['username']}")
    st.write(f"**Date of birth:** {USER['dob']}")
    st.write(f"**Account created:** {USER['created_at']}")
    st.write(f"**Database:** server_data/cyber_rakshak.sqlite3")
    st.markdown("</div>",unsafe_allow_html=True)
    cases=get_cases(USER['id'])
    st.markdown("<div class='panel'><div class='panel-title'>Saved investigations</div>",unsafe_allow_html=True)
    if cases:
        st.dataframe(pd.DataFrame([{k:x.get(k,'') for k in ['id','title','subject','priority','updated_at']} for x in cases]),use_container_width=True,hide_index=True)
    else: st.info('No saved investigations yet. Create your first case from Investigation.')
    st.markdown("</div>",unsafe_allow_html=True)

# ---------------- INVESTIGATION ----------------
elif selected=='Investigation':
    st.markdown("<div class='panel'><div class='section-number'>01 · CASE SETUP</div><div class='panel-title'>Define the investigation question</div><div class='panel-sub'>Only record the subject/entity information you are authorized to investigate.</div>",unsafe_allow_html=True)
    with st.form('case_form'):
        a,b=st.columns(2)
        with a:
            title=st.text_input('Investigation title',C.get('title',''),placeholder='e.g. Suspicious payment investigation')
            subject=st.text_input('Subject / entity',C.get('subject',''),placeholder='Person, organization, account or technical identifier')
            aliases=st.text_input('Known aliases / identifiers',C.get('aliases',''))
        with b:
            priority=st.selectbox('Priority',['Low','Medium','High','Critical'],index=['Low','Medium','High','Critical'].index(C.get('priority','Medium')))
            desc=st.text_area('Investigation question / description',C.get('description',''),height=125,placeholder='What does the available evidence need to establish?')
        notes=st.text_area('Analyst notes',st.session_state.notes,height=100,placeholder='Record observations, provenance checks or follow-up questions.')
        save=st.form_submit_button('💾 '+t('save'),type='primary',use_container_width=True)
    if save:
        C.update({'title':title,'subject':subject,'aliases':aliases,'description':desc,'priority':priority}); st.session_state.notes=notes; persist_current(); st.success('Case saved permanently to the server database.'); print('[CYBER RAKSHAK] case saved:',C['id'])
    st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div class='panel'><div class='panel-title'>Quick start</div><div class='card-grid'><div class='feature-card'><b>🧪 Safe demo</b><span>Loads synthetic evidence only.</span></div><div class='feature-card'><b>📥 Evidence</b><span>Use Evidence Intake to add your own authorized data.</span></div><div class='feature-card'><b>🔎 Review</b><span>Inspect every evidence item before relying on its signal.</span></div></div></div>",unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        if st.button('🧪 Load safe demo evidence',use_container_width=True):
            demo_text='Your account will be suspended today. Verify your account immediately using the secure login link and send the OTP to complete verification.'
            add_ev('TEXT / MESSAGE','Synthetic demo',demo_text,analyze_text(demo_text)); demo_url='http://secure-account.example/login/verify-otp'; add_ev('URL / LINK','Synthetic demo',demo_url,analyze_url(demo_url)); persist_current(); st.toast('Synthetic demo evidence loaded'); st.rerun()
    with b:
        if st.button('🧹 Clear evidence',use_container_width=True): st.session_state.evidence=[]; persist_current(); st.rerun()

# ---------------- EVIDENCE INTAKE ----------------
elif selected=='Evidence Intake':
    st.markdown("<div class='panel'><div class='section-number'>02 · EVIDENCE INTAKE</div><div class='panel-title'>Add authorized evidence</div><div class='panel-sub'>Each item is stored with source, timestamp and analysis output. Avoid uploading secrets or data you are not authorized to process.</div>",unsafe_allow_html=True)
    typ=st.selectbox('Evidence type',['TEXT / MESSAGE','URL / LINK','AUDIO TRANSCRIPT','PUBLIC SOURCE','TRANSACTION CSV'])
    source=st.text_input('Source / provenance',placeholder='e.g. User supplied, synthetic demo, official registry')
    if typ in ['TEXT / MESSAGE','AUDIO TRANSCRIPT','PUBLIC SOURCE']:
        raw=st.text_area('Evidence content',height=180,placeholder='Paste the content here...')
        if st.button('＋ Add & analyze evidence',type='primary',use_container_width=True):
            if raw.strip():
                fn={'TEXT / MESSAGE':analyze_text,'AUDIO TRANSCRIPT':analyze_audio,'PUBLIC SOURCE':analyze_public}[typ]; add_ev(typ,source,raw,fn(raw)); persist_current(); st.success('Evidence added and saved.'); st.rerun()
            else: st.warning('Enter evidence content first.')
    elif typ=='URL / LINK':
        raw=st.text_input('URL',placeholder='https://example.com/login')
        if st.button('＋ Add & analyze URL',type='primary',use_container_width=True):
            if raw.strip(): add_ev(typ,source,raw,analyze_url(raw)); persist_current(); st.success('URL added and saved.'); st.rerun()
            else: st.warning('Enter a URL first.')
    else:
        up=st.file_uploader('Upload transaction CSV',type=['csv'])
        st.caption('Required columns: Sender, Receiver, Amount, Timestamp')
        if up is not None:
            try: df=pd.read_csv(up); st.dataframe(df.head(10),use_container_width=True,hide_index=True)
            except Exception as ex: st.error(f'Could not read CSV: {ex}'); df=None
            if df is not None and st.button('＋ Analyze transaction file',type='primary',use_container_width=True): add_ev(typ,source,{'rows':len(df)},analyze_transactions(df)); persist_current(); st.success('Transaction analysis added and saved.'); st.rerun()
    st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div class='panel'><div class='panel-title'>Evidence ledger</div>",unsafe_allow_html=True)
    if not st.session_state.evidence: st.markdown("<div class='empty'>No evidence yet. Add an item above or load the safe synthetic demo.</div>",unsafe_allow_html=True)
    for idx,e in enumerate(st.session_state.evidence):
        a=e['analysis']; lev=lvl(a.get('score',0))
        c1,c2,c3=st.columns([1.6,4,1])
        with c1: st.markdown(f"<div class='evidence-card'><div class='ev-id'>{e['id']}</div><div class='ev-type'>{e['type']}</div><div class='ev-source'>{e['source']}</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"{badge(str(a.get('score',0))+'/100',lev)} <span class='small'>{a.get('strength','')}</span><div class='small'>{'; '.join(a.get('indicators',[])[:2])}</div>",unsafe_allow_html=True)
        with c3:
            if st.button('Inspect',key=f'inspect_{e["id"]}_{idx}',use_container_width=True): st.session_state.selected_ev=e['id']
            if st.button('Remove',key=f'remove_{e["id"]}_{idx}',use_container_width=True): st.session_state.evidence=[x for x in st.session_state.evidence if x['id']!=e['id']]; st.session_state.selected_ev=None; persist_current(); st.rerun()
        if st.session_state.selected_ev==e['id']:
            with st.expander(f"Inspection · {e['id']}",expanded=True):
                st.write('**Source:**',e['source']); st.write('**Timestamp:**',e['timestamp']); st.write('**Raw evidence:**',e['raw']); st.write('**Indicators:**'); [st.markdown('• '+x) for x in a.get('indicators',[])]; st.write('**Entities:**',a.get('entities',[])); st.info(a.get('explanation','No explanation available.'))
    st.markdown("</div>",unsafe_allow_html=True)

# ---------------- AI ANALYSIS ----------------
elif selected=='AI Analysis':
    st.markdown("<div class='panel'><div class='section-number'>03 · AI ANALYSIS</div><div class='panel-title'>Run the intelligence pass</div><div class='panel-sub'>Local analysis combines content indicators, structural URL checks, transaction anomaly signals and entity extraction.</div>",unsafe_allow_html=True)
    if st.button('🧠 Run full intelligence pass',type='primary',use_container_width=True):
        st.session_state.analysis_run+=1; persist_current(); print(f'[CYBER RAKSHAK] full intelligence pass run={st.session_state.analysis_run} evidence={len(st.session_state.evidence)}'); st.success('Analysis refreshed from the current evidence ledger.'); st.rerun()
    cols=st.columns(4)
    for col,label,val in zip(cols,['Evidence units','Evidence types','Entities','Corroborated'],[len(st.session_state.evidence),F['coverage'],len(F['entities']),len(F['corroborated'])]): col.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{val}</div><div class='metric-note'>current case</div></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    for e in st.session_state.evidence:
        a=e['analysis']; lev=lvl(a.get('score',0)); st.markdown(f"<div class='panel'><div class='panel-title'>{e['id']} · {e['type']} {badge(str(a.get('score',0))+'/100',lev)}</div><div class='panel-sub'>{e['source']} · {e['timestamp']}</div>",unsafe_allow_html=True)
        for ind in a.get('indicators',[]): st.markdown(f"<div class='finding {'danger' if lev=='high' else 'warn' if lev=='moderate' else 'ok'}'>• {ind}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='tip'><b>Explanation:</b> {a.get('explanation','')}</div></div>",unsafe_allow_html=True)
    if not st.session_state.evidence: st.info('Add evidence first. The analysis page does not generate conclusions from empty input.')

# ---------------- RISK ----------------
elif selected=='Risk Assessment':
    st.markdown("<div class='panel'><div class='section-number'>04 · EXPLAINABLE ASSESSMENT</div><div class='panel-title'>What does the evidence currently support?</div><div class='panel-sub'>This is an investigative signal, not a probability of criminality or a criminal verdict.</div>",unsafe_allow_html=True)
    a,b=st.columns([1.15,.85])
    with a: st.markdown(f"<div class='score-ring'><div class='score'>{F['score']}<span style='font-size:18px;color:#748297'>/100</span></div><div class='score-label'>COMPOSITE INVESTIGATIVE SIGNAL</div><div style='margin-top:12px'>{badge(F['risk'],lvl(F['score']))}</div><div class='progress'><div style='width:{F['score']}%'></div></div></div>",unsafe_allow_html=True)
    with b:
        action={'NETWORK_REVIEW':'Further human review + future network analysis','HUMAN_REVIEW':'Human review recommended','CONTINUE_REVIEW':'Continue evidence collection','ADD_EVIDENCE':'Add evidence'}[F['action']]
        st.markdown(f"<div class='finding {'danger' if F['score']>=70 else 'warn' if F['score']>=40 else 'ok'}'><b>Recommended next step</b><br>{action}</div>",unsafe_allow_html=True)
        for r in [f"Evidence modalities: {F['coverage']}",f"Corroborated technical entities: {len(F['corroborated'])}",f"Evidence units: {len(st.session_state.evidence)}"]: st.markdown(f"<div class='finding'>✓ {r}</div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if F['breakdown']: st.markdown("<div class='panel'><div class='panel-title'>Signal decomposition</div>",unsafe_allow_html=True); st.dataframe(pd.DataFrame(F['breakdown']),use_container_width=True,hide_index=True); st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div class='panel'><div class='panel-title'>Safeguards</div>"+''.join(f"<div class='evidence-card'>• {x}</div>" for x in ['An indicator is not proof of criminal conduct.','Entity ownership and attribution require independent verification.','Public-source information can be incomplete or misattributed.','Demographic, appearance, accent, emotion and protected traits are not used.'])+"</div>",unsafe_allow_html=True)

# ---------------- REPORT ----------------
elif selected=='Report':
    lines=['CYBER RAKSHAK — INVESTIGATION INTELLIGENCE BRIEF','='*70,f'Case: {C["id"]}',f'Title: {C.get("title") or "Untitled Investigation"}',f'Subject/entity: {C.get("subject") or "Not specified"}',f'Generated: {now_str()}',f'ASSESSMENT: {F["risk"]}',f'COMPOSITE SIGNAL: {F["score"]}/100',f'EVIDENCE TYPES: {F["coverage"]}','','This is investigative triage output, not a criminal verdict. Human verification is required.','']
    for e in st.session_state.evidence:
        a=e['analysis']; lines.append(f'[{e["id"]}] {e["type"]} | source={e["source"]} | signal={a.get("score",0)}/100'); lines += ['  - '+x for x in a.get('indicators',[])]
    lines += ['','CROSS-SOURCE FINDINGS']+['- '+x['title']+': '+x['finding'] for x in F['correlations']]+['','ANALYST NOTES',st.session_state.notes or 'No analyst notes recorded.','','LIMITATIONS','- Source provenance must be validated.','- Entity attribution requires verification.','- Automated output must not be treated as a criminal determination.']
    report='\n'.join(lines)
    st.markdown("<div class='panel'><div class='section-number'>05 · REPORT</div><div class='panel-title'>Evidence-led investigation brief</div><div class='panel-sub'>Generated from the current saved case state.</div>",unsafe_allow_html=True)
    st.text_area('Report preview',report,height=400,label_visibility='collapsed')
    a,b=st.columns(2)
    with a: st.download_button('⬇ Download .txt',report,file_name=f'{C["id"]}_investigation.txt',mime='text/plain',use_container_width=True)
    with b: st.download_button('⬇ Download case .json',json.dumps({'case':C,'assessment':F,'evidence':st.session_state.evidence,'notes':st.session_state.notes},indent=2,default=str),file_name=f'{C["id"]}_case.json',mime='application/json',use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

# ---------------- FAQ ----------------
elif selected=='FAQ':
    st.markdown("<div class='hero'><div class='kicker'>HELP CENTER</div><div class='hero-title'>Frequently Asked Questions</div><div class='hero-sub'>Common questions about Cyber Rakshak, evidence, AI signals, accounts, privacy and reporting.</div></div>",unsafe_allow_html=True)
    faqs=[
    ('What is Cyber Rakshak?','An AI-assisted evidence intelligence prototype that organizes authorized evidence, extracts technical entities, identifies analytical indicators and prepares an explainable investigation brief.'),
    ('Does it decide whether someone is a criminal?','No. It produces investigative signals only. Criminality requires verified evidence and appropriate human/legal processes.'),
    ('What evidence can I analyze?','Text/messages, URLs, audio transcripts, public-source text and transaction CSV data are supported in Part 1.'),
    ('Can I upload an audio recording directly?','Part 1 analyzes an audio transcript. A future version can add speech-to-text as a separate controlled module.'),
    ('How does URL analysis work?','It checks structural characteristics such as HTTP use, unusual length, deep subdomains, raw IP hosts and credential-related terms. It is not a live reputation verdict.'),
    ('How are transactions analyzed?','The prototype uses statistical anomaly detection and simple relationship features such as fan-out and repeated amounts.'),
    ('What does the score mean?','It represents the strength of combined investigative indicators, not the probability that a person committed a crime.'),
    ('Why does corroboration matter?','A technical identifier appearing across independent evidence types can provide a stronger lead than a single isolated signal.'),
    ('Is the AI always correct?','No. Data can be incomplete, noisy, outdated or misattributed. Human verification is required.'),
    ('Does it use appearance, gender, accent or emotion?','No. Those characteristics are not valid evidence for criminality and are intentionally excluded.'),
    ('Where is my account data stored?','The prototype stores accounts, cases and evidence in a server-side SQLite database at server_data/cyber_rakshak.sqlite3.'),
    ('Is my password stored directly?','No. The application stores a salted PBKDF2-SHA256 password hash rather than plain text.'),
    ('Can I use my name + DOB as my password?','You should not. That creates a predictable password. Use a unique password of 8+ characters with letters, numbers and symbols.'),
    ('Will my case return after login?','Yes, when the same server database is available. The latest saved case and its evidence are restored to the workspace.'),
    ('What is the completion percentage?','It summarizes progress through case definition, evidence coverage, analysis, corroboration and analyst notes. It is a workflow metric, not a criminality score.'),
    ('Can this be deployed online?','Yes, but persistent production storage should use a managed database such as PostgreSQL rather than relying on a local SQLite file.'),
    ('Can I access it from Android?','Yes. When deployed as a web application, the same interface can be opened in a mobile browser.'),
    ('What if I am a victim of cyber fraud in India?','Use the official National Cyber Crime Reporting Portal and the official reporting channels. For financial cyber fraud, report immediately through the official 1930 helpline.'),
    ('Can I report a suspicious identifier?','India’s official cybercrime portal provides a Report Suspect facility for certain URLs, phone numbers, email IDs, social-media URLs and other identifiers.'),
    ('What is Part 2?','The planned next stage is network analysis: entity resolution, relationship graphs, timelines and cross-case technical correlation with human review.'),
    ('Who created Cyber Rakshak?','Team Voxshield: Harsh Sharma (Technical), Avinash Kumar and Devansh Gocher (Research), Manish Meena, Krish Pareek and Mahak Gurumukhani (Innovation).')]
    for q,a in faqs:
        with st.expander(q): st.write(a)

# ---------------- ABOUT ----------------
elif selected=='About Team':
    st.markdown("<div class='hero'><div class='kicker'>TEAM VOXSHIELD</div><div class='hero-title'>About the Creator Team</div><div class='hero-sub'>Cyber Rakshak is a collaborative prototype focused on explainable cyber investigation and evidence intelligence.</div></div>",unsafe_allow_html=True)
    members=[('Harsh Sharma','Technical','Application architecture, Streamlit engineering, analysis pipeline and system integration.'),('Avinash Kumar','Research','Research, evidence methodology and investigation workflow.'),('Devansh Gocher','Research','Research, data interpretation and investigation methodology.'),('Manish Meena','Innovation','Product ideas, usability and feature innovation.'),('Krish Pareek','Innovation','Workflow innovation and prototype experience.'),('Mahak Gurumukhani','Innovation','User experience, innovation and presentation.')]
    st.markdown('<div class="card-grid">'+''.join(f'<div class="feature-card"><div class="feature-icon">👤</div><b>{n}</b><span><span class="pill">{r}</span><br>{d}</span></div>' for n,r,d in members)+'</div>',unsafe_allow_html=True)
    st.markdown("<div class='panel'><div class='panel-title'>Our principle</div><div class='tip'>Evidence first. Explain every signal. Preserve provenance. Keep a human decision-maker in the loop.</div></div>",unsafe_allow_html=True)

# ---------------- CONTACT ----------------
elif selected=='Contact':
    st.markdown("<div class='hero'><div class='kicker'>TEAM VOXSHIELD · CONTACT</div><div class='hero-title'>Contact & Support</div><div class='hero-sub'>General project contact information for prototype/demo communication.</div></div>",unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        st.markdown("<div class='panel'><div class='panel-title'>Project contact</div><div class='evidence-card'><b>Team</b><br>Voxshield</div><div class='evidence-card'><b>General phone</b><br>+91-XXXX-XXXXXX</div><div class='evidence-card'><b>General email</b><br>team.voxshield@XXXX.com</div><div class='evidence-card'><b>Availability</b><br>Prototype / academic communication</div></div>",unsafe_allow_html=True)
    with b:
        st.markdown("<div class='panel'><div class='panel-title'>Send a note</div>",unsafe_allow_html=True)
        st.text_input('Your name')
        st.text_input('Topic')
        st.text_area('Message',height=140)
        st.button('Send message (demo)',use_container_width=True)
        st.caption('This prototype button does not transmit messages to an external mail server.')
        st.markdown('</div>',unsafe_allow_html=True)

# ---------------- SAFETY ----------------
elif selected=='Safety & Response':
    st.markdown("<div class='hero'><div class='kicker'>CYBER SAFETY & OFFICIAL RESPONSE</div><div class='hero-title'>If the incident is real</div><div class='hero-sub'>Cyber Rakshak is an analysis aid. Official reporting channels should be used for actual cybercrime complaints.</div></div>",unsafe_allow_html=True)
    st.markdown("<div class='danger-note'><b>🚨 India cyber financial fraud:</b> report immediately through the National Cyber Crime Reporting Portal or call the official 24×7 cybercrime helpline <b>1930</b>. Do not wait for an AI assessment.</div>",unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        st.link_button('🇮🇳 National Cyber Crime Reporting Portal ↗','https://www.cybercrime.gov.in/',use_container_width=True)
        st.link_button('🔎 Official Report Suspect page ↗','https://www.cybercrime.gov.in/Webform/cyber_suspect.aspx',use_container_width=True)
    with b:
        st.markdown("<div class='panel'><div class='panel-title'>Preserve evidence</div>"+''.join(f"<div class='evidence-card'>✓ {x}</div>" for x in ['Keep original messages/files without editing them.','Record incident date and time.','Keep transaction / UTR information where relevant.','Preserve suspicious URLs, handles and email identifiers.','Record the source of each evidence item.','Do not confront or threaten a person based only on an AI result.'])+"</div>",unsafe_allow_html=True)

st.markdown("<div class='footer'>CYBER RAKSHAK · TEAM VOXSHIELD · PART 1 · INVESTIGATIVE SUPPORT ONLY · HUMAN VERIFICATION REQUIRED · ACCOUNT DATA STORED IN SERVER-SIDE DATABASE</div>",unsafe_allow_html=True)
