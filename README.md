# Project & Resource Management (PRM) Tool

A console-based client-server app for IT companies to manage employees, projects, allocations and timesheets. Built as a final project for the Learn & Code program.

---

## What this does

Managing resources across projects on spreadsheets gets messy pretty fast. This tool tries to fix that by giving a single place to track:

- Who's on bench and what skills they have
- Which employees fit a new project requirement (AI-assisted)
- Whether a project is on track or falling behind
- Timesheet submissions for the week

There's a REST API (FastAPI) and a console client (Typer) supporting three roles — Admin, Manager, and Employee.

---

## Roles & what they can do

**Admin**
- Create user accounts, manage employees and skills
- Assign managers, create projects with story points and milestones
- Configure system settings (LLM key, max weekly hours, scheduler)

**Manager**
- View and allocate employees on their team (AI suggestions or manual)
- See project health, story point progress, team timesheets (read-only)

**Employee**
- Submit weekly timesheets with activity tags
- View own allocations and past timesheet history

---

## Tech stack

- Python 3.12, FastAPI, MySQL
- SQLAlchemy + Alembic for ORM and migrations
- Typer for the console client
- JWT for auth, APScheduler for background tasks
- Google Gemini for AI features (Groq as a fallback option)
- pytest for tests

---

## Project structure

```
Project_and_Resource_Management/
├── README.md
├── PRM_BRD_V4.md               # Full requirements doc
├── design/
│   ├── README.md
│   ├── usecase-diagram.md
│   ├── sequence-diagrams.md
│   ├── er-diagram.md
│   └── class-diagram.md
├── src/prm/                    # app source (planned)
├── tests/                      # (planned)
├── migrations/                 # Alembic migrations (planned)
└── scripts/                    # e.g. seed_first_admin.py
```

Code follows a layered structure: domain → application → infrastructure → interfaces (API + console).

---

## Design docs

All diagrams are written in Mermaid inside markdown files under `design/`. Open them with **Markdown Preview** (`Ctrl+Shift+V`) in VS Code, or just view them on GitHub.

| File | What's in it |
|------|--------------|
| `usecase-diagram.md` | Actors and use cases |
| `sequence-diagrams.md` | Key flows for each role + scheduler |
| `er-diagram.md` | Database schema |
| `class-diagram.md` | Services, entities, repositories |

---

## Setup

### Requirements

- Python 3.12+
- MySQL 8.x
- A Google Gemini API key (optional, for AI features)

### Steps

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Set up environment variables
copy .env.example .env        # Windows
# cp .env.example .env        # Mac/Linux
```

Fill in `.env` with your database URL, JWT secret, and optionally the Gemini API key:

```
DATABASE_URL=mysql+pymysql://user:pass@localhost/prm
JWT_SECRET_KEY=your-secret-here
JWT_EXPIRE_MINUTES=60
GEMINI_API_KEY=...
```

```bash
# 4. Run migrations
alembic upgrade head

# 5. Seed the first admin user
python scripts/seed_first_admin.py
# Default login: admin / Admin@1234  — change it on first login

# 6. Start the API server
uvicorn prm.interfaces.api.main:app --reload

# 7. Start the console client
prm-console
```

---

## A few important business rules

- Only admins can create user accounts (no self-registration)
- An employee profile is created at the same time as the user account
- Managers can only see/allocate employees on their own team
- Total allocation for an employee can't exceed 100% at any point
- Timesheet hours per project are capped based on the allocation % × max weekly hours
- No duplicate timesheets for the same employee and week
- AI suggestions are just recommendations — managers confirm allocations manually

---

## Notes

This is an academic project (Learn & Code). The AI integration uses only system data — it doesn't call out to external sources or make autonomous decisions.
