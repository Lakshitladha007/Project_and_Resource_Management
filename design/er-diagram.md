# ER Diagram - PRM Tool

```mermaid
erDiagram
    USERS ||--o| EMPLOYEES : links
    USERS ||--o{ EMPLOYEES : leads
    USERS ||--o{ PROJECTS : manages
    EMPLOYEES ||--o{ EMPLOYEE_SKILLS : has
    SKILLS ||--o{ EMPLOYEE_SKILLS : includes
    EMPLOYEES ||--o{ ALLOCATIONS : assigned
    PROJECTS ||--o{ ALLOCATIONS : contains
    PROJECTS ||--o{ MILESTONES : has
    EMPLOYEES ||--o{ TIMESHEETS : submits
    TIMESHEETS ||--o{ TIMESHEET_ENTRIES : contains
    PROJECTS ||--o{ TIMESHEET_ENTRIES : logs
    TIMESHEET_ENTRIES ||--o{ TIMESHEET_ENTRY_TAGS : tags
    ACTIVITY_TAGS ||--o{ TIMESHEET_ENTRY_TAGS : used

    USERS {
        int id
        string username
        string email
        string password_hash
        string role
        string is_active
        string force_password_change
        string created_at
        string updated_at
    }

    EMPLOYEES {
        int id
        int user_id
        int manager_id
        string full_name
        string email
        string department
        string designation
        string status
        string is_active
        string created_at
        string updated_at
    }

    SKILLS {
        int id
        string name
        string category
        string created_at
    }

    EMPLOYEE_SKILLS {
        int id
        int employee_id
        int skill_id
        string proficiency
        string updated_at
    }

    PROJECTS {
        int id
        string name
        string description
        string start_date
        string end_date
        string status
        int manager_user_id
        int total_story_points
        string health_status
        string created_at
        string updated_at
    }

    MILESTONES {
        int id
        int project_id
        string title
        string due_date
        int story_points
        string status
        string updated_at
    }

    ALLOCATIONS {
        int id
        int employee_id
        int project_id
        int utilization_percent
        string alloc_start
        string alloc_end
        string is_active
        string created_at
    }

    TIMESHEETS {
        int id
        int employee_id
        string week_start
        int total_hours
        string status
        string submitted_at
    }

    TIMESHEET_ENTRIES {
        int id
        int timesheet_id
        int project_id
        int hours
    }

    ACTIVITY_TAGS {
        int id
        string name
        string is_system_tag
    }

    TIMESHEET_ENTRY_TAGS {
        int id
        int timesheet_entry_id
        int activity_tag_id
    }

    SYSTEM_CONFIG {
        int id
        string llm_provider
        string llm_api_key_encrypted
        int scheduler_interval_hours
        int max_weekly_hours
        string updated_at
    }
```

## Keys and Constraints
| Rule | Detail |
|---|---|
| USERS | `username`, `email` unique |
| EMPLOYEES | `user_id` unique FK to USERS; `manager_id` FK to USERS (manager) |
| PROJECTS | `name` unique; `manager_user_id` FK to USERS; `total_story_points` >= 0 |
| MILESTONES | `story_points` >= 0; project SP = sum of milestone SP |
| TIMESHEETS | unique per `employee_id` + `week_start` |
| ALLOCATIONS | overlapping totals must not exceed 100% |

## Enum Reference
| Table | Column | Values |
|---|---|---|
| USERS | role | ADMIN, MANAGER, EMPLOYEE |
| EMPLOYEES | status | BENCH, ALLOCATED |
| SKILLS | category | BACKEND, FRONTEND, DEVOPS, QA, OTHER |
| EMPLOYEE_SKILLS | proficiency | BEGINNER, INTERMEDIATE, ADVANCED |
| PROJECTS | status | PLANNED, ACTIVE, ON_HOLD, COMPLETED |
| PROJECTS | health_status | ON_TRACK, ATTENTION, AT_RISK |
| MILESTONES | status | NOT_STARTED, IN_PROGRESS, DONE |
| TIMESHEETS | status | SUBMITTED, MISSED |
| SYSTEM_CONFIG | llm_provider | GEMINI, GROQ |
