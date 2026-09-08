CYBER RAKSHAK FINAL
===================

Unified Part 1 + Part 2 investigative-support application.

PART 1 — INVESTIGATION
- Account / secure login and registration
- Case setup
- Evidence intake: text, URL, transactions, public context, audio/transcript
- AI evidence analysis
- Risk assessment
- Investigation report + report email
- Feedback, contact, FAQ, safety and account workspace

PART 2 — NETWORK INTELLIGENCE
- Data & Match
- Financial Network
- Cyber Network
- Relationship Graph
- Multi-Hop Paths (1/2/3 hops)
- Clusters / communities
- Centrality & bridge analysis
- Transaction Flow
- Entity Similarity
- Timeline
- AI Correlation
- Evidence Chain / Why Connected
- Evidence Ledger / provenance

The Part 2 section uses the same case, datasets and evidence workspace as Part 1.
It is not a second application.

Responsible-use boundary:
The application produces evidence-supported analytical signals. A relationship, identifier match, risk score or graph position is not by itself proof of criminality, identity, intent or legal responsibility. Human review and source verification are required.

Run:
1. Install requirements_cyber_rakshak_final.txt
2. Run RUN_APP_FINAL.bat or: streamlit run cyber_rakshak_final.py

LOGIN OPTIONS
-------------
1. Gmail/email + Cyber Rakshak password:
   The login field accepts the Gmail address registered to the Cyber Rakshak
   account, plus that account's Cyber Rakshak password. The app never asks for
   or stores a user's Google/Gmail password.

2. Continue with Google (optional):
   Add the [auth] block from STREAMLIT_SECRETS_EXAMPLE_CYBER_RAKSHAK_FINAL.txt
   to .streamlit/secrets.toml. The Google button will then use Streamlit's
   OpenID Connect flow. Google handles the Google password on Google's own
   authentication page; Cyber Rakshak receives the authenticated identity and
   maps it to the local workspace.

IMPORTANT
---------
The Google button is intentionally disabled when [auth] is not configured.
This prevents a misleading login control in local deployments that have not
been connected to Google yet.


EMAIL DELIVERY SERVICE
- Report & Email includes Send investigation brief and Send test email.
- SMTP credentials are read only from Streamlit secrets.
- The report can be attached as a .txt file.
- Do not place mailbox passwords in the Python source or commit secrets.toml.
