import re
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Tuple

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

st.set_page_config(
    page_title="Cyber Rakshak | Investigation Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------ DESIGN SYSTEM ------------------------------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');
:root{
 --bg:#070a0f; --surface:#0d121a; --surface2:#111925; --surface3:#151e2b;
 --line:#202b3a; --line2:#2b394c; --text:#eef4fb; --muted:#8c9aae;
 --cyan:#39d5f6; --blue:#65a9ff; --green:#48d7a0; --amber:#f4c95d; --red:#ff7187;
}
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:radial-gradient(circle at 75% 0%,#0e1a2a 0%,var(--bg) 38%);color:var(--text)}
.block-container{max-width:1420px;padding:28px 34px 70px}
section[data-testid="stSidebar"]{background:#080c12;border-right:1px solid var(--line)}
section[data-testid="stSidebar"]>div{padding:22px 16px}
section[data-testid="stSidebar"] .stRadio label{color:#aeb9c8!important}
section[data-testid="stSidebar"] .stRadio label:hover{color:#fff!important}
section[data-testid="stSidebar"] hr{border-color:var(--line)}
header[data-testid="stHeader"]{background:transparent}

.brand{display:flex;align-items:center;gap:12px;margin-bottom:3px}
.shield{width:36px;height:36px;border:1px solid #28506a;border-radius:10px;display:flex;align-items:center;justify-content:center;background:#0c1a26;font-size:18px}
.brand-name{font-weight:800;letter-spacing:.5px;font-size:18px}
.brand-sub{font:500 10px 'JetBrains Mono';letter-spacing:1.2px;color:#607086;margin:4px 0 20px 48px}

.hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#101b2a 0%,#0b111a 70%);border:1px solid #263a52;border-radius:18px;padding:28px 30px;margin-bottom:18px;box-shadow:0 16px 50px rgba(0,0,0,.22)}
.hero:after{content:"";position:absolute;width:240px;height:240px;border-radius:50%;right:-110px;top:-120px;background:rgba(57,213,246,.08);filter:blur(4px)}
.kicker{font:700 10px 'JetBrains Mono';letter-spacing:1.5px;color:var(--cyan);text-transform:uppercase}
.hero-title{font-size:34px;line-height:1.05;font-weight:800;margin-top:7px}
.hero-sub{color:#9ba9bb;font-size:13px;margin-top:9px}
.hero-meta{font:600 11px 'JetBrains Mono';color:#9db0c6}

.metric-card{background:rgba(13,18,26,.9);border:1px solid var(--line);border-radius:13px;padding:17px 18px;min-height:100px}
.metric-label{font-size:11px;color:#7e8da1;text-transform:uppercase;letter-spacing:.7px}
.metric-value{font:700 26px 'JetBrains Mono';margin-top:9px;color:#edf4fc}
.metric-note{font-size:11px;color:#68778b;margin-top:4px}

.panel{background:rgba(13,18,26,.92);border:1px solid var(--line);border-radius:15px;padding:21px;margin-bottom:16px}
.panel-head{display:flex;justify-content:space-between;gap:15px;align-items:flex-start;margin-bottom:15px}
.panel-title{font-size:17px;font-weight:750}
.panel-sub{font-size:12px;color:var(--muted);margin-top:4px;line-height:1.5}
.section-number{font:700 11px 'JetBrains Mono';color:#5f728b}

.badge{display:inline-flex;align-items:center;padding:5px 9px;border-radius:999px;font:700 10px 'JetBrains Mono';letter-spacing:.5px;border:1px solid}
.badge-low{color:#70e6ba;background:#09251d;border-color:#165b46}.badge-med{color:#f8d46e;background:#2a2108;border-color:#6e560e}.badge-high{color:#ff9bac;background:#2a0d15;border-color:#7d2435}.badge-info{color:#78dfff;background:#092330;border-color:#18566d}

.step-row{display:flex;gap:0;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#0b1119;margin-bottom:17px}
.step{flex:1;padding:13px 12px;border-right:1px solid var(--line);position:relative}.step:last-child{border-right:0}
.step-no{font:700 10px 'JetBrains Mono';color:#63748a}.step-name{font-size:11px;font-weight:700;margin-top:5px}.step-state{font-size:10px;color:#63748a;margin-top:3px}.step.active{background:#0e1b28}.step.active .step-no,.step.active .step-state{color:var(--cyan)}

.evidence-card{background:#0b1119;border:1px solid var(--line);border-radius:12px;padding:15px;margin-bottom:10px}
.ev-top{display:flex;align-items:center;justify-content:space-between;gap:12px}.ev-id{font:700 11px 'JetBrains Mono';color:#708197}.ev-type{font-size:13px;font-weight:700;margin-top:4px}.ev-source{font-size:11px;color:#718096;margin-top:3px}
.finding{background:#0c1621;border:1px solid #1c3449;border-left:3px solid var(--cyan);padding:12px 14px;border-radius:8px;margin:8px 0;line-height:1.5;font-size:12px}
.finding.warn{border-left-color:var(--amber)}.finding.danger{border-left-color:var(--red)}.finding.ok{border-left-color:var(--green)}

.score-ring{border:1px solid var(--line2);border-radius:14px;background:#0b1119;padding:18px;text-align:center}.score{font:800 38px 'JetBrains Mono'}.score-label{font-size:10px;letter-spacing:1px;color:#718096;margin-top:2px}
.progress{height:7px;background:#17202c;border-radius:99px;overflow:hidden;margin:10px 0 5px}.progress>div{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--cyan),var(--blue))}

.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div,.stNumberInput input{background:#0b1119!important;color:#edf4fb!important;border:1px solid #263447!important;border-radius:9px!important}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#59697d!important}
.stFileUploader{background:#0b1119;border:1px dashed #304057;border-radius:10px;padding:6px}
.stButton>button,.stDownloadButton>button{border-radius:9px!important;border:1px solid #2a3a4f!important;background:#111b28!important;color:#eaf2fb!important;font-weight:700!important;min-height:40px}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#3b607b!important;background:#142334!important}
button[kind="primary"]{background:#0c3d52!important;border-color:#1a718f!important}
.stTabs [data-baseweb="tab-list"]{gap:5px;border-bottom:1px solid var(--line)}
.stTabs [data-baseweb="tab"]{padding:12px 15px;color:#7e8da1}
.stTabs [aria-selected="true"]{color:#5de0fb!important}
.stDataFrame{border:1px solid var(--line);border-radius:10px;overflow:hidden}
.stAlert{border-radius:10px!important}
[data-testid="stMetricValue"]{color:#edf4fb!important}
[data-testid="stMetricLabel"]{color:#7f8da0!important}

.quick-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0}.quick-card{background:#0b1119;border:1px solid var(--line);border-radius:12px;padding:14px}.quick-card b{font-size:12px}.quick-card span{display:block;font-size:11px;color:#738298;margin-top:5px;line-height:1.45}.console{background:linear-gradient(135deg,#08141d,#0b121a);border:1px solid #193b4c;border-radius:13px;padding:15px 17px;margin:12px 0}.console-label{font:700 9px 'JetBrains Mono';letter-spacing:1.4px;color:#4bdcf8}.console-text{font-size:13px;color:#d9edf5;margin-top:7px;line-height:1.55}.tip{border-left:3px solid var(--green);background:#0b1715;padding:12px 14px;border-radius:8px;font-size:12px;line-height:1.55}.danger-note{border-left:3px solid var(--red);background:#190c11;padding:12px 14px;border-radius:8px;font-size:12px;line-height:1.55}.mini-stat{font:700 12px 'JetBrains Mono';color:#cfe0f0}.stLinkButton a{border-radius:9px!important;border:1px solid #2a3a4f!important;background:#111b28!important;color:#eaf2fb!important;font-weight:700!important}.stLinkButton a:hover{border-color:#3b607b!important;background:#142334!important}.footer{color:#56657a;font:500 10px 'JetBrains Mono';letter-spacing:.5px;text-align:center;margin-top:28px;padding-top:18px;border-top:1px solid var(--line)}
.empty{border:1px dashed #2c3a4d;border-radius:14px;padding:34px;text-align:center;color:#718096;background:#0a1017}
</style>
""", unsafe_allow_html=True)

# ------------------------------ STATE --------------------------------------
def now_str(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def init_state():
    if "case" not in st.session_state:
        st.session_state.case={"id":f"INV-{datetime.now().year}-001","title":"","subject":"","aliases":"","description":"","priority":"Medium","created":now_str()}
    if "evidence" not in st.session_state: st.session_state.evidence=[]
    if "nav" not in st.session_state: st.session_state.nav="Investigation"
    if "analysis_run" not in st.session_state: st.session_state.analysis_run=0
    if "console_index" not in st.session_state: st.session_state.console_index=0
    if "notes" not in st.session_state: st.session_state.notes=""
    if "show_help" not in st.session_state: st.session_state.show_help=False

def reset_case():
    st.session_state.case={"id":f"INV-{datetime.now().year}-{np.random.randint(100,999)}","title":"","subject":"","aliases":"","description":"","priority":"Medium","created":now_str()}
    st.session_state.evidence=[]
    st.session_state.notes=""
    st.session_state.analysis_run+=1
    st.session_state.notes=""
    print(f"[CYBER RAKSHAK] new investigation created: {st.session_state.case['id']}")

init_state()

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

# ------------------------------ SIDEBAR ------------------------------------
with st.sidebar:
    st.markdown("<div class='brand'><div class='shield'>🛡️</div><div class='brand-name'>CYBER RAKSHAK</div></div><div class='brand-sub'>INVESTIGATION INTELLIGENCE · PART 1</div>",unsafe_allow_html=True)
    st.markdown("<div style='font-size:10px;color:#5e6d80;letter-spacing:1px;font-weight:700;margin-bottom:8px'>WORKSPACE</div>",unsafe_allow_html=True)
    pages=["Investigation","Evidence Intake","AI Analysis","Risk Assessment","Report","Safety & Response"]
    selected=st.radio("",pages,index=pages.index(st.session_state.nav),label_visibility="collapsed")
    st.session_state.nav=selected
    st.divider()
    c=st.session_state.case
    st.markdown("<div style='font-size:10px;color:#5e6d80;letter-spacing:1px;font-weight:700'>CURRENT INVESTIGATION</div>",unsafe_allow_html=True)
    st.markdown(f"<div style='font:700 12px JetBrains Mono;color:#d8e3ef;margin-top:10px'>{c['id']}</div><div style='font-size:12px;color:#78879b;margin-top:8px'>{c['subject'] or 'No subject entered'}</div>",unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:12px;color:#78879b;margin-top:7px'>Evidence <b style='color:#d9e3ee'>{len(st.session_state.evidence)}</b></div>",unsafe_allow_html=True)
    st.divider()
    if st.button("＋  New Investigation",use_container_width=True): reset_case(); st.session_state.nav="Investigation"; st.rerun()
    if st.button("⚡ Quick Evidence Intake",use_container_width=True): st.session_state.nav="Evidence Intake"; st.rerun()
    if st.button("🛡️ Cyber Safety & Reporting",use_container_width=True): st.session_state.nav="Safety & Response"; st.rerun()
    st.markdown("<div style='height:12vh'></div>",unsafe_allow_html=True)
    st.markdown("<div class='console'><div class='console-label'>ANALYST CONSOLE</div><div class='console-text'>Good investigation follows evidence, not assumptions. Keep sources, timestamps and context attached to every finding.</div></div>",unsafe_allow_html=True)
    st.markdown("<div class='mono' style='font-size:9px;color:#526176;line-height:1.8'>LOCAL ANALYSIS ENGINE · READY<br>HUMAN VERIFICATION · REQUIRED<br>NO AUTOMATIC CRIMINAL VERDICT</div>",unsafe_allow_html=True)

# ------------------------------ HEADER -------------------------------------
F=fusion(st.session_state.evidence); C=st.session_state.case
priority_level="high" if C["priority"] in ["High","Critical"] else "moderate" if C["priority"]=="Medium" else "low"
st.markdown(f"""
<div class='hero'>
 <div style='display:flex;justify-content:space-between;gap:20px;align-items:flex-start'>
  <div><div class='kicker'>CYBER RAKSHAK · PART 1 · EVIDENCE INTELLIGENCE</div><div class='hero-title'>Investigation Workspace</div><div class='hero-sub'>Multi-source evidence analysis · explainable investigative signal · human verification</div></div>
  <div style='text-align:right'><div class='hero-meta'>{C['id']}</div><div style='margin-top:9px'>{badge(C['priority'].upper()+" PRIORITY",priority_level)}</div></div>
 </div>
</div>
""",unsafe_allow_html=True)

m=st.columns(4)
for col,label,val,note in [(m[0],"Evidence units",len(st.session_state.evidence),"items analyzed"),(m[1],"Evidence types",F["coverage"],"independent modalities"),(m[2],"Corroborated entities",len(F["corroborated"]),"repeat across sources"),(m[3],"Investigative signal",f"{F['score']}/100",F["risk"].lower())]:
    col.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{val}</div><div class='metric-note'>{note}</div></div>",unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
readiness=min(100,int(F["coverage"]*20 + min(len(st.session_state.evidence),5)*10 + min(len(F["corroborated"]),5)*6))
st.markdown(f"<div class='panel' style='padding:14px 17px'><div class='panel-head' style='margin-bottom:8px'><div><div class='section-number'>INVESTIGATION READINESS</div><div class='panel-title'>Evidence readiness · {readiness}%</div></div><div class='mini-stat'>{len(st.session_state.evidence)} evidence · {F['coverage']} modalities · {len(F['corroborated'])} corroborated</div></div><div class='progress'><div style='width:{readiness}%'></div></div><div class='panel-sub'>Readiness measures evidence coverage and corroboration; it does not measure whether a person is criminal.</div></div>",unsafe_allow_html=True)
st.info("Responsible AI: this prototype identifies evidence-based investigative indicators. It must not be used to label a real person as criminal based on demographic, appearance, accent, emotion or other protected/behavioral traits. Evidence provenance and human verification are required.")

# Helpful analyst console
console_messages=[
    "🔎 Strong investigators do not rush to a conclusion — they strengthen the evidence chain.",
    "🧭 Compare independent sources before escalating an investigation.",
    "📝 Preserve the original evidence, source and timestamp so every finding remains traceable.",
    "🛡️ If you are dealing with an actual cybercrime or financial fraud in India, use the official reporting channels rather than relying on an AI assessment.",
]
st.markdown(f"<div class='console'><div class='console-label'>LIVE ANALYST CONSOLE · {now_str()}</div><div class='console-text'>{console_messages[st.session_state.console_index % len(console_messages)]}</div></div>",unsafe_allow_html=True)

c1,c2,c3=st.columns(3)
with c1:
    if st.button("🔄 Refresh intelligence",use_container_width=True): st.session_state.analysis_run+=1; st.session_state.console_index+=1; st.toast("Intelligence view refreshed")
with c2:
    if st.button("📋 Evidence checklist",use_container_width=True): st.session_state.show_help=not st.session_state.show_help
with c3:
    st.link_button("🇮🇳 Official cybercrime portal", "https://www.cybercrime.gov.in/", use_container_width=True)
if st.session_state.show_help:
    st.markdown("<div class='tip'><b>Evidence checklist:</b> preserve the original message/file, note the incident time, keep relevant URLs or identifiers, retain transaction/UTR details when applicable, record the source, and avoid editing the original evidence. Use only evidence you are authorized to analyze.</div>",unsafe_allow_html=True)

# ------------------------------ PAGE: INVESTIGATION ------------------------
if selected=="Investigation":
    st.markdown("<div class='panel'><div class='panel-head'><div><div class='section-number'>01 · CASE SETUP</div><div class='panel-title'>Define the investigation question</div><div class='panel-sub'>Create a case and describe what you are trying to establish from the evidence you actually possess.</div></div></div>",unsafe_allow_html=True)
    st.markdown("<div class='quick-grid'><div class='quick-card'><b>1 · Define</b><span>State what you want the evidence to establish.</span></div><div class='quick-card'><b>2 · Feed</b><span>Add only the evidence you actually possess and are authorized to use.</span></div><div class='quick-card'><b>3 · Correlate</b><span>Let the engine compare independent evidence before escalation.</span></div></div>",unsafe_allow_html=True)
    q1,q2=st.columns(2)
    with q1:
        if st.button("🧪 Load safe demo evidence",use_container_width=True):
            demo_text="Your account will be suspended today. Verify your account immediately using the secure login link and send the OTP to complete verification."
            add_ev("TEXT / MESSAGE","Synthetic demo",demo_text,analyze_text(demo_text))
            demo_url="http://secure-account.example/login/verify-otp"
            add_ev("URL / LINK","Synthetic demo",demo_url,analyze_url(demo_url))
            st.toast("Safe synthetic evidence loaded")
            st.rerun()
    with q2:
        if st.button("🧹 Clear all evidence",use_container_width=True):
            st.session_state.evidence=[]; st.session_state.analysis_run+=1; st.toast("Evidence ledger cleared"); st.rerun()
    a,b=st.columns([1.25,.75],gap="large")
    with a:
        with st.form("case_form"):
            title=st.text_input("Investigation title",C["title"],placeholder="e.g. Suspicious payment investigation")
            subject=st.text_input("Subject / entity identifier",C["subject"],placeholder="Person, organization, account, domain or case identifier")
            aliases=st.text_input("Known aliases / identifiers",C["aliases"],placeholder="Optional")
            description=st.text_area("Investigation question",C["description"],height=105,placeholder="Example: Determine whether the supplied evidence contains coordinated fraud indicators.")
            priority=st.selectbox("Priority",["Low","Medium","High","Critical"],index=["Low","Medium","High","Critical"].index(C["priority"]))
            st.session_state.notes=st.text_area("Analyst notes",st.session_state.notes,height=85,placeholder="Optional: what should the investigator pay attention to?")
            if st.form_submit_button("Save investigation",type="primary",use_container_width=True):
                C.update({"title":title or "Untitled Investigation","subject":subject,"aliases":aliases,"description":description,"priority":priority}); st.success("Investigation saved."); st.rerun()
    with b:
        st.markdown("<div class='section-number'>ANALYSIS PIPELINE</div><div class='panel-title' style='margin-top:5px'>How the engine works</div>",unsafe_allow_html=True)
        for no,name,desc in [("01","INGEST","Accept only supplied evidence."),("02","ANALYZE","Run modality-specific models."),("03","EXTRACT","Identify technical entities."),("04","CORRELATE","Find independent convergence."),("05","ASSESS","Produce explainable signal."),("06","REVIEW","Human decision gate.")]:
            st.markdown(f"<div class='evidence-card' style='padding:11px 13px'><span class='section-number'>{no}</span> <b style='font-size:12px'>{name}</b><div class='panel-sub'>{desc}</div></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

# ------------------------------ PAGE: EVIDENCE -----------------------------
elif selected=="Evidence Intake":
    st.markdown("<div class='panel'><div class='panel-head'><div><div class='section-number'>02 · EVIDENCE INTAKE</div><div class='panel-title'>Feed the investigation</div><div class='panel-sub'>Each item is analyzed immediately and remains traceable to its source, findings and final assessment.</div></div></div>",unsafe_allow_html=True)
    tabs=st.tabs(["💬  Text","🔗  URL","🎙  Audio transcript","📊  Transactions","📄  Public source"])
    with tabs[0]:
        with st.form("text_form"):
            text=st.text_area("Message / email / chat content",height=170,placeholder="Paste evidence text here…")
            source=st.text_input("Source / provenance",value="User supplied",key="text_source")
            if st.form_submit_button("Analyze text →",type="primary"):
                if text.strip(): add_ev("TEXT / MESSAGE",source,text,analyze_text(text)); st.success("Text analyzed and added to the evidence ledger."); st.rerun()
                else: st.warning("Enter text first.")
    with tabs[1]:
        with st.form("url_form"):
            url=st.text_input("URL / domain",placeholder="https://example.com/login")
            source=st.text_input("Source / provenance",value="User supplied",key="url_source")
            if st.form_submit_button("Inspect URL →",type="primary"):
                if url.strip(): add_ev("URL / LINK",source,url,analyze_url(url)); st.success("URL analyzed and added."); st.rerun()
                else: st.warning("Enter a URL first.")
    with tabs[2]:
        st.caption("For audio, supply a transcript from an authorized speech-to-text workflow. The engine analyzes content, not voice identity or accent.")
        with st.form("audio_form"):
            transcript=st.text_area("Verified / generated transcript",height=170,placeholder="Paste transcript here…")
            source=st.text_input("Source / provenance",value="User supplied",key="audio_source")
            if st.form_submit_button("Analyze transcript →",type="primary"):
                if transcript.strip(): add_ev("AUDIO / TRANSCRIPT",source,transcript,analyze_audio(transcript)); st.success("Transcript analyzed and added."); st.rerun()
                else: st.warning("Enter transcript first.")
    with tabs[3]:
        st.caption("CSV columns: Sender, Receiver, Amount, Timestamp. Statistical anomalies are treated as investigative signals, not proof of wrongdoing.")
        template=pd.DataFrame([{"Sender":"ACC-1001","Receiver":"ACC-2001","Amount":2500,"Timestamp":"2026-09-06 10:00:00"},{"Sender":"ACC-1001","Receiver":"ACC-2002","Amount":2500,"Timestamp":"2026-09-06 10:05:00"}])
        st.download_button("⬇ Download CSV template",template.to_csv(index=False),file_name="cyber_rakshak_transaction_template.csv",mime="text/csv")
        uploaded=st.file_uploader("Upload transaction CSV",type=["csv"],key="tx_upload")
        if uploaded:
            try:
                df=pd.read_csv(uploaded); st.dataframe(df.head(8),use_container_width=True,hide_index=True)
                source=st.text_input("Source / provenance",value="User supplied",key="tx_source")
                if st.button("Analyze transaction batch →",type="primary"):
                    add_ev("TRANSACTION DATA",source,df,analyze_transactions(df)); st.success("Transaction batch analyzed and added."); st.rerun()
            except Exception as e: st.error(f"Could not read CSV: {e}")
    with tabs[4]:
        with st.form("public_form"):
            doc=st.text_area("Public-source excerpt / document text",height=170,placeholder="Paste relevant, lawfully obtained public-source content…")
            source=st.text_input("Source / URL / registry",value="User supplied",key="public_source")
            if st.form_submit_button("Analyze source →",type="primary"):
                if doc.strip(): add_ev("PUBLIC SOURCE",source,doc,analyze_public(doc)); st.success("Public-source evidence analyzed and added."); st.rerun()
                else: st.warning("Enter source content first.")
    st.markdown("</div>",unsafe_allow_html=True)

    if st.session_state.evidence:
        st.markdown("<div class='panel'><div class='panel-head'><div><div class='section-number'>EVIDENCE LEDGER</div><div class='panel-title'>Traceable evidence</div><div class='panel-sub'>Every assessment can be traced back to an evidence item.</div></div></div>",unsafe_allow_html=True)
        search=st.text_input("Search evidence",placeholder="Search type, source, entity or keyword…",key="evidence_search")
        filtered=[]
        q=(search or "").lower().strip()
        for ev in st.session_state.evidence:
            hay=(ev["id"]+" "+ev["type"]+" "+ev["source"]+" "+str(ev.get("raw",""))).lower()
            if not q or q in hay: filtered.append(ev)
        st.caption(f"Showing {len(filtered)} of {len(st.session_state.evidence)} evidence items")
        for ev in filtered:
            a=ev["analysis"]; c1,c2,c3,c4=st.columns([1.1,2.2,1,.75])
            with c1: st.markdown(f"<div class='ev-id'>{ev['id']}</div><div class='ev-type'>{ev['type']}</div>",unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='ev-source'>{ev['source']} · {ev['timestamp']}</div><div style='margin-top:7px'>{badge(a.get('strength','Weak'),lvl(a.get('score',0)))}</div>",unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='metric-label'>SIGNAL</div><div style='font:700 18px JetBrains Mono;margin-top:5px'>{a.get('score',0)}/100</div>",unsafe_allow_html=True)
            with c4:
                if st.button("Inspect",key=f"inspect_{ev['id']}"): st.session_state[f"inspect_{ev['id']}"]=not st.session_state.get(f"inspect_{ev['id']}",False)
                if st.button("Remove",key=f"remove_{ev['id']}"):
                    st.session_state.evidence=[x for x in st.session_state.evidence if x["id"]!=ev["id"]]
                    st.session_state.analysis_run+=1
                    st.toast(f"{ev['id']} removed")
                    st.rerun()
            if st.session_state.get(f"inspect_{ev['id']}",False):
                st.markdown(f"<div class='finding'>{a.get('explanation','')}</div>",unsafe_allow_html=True)
                for item in a.get("indicators",[]): st.markdown(f"<div class='finding warn'>• {item}</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='empty'>No evidence has been added yet.<br><span style='font-size:12px'>Choose a source above and feed the system the evidence you actually have.</span></div>",unsafe_allow_html=True)

# ------------------------------ PAGE: AI ----------------------------------
elif selected=="AI Analysis":
    st.markdown("<div class='panel'><div class='panel-head'><div><div class='section-number'>03 · AI ANALYSIS CENTER</div><div class='panel-title'>Evidence intelligence pipeline</div><div class='panel-sub'>Inspect exactly what the engine extracted, detected and correlated.</div></div></div>",unsafe_allow_html=True)
    active=bool(st.session_state.evidence)
    if st.button("▶ Run full intelligence pass",type="primary",use_container_width=True,disabled=not active):
        st.session_state.analysis_run+=1
        print(f"[CYBER RAKSHAK] full intelligence pass run={st.session_state.analysis_run} evidence={len(st.session_state.evidence)}")
        st.toast("Full evidence correlation refreshed")
        st.rerun()
    stages=["INGESTION","MODALITY AI","ENTITY EXTRACTION","PATTERN ANALYSIS","CORRELATION","ASSESSMENT"]
    st.markdown("<div class='step-row'>"+"".join([f"<div class='step {'active' if active else ''}'><div class='step-no'>{i+1:02d}</div><div class='step-name'>{s}</div><div class='step-state'>{'COMPLETE' if active else 'WAITING'}</div></div>" for i,s in enumerate(stages)])+"</div>",unsafe_allow_html=True)
    if not active:
        st.markdown("<div class='empty'>Analysis is waiting for evidence.<br><span style='font-size:12px'>Go to Evidence Intake and add at least one item.</span></div>",unsafe_allow_html=True)
    else:
        left,right=st.columns([1.25,.75],gap="large")
        with left:
            for ev in st.session_state.evidence:
                a=ev["analysis"]
                with st.expander(f"{ev['id']}  ·  {ev['type']}  ·  {a.get('score',0)}/100",expanded=False):
                    st.markdown("**Model explanation**  \n" + a.get("explanation", ""))
                    st.markdown("**Detected indicators**")
                    for x in a.get("indicators",[]): st.markdown(f"- {x}")
                    if a.get("entities"): st.dataframe(pd.DataFrame(a["entities"]),use_container_width=True,hide_index=True)
        with right:
            st.markdown("<div class='panel-title'>Cross-source intelligence</div><div class='panel-sub'>Independent evidence becomes more useful when the same technical entity or pattern recurs.</div>",unsafe_allow_html=True)
            if F["correlations"]:
                for c in F["correlations"]: st.markdown(f"<div class='finding'><b>{c['title']}</b><br>{c['finding']}<br><span class='muted'>Strength: {c['strength']}</span></div>",unsafe_allow_html=True)
            else: st.info("No corroboration yet. Add independent evidence containing shared technical identifiers.")
            st.markdown("<div class='panel-title' style='margin-top:20px'>Entity pool</div>",unsafe_allow_html=True)
            if F["entities"]:
                st.dataframe(pd.DataFrame([{"Type":t,"Value":v} for t,v in F["entities"]]),use_container_width=True,hide_index=True)
            else: st.caption("No technical entities extracted yet.")
        
    st.markdown("</div>",unsafe_allow_html=True)

# ------------------------------ PAGE: RISK ---------------------------------
elif selected=="Risk Assessment":
    st.markdown("<div class='panel'><div class='panel-head'><div><div class='section-number'>04 · EXPLAINABLE ASSESSMENT</div><div class='panel-title'>What does the evidence currently support?</div><div class='panel-sub'>The score represents investigative signal strength, not probability that a person is a criminal.</div></div></div>",unsafe_allow_html=True)
    l,r=st.columns([1.2,.8],gap="large")
    with l:
        color_class=lvl(F["score"])
        st.markdown(f"<div class='score-ring'><div class='score'>{F['score']}<span style='font-size:18px;color:#718096'>/100</span></div><div class='score-label'>COMPOSITE INVESTIGATIVE SIGNAL</div><div style='margin-top:13px'>{badge(F['risk'],color_class)}</div><div class='progress'><div style='width:{F['score']}%'></div></div><div style='font-size:11px;color:#77869a'>Built from modality signals, source reliability, cross-source coverage and corroborated technical entities.</div></div>",unsafe_allow_html=True)
    with r:
        action_text={"NETWORK_REVIEW":"Further human review + network analysis","HUMAN_REVIEW":"Human review recommended","CONTINUE_REVIEW":"Continue evidence collection","ADD_EVIDENCE":"Add evidence"}[F["action"]]
        st.markdown(f"<div class='finding {'danger' if color_class=='high' else 'warn' if color_class=='moderate' else 'ok'}'><b>Recommended next step</b><br>{action_text}</div>",unsafe_allow_html=True)
        st.markdown("<div class='panel-title' style='margin-top:16px'>Why?</div>",unsafe_allow_html=True)
        reasons=[]
        if F["coverage"]>1: reasons.append(f"{F['coverage']} independent evidence modalities are present.")
        if F["corroborated"]: reasons.append(f"{len(F['corroborated'])} technical identifier(s) recur across evidence types.")
        if any(x["adjusted"]>=45 for x in F["breakdown"]): reasons.append("At least one evidence item has a high adjusted signal after source reliability weighting.")
        if not reasons: reasons.append("Current evidence does not yet show strong independent convergence.")
        for x in reasons: st.markdown(f"<div class='finding'>✓ {x}</div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if F["breakdown"]:
        st.markdown("<div class='panel'><div class='panel-title'>Signal decomposition</div><div class='panel-sub'>See how each evidence item contributes to the composite.</div>",unsafe_allow_html=True)
        rows=[]
        for i,x in enumerate(F["breakdown"],1): rows.append({"Evidence":f"EVD-{i:03d}","Type":x["type"],"Raw signal":x["raw"],"Source reliability":f"{x['reliability']:.0%}","Adjusted signal":x["adjusted"]})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div class='panel'><div class='panel-title'>Uncertainty & safeguards</div>",unsafe_allow_html=True)
    for x in ["An indicator is not proof of criminal conduct.","Entity ownership and attribution require independent verification.","Public-source information may be incomplete or misattributed.","The local prototype does not automatically query private records or live threat-intelligence feeds."]:
        st.markdown(f"<div class='evidence-card' style='padding:11px 13px'>• {x}</div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if F["action"]=="NETWORK_REVIEW":
        st.success("The prototype gate is satisfied for deeper human review. Extracted entities are ready for the future Part 2 network module.")
        if st.button("→ Prepare Part 2: Network Analysis",type="primary",use_container_width=True): st.session_state.network_ready=True; st.toast("Network hand-off prepared")

# ------------------------------ PAGE: SAFETY & RESPONSE -------------------
elif selected=="Safety & Response":
    st.markdown("<div class='panel'><div class='panel-head'><div><div class='section-number'>06 · CYBER SAFETY & RESPONSE</div><div class='panel-title'>When an incident may be real</div><div class='panel-sub'>This workspace is for analysis and triage. Official reporting channels should be used for actual cybercrime complaints.</div></div></div>",unsafe_allow_html=True)
    a,b=st.columns([1.15,.85],gap="large")
    with a:
        st.markdown("<div class='danger-note'><b>🚨 If you are experiencing cyber financial fraud in India:</b><br>Report it immediately through the National Cyber Crime Reporting Portal or call the 24×7 cybercrime helpline <b>1930</b>. Do not wait for this tool to finish an analysis.</div>",unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
        st.link_button("Open National Cyber Crime Reporting Portal ↗", "https://www.cybercrime.gov.in/", use_container_width=True)
        st.markdown("<div class='panel-title' style='margin-top:22px'>Useful official actions</div>",unsafe_allow_html=True)
        st.markdown("<div class='evidence-card'><b>Report a suspect identifier</b><div class='panel-sub'>The official portal provides a facility for reporting suspicious website URLs, phone numbers, email IDs, social-media URLs and other identifiers.</div></div>",unsafe_allow_html=True)
        st.link_button("Open official Report Suspect page ↗", "https://www.cybercrime.gov.in/Webform/cyber_suspect.aspx", use_container_width=True)
        st.markdown("<div class='evidence-card'><b>Check available suspect identifiers</b><div class='panel-sub'>The National Cyber Crime Reporting Portal also provides suspect-search facilities for certain identifiers.</div></div>",unsafe_allow_html=True)
        st.link_button("Open official portal ↗", "https://www.cybercrime.gov.in/", use_container_width=True)
    with b:
        st.markdown("<div class='panel-title'>Preserve evidence before acting</div>",unsafe_allow_html=True)
        for item in ["Keep original messages/files without editing them.","Record the date and time of the incident.","Keep relevant transaction/UTR information for financial fraud.","Preserve suspicious URLs, handles, email IDs and other identifiers.","Record where each item came from and who provided it.","Do not confront or threaten a suspected person based only on an AI result."]:
            st.markdown(f"<div class='evidence-card' style='padding:11px 13px'>✓ {item}</div>",unsafe_allow_html=True)
        st.markdown("<div class='tip'><b>Remember:</b> Cyber Rakshak is an investigative-support prototype. An AI signal is not a criminal verdict and should not replace police, legal or official cybercrime reporting processes.</div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

# ------------------------------ PAGE: REPORT -------------------------------
elif selected=="Report":
    st.markdown("<div class='panel'><div class='panel-head'><div><div class='section-number'>05 · INVESTIGATION REPORT</div><div class='panel-title'>Evidence-led intelligence brief</div><div class='panel-sub'>A concise, traceable summary generated from the current case state.</div></div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='finding'><b>{C['id']}</b> · {C['title'] or 'Untitled Investigation'}<br>Subject: {C['subject'] or 'Not specified'}<br>Assessment: {F['risk']} · {F['score']}/100</div>",unsafe_allow_html=True)
    lines=["CYBER RAKSHAK — INVESTIGATION INTELLIGENCE BRIEF","="*70,f"Case: {C['id']}",f"Title: {C['title'] or 'Untitled Investigation'}",f"Subject/entity: {C['subject'] or 'Not specified'}",f"Generated: {now_str()}","",f"ASSESSMENT: {F['risk']}",f"COMPOSITE SIGNAL: {F['score']}/100",f"EVIDENCE TYPES: {F['coverage']}","","This report is an investigative triage output, not a criminal verdict. Human verification is required.","","EVIDENCE","-"*70]
    for e in st.session_state.evidence:
        a=e["analysis"]; lines.append(f"[{e['id']}] {e['type']} | source={e['source']} | signal={a.get('score',0)}/100")
        for ind in a.get("indicators",[]): lines.append(f"  - {ind}")
    lines += ["","CROSS-SOURCE FINDINGS","-"*70]
    for c in F["correlations"]: lines.append(f"- {c['title']}: {c['finding']} ({c['strength']})")
    lines += ["","ANALYST NOTES","-"*70,st.session_state.notes or "No analyst notes recorded.","","LIMITATIONS","-"*70,"- Source provenance must be validated.","- Entity attribution requires verification.","- Automated output must not be treated as a criminal determination."]
    report="\n".join(lines)
    with st.expander("Preview generated investigation brief",expanded=True):
        st.text_area("Report preview",report,height=360,label_visibility="collapsed")
    st.download_button("⬇ Download investigation brief (.txt)",report,file_name=f"{C['id']}_investigation.txt",mime="text/plain",use_container_width=True)
    import json
    machine_report={"case":C,"assessment":F,"evidence":[{"id":e["id"],"type":e["type"],"source":e["source"],"timestamp":e["timestamp"],"analysis":e["analysis"]} for e in st.session_state.evidence],"notes":st.session_state.notes}
    st.download_button("Download structured case data (.json)",json.dumps(machine_report,indent=2,default=str),file_name=f"{C['id']}_case.json",mime="application/json",use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown("<div class='footer'>CYBER RAKSHAK · PART 1 · LOCAL EVIDENCE INTELLIGENCE · INVESTIGATIVE LEAD ONLY · HUMAN VERIFICATION REQUIRED</div>",unsafe_allow_html=True)
