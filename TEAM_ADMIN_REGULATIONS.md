# CYBER RAKSHAK — TEAM ADMIN REGULATIONS

## 1. Purpose

The Team Command Center is a private administrative interface for authorized project-team members. It is intended to monitor application registrations, login activity, feedback, contact messages, investigation metadata, evidence records, dataset provenance and team audit events.

## 2. Access control

1. The public registration form does **not** grant administrative access.
2. Team registration requires a private invitation code configured in Streamlit secrets.
3. The administrator invitation code and team-member invitation code must never be committed to GitHub.
4. Team passwords are stored as salted PBKDF2-SHA256 password hashes, not plaintext passwords.
5. Only active team accounts may enter the command center.
6. The command center should be deployed privately or behind an additional platform-level access control where available.
7. Do not share the command-center URL, invitation codes or server secrets publicly.

## 3. Roles

### Admin

- May access all administrative database views.
- May review team accounts and audit events.
- Should be limited to trusted project leads.

### Team member

- May access the administrative read-only database views required for project operations.
- Should not receive server secrets or database files directly.

## 4. Database handling

The portal presents controlled views of the application's server-side SQLite databases. The database files themselves must not be exposed through a public download route.

Administrative exports should be created only for an authorized project purpose and stored securely.

## 5. Personal data handling

The system may contain account details and messages submitted by users. Team members should:

- access only what is necessary for project operation;
- avoid copying personal information into unrelated documents;
- avoid sharing exported records in public repositories or chat groups;
- delete or archive records according to the project's approved retention policy;
- use anonymized or synthetic records for demonstrations whenever possible.

## 6. Investigation data

Investigation metadata and evidence records may be sensitive. Administrative access does not mean that a team member may use the information for an unauthorized investigation.

Analytical scores, correlations, network relationships and risk indicators are investigative-support signals. They must not be presented as proof of criminality or guilt without appropriate human verification and lawful authority.

## 7. Auditability

The command center records administrative login/logout events and other team administrative events. Audit records should not be edited casually because they provide accountability for administrative access.

## 8. Secrets management

Never commit:

- `.streamlit/secrets.toml`
- Google client secrets
- SMTP passwords
- Team invitation codes
- production database files
- exported user/feedback/evidence CSV files

Use the included `secrets.toml.example` only as a template.

## 9. Deployment rule

Local SQLite is suitable for a prototype or controlled demonstration. For production or multi-instance deployment, use a properly managed persistent database and secure secret-management system. A cloud platform may use an ephemeral filesystem, so local SQLite files should not be assumed to survive every restart or redeployment.

## 10. Incident response

If an invitation code, password or server credential is exposed:

1. Rotate the exposed credential immediately.
2. Review the admin audit trail.
3. Review recent administrative access.
4. Revoke or disable affected team accounts where appropriate.
5. Do not commit the exposed credential while attempting to document the incident.

## 11. Responsible-use rule

Cyber Rakshak is an evidence-analysis and investigation-support prototype. It must not be used to make unsupported decisions about a person's criminality, identity, intent or legal responsibility. Human review and appropriate authorization remain mandatory.

## 12. Competition/demo rule

For demonstrations, prefer synthetic datasets. If real user-submitted information is used, restrict access to the project team and avoid exposing it in screenshots, GitHub repositories, presentations or public deployment logs.

> This document is an internal project security/governance policy, not legal advice. Before production use, the project owner should review applicable privacy, cybersecurity, evidence-handling and data-retention requirements with the responsible institution or qualified counsel.
