CYBER RAKSHAK — UNIFIED V3
===========================

This build combines the complete Part 1 baseline with the complete Part 2 V4 network workspace.

PART 1 FEATURES
- Public landing page
- Top-right Sign in / Register controls
- Email OR username login
- SQLite account persistence
- PBKDF2-HMAC-SHA256 password hashing
- Linked account email
- Case persistence
- Evidence persistence
- Evidence intake
- Text analysis and entity extraction
- URL structural analysis
- Transaction anomaly baseline
- Public-source context analysis
- Audio/transcript baseline with honest limitations
- Explainable AI analysis
- Risk assessment
- Investigation report + JSON export
- Report email via Streamlit SMTP secrets
- FAQ
- About Team
- Feedback & Reviews in separate database
- Contact notes in separate database
- Safety & official response page
- English / Hindi / Tamil / Bengali language selector

PART 2 FEATURES
- Data & Match
- CSV / Excel / JSON / TXT ingestion
- Identifier normalization: phone/email/account/IP/domain/URL
- Source-traceable match results
- Financial Network
- Cyber Network
- Relationship Graph
- Multi-Hop Paths
- Clusters
- Centrality & Bridges
- Transaction Flow
- Entity Similarity
- Timeline
- AI Correlation
- Evidence Chain / Why Connected?
- Evidence Ledger
- Bundled structured synthetic demo dataset

DEMO
- Use the sidebar action “Load bundled demo pack”.
- Search: +91-70000-00001
- The bundled data is synthetic/fictitious and intended only for testing.

SECURITY / RESPONSIBLE ANALYSIS
- The application is an investigative decision-support prototype.
- It does not determine legal guilt or automatically label a person a criminal.
- Connections are based on supplied/authorized records.
- Do not use it to probe external systems or access private communications.
- Keep SMTP credentials in Streamlit secrets, not in Python source.

RUN
1. Open a terminal in this folder.
2. python -m pip install -r requirements_cyber_rakshak_unified_v3.txt
3. python -m streamlit run cyber_rakshak_unified_v3.py

TEST
python test_cyber_rakshak_unified_v3.py

The automated test suite checks all navigation branches, authentication, demo matching,
graph construction, Part 1 analysis functions, evidence persistence and feedback persistence.
