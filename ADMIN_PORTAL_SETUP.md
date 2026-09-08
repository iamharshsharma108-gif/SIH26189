# Team Admin Portal Setup

## 1. Configure secrets

Copy:

`.streamlit/secrets.toml.example`

to:

`.streamlit/secrets.toml`

Then replace the placeholder team invitation codes.

Use two different long random values:

- `team_member_invite_code` — creates a `team_member` account.
- `team_admin_invite_code` — creates an `admin` account.

Never commit the real file.

## 2. Run the main application

```bash
streamlit run cyber_rakshak_final.py
```

## 3. Run the Team Command Center

```bash
streamlit run admin_portal.py --server.port 8502
```

The two applications must use the same deployed filesystem/server data directory for the admin console to see the same SQLite databases.

## 4. Team registration

Open the Team Command Center and use **TEAM REGISTER**. Registration requires the private invitation code. Public Cyber Rakshak users do not automatically become team members.

## 5. Team login

Use **TEAM LOGIN** with the registered team email and password. Only active team accounts can access the database views.

## 6. Database sections

The command center includes:

- Overview
- Users & Registration
- Login Activity
- Feedback
- Contact Messages
- Cases
- Evidence
- Dataset Activity
- Team Members
- Audit Log

Each database section supports search and CSV export where appropriate.

## 7. Deployment architecture

```text
Public users
    |
    v
Cyber Rakshak application
    |
    +---- cyber_rakshak.sqlite3
    |        +-- users
    |        +-- login_activity
    |        +-- cases
    |        +-- evidence
    |        +-- dataset_log
    |        +-- case_notes
    |
    +---- voxshield_feedback.sqlite3
    |        +-- feedback
    |        +-- contact_notes
    |
    +---- team_admin.sqlite3
             +-- team_members
             +-- admin_audit
                    ^
                    |
             Team Command Center
```

For a real production system, replace local SQLite with a managed persistent database when the hosting architecture requires it.
