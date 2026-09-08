# CYBER RAKSHAK FINAL

AI-assisted cyber investigation and evidence-analysis platform built with Streamlit.

## Final repository structure

```text
CYBER_RAKSHAK_FINAL/
├── cyber_rakshak_final.py      # Main public application
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

## Final fixes included

- Working language switching with English, Hindi, Tamil and Bengali labels/navigation.
- Login/Register redesigned as two equal high-contrast controls.
- Responsive light-mode layout for desktop, tablet and mobile.
- Google OIDC login support using Streamlit authentication secrets.
- SMTP/server email delivery and test email.
- Server-side SQLite persistence for registrations, cases, evidence and provenance.
- SQLite WAL + busy timeout for better multi-user submission reliability.
- Unified `USER / ADMIN` access on the same page; the Admin Console provides registrations, login activity, feedback, contact notes, cases, evidence and dataset activity.
- In-app Admin Console for configured administrator emails.
- Cached network graphs to reduce repeated graph computation while switching sections.
- Session data remains available in the current browser session.
- Existing investigation, evidence, network, timeline, reporting and correlation features retained.

## Run the main portal

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run cyber_rakshak_final.py
```

## Run the separate admin website

On the same server, use another port:

```bash
streamlit run cyber_rakshak_final.py
```

The admin portal reads the same `server_data/` databases. Keep port 8502 private or protect it behind your server's authentication/firewall.

## Server data flow

When a user on another computer opens the deployed Cyber Rakshak URL, their registration, feedback/contact submission and saved case/evidence metadata are written to the databases on the **server running the application**. The administrator can inspect that data from the Admin Console or the separate admin website.

The application automatically creates:

```text
server_data/
├── cyber_rakshak.sqlite3
└── voxshield_feedback.sqlite3
```

These files are intentionally ignored by Git. They contain runtime data and must not be committed to a public repository.

### Important hosting limitation

This is a server-side SQLite design. It works as a central database when the Streamlit application and `server_data/` live on the same persistent server. Some cloud platforms use ephemeral filesystems, so SQLite data can disappear after a restart/redeploy. For production-scale deployment, migrate the database layer to PostgreSQL or another managed persistent database.

## Google login

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill the `[auth]` values. Google OAuth must use the exact deployed callback URL ending in `/oauth2callback`.

Never put Google client secrets, SMTP passwords or the admin portal password into GitHub.

## SMTP email

Fill the `[smtp]` section with the SMTP settings of the mailbox/provider used by the server. The application supports test email and investigation brief delivery.

## Admin access

For the in-app Admin Console, add one or more authorized email addresses to `admin_emails`.

Set `admin_portal_password` as the initial admin password in server secrets, then change it from the Admin Console.

## Responsible-use boundary

Cyber Rakshak is an investigation-support prototype. Network connections, similarity, anomalies and risk signals are not proof that a person committed a crime. Use authorized evidence, verify source provenance and keep a human decision-maker in the loop.

## Team Admin Portal

The repository uses one Streamlit page. Choose USER or ADMIN on the authentication screen; ADMIN opens the protected Admin Console.

Only users with a valid private team invitation code can register a team account. Team accounts are stored in `server_data/team_admin.sqlite3`, separate from public-user credentials.

Run it with:

```bash
streamlit run cyber_rakshak_final.py
```

Administrative sections include Users & Registration, Login Activity, Feedback, Contact Messages, Cases, Evidence, Dataset Activity, Team Members and Audit Log, with search and CSV export.

See `ADMIN_PORTAL_SETUP.md` and `TEAM_ADMIN_REGULATIONS.md` before deployment.
