# Manager Actor — Use Case Diagram

The **Manager** is the delivery manager: searches for team resources, allocates people to **own projects**, monitors health, and views team timesheets (read-only). Scope is limited to **own team** (`manager_id`) and **own projects** (`manager_user_id`).

---

## Use Case Diagram

```mermaid
flowchart TB
    Manager(["Manager"])

    subgraph Auth["Authentication"]
        UC_Login(["Login"])
        UC_ChangePwd(["Force Password Change"])
        UC_Logout(["Logout"])
    end

    subgraph MgrUC["Manager — Operations"]
        UC_Dashboard(["Resource Dashboard"])
        UC_Allocate(["Allocate Resource"])
        UC_End(["End Allocation"])
        UC_Projects(["View My Projects and Health"])
        UC_TeamTS(["View Team Timesheets"])
        UC_AISkill(["AI Skill Match"])
        UC_AIRisk(["AI Risk Summary"])
    end

    Manager --> UC_Login
    Manager --> UC_Logout
    Manager --> UC_Dashboard
    Manager --> UC_Allocate
    Manager --> UC_End
    Manager --> UC_Projects
    Manager --> UC_TeamTS

    UC_Login -.->|"<<extend>>"| UC_ChangePwd
    UC_Allocate -.->|"<<extend>>"| UC_AISkill
    UC_Projects -.->|"<<extend>>"| UC_AIRisk
    UC_Dashboard -.->|"<<include>>"| UC_Allocate

    classDef actor fill:#F3F4F6,stroke:#374151,stroke-width:2px
    classDef auth fill:#FFF7E6,stroke:#D97706,stroke-width:1.5px
    classDef uc fill:#ECFDF5,stroke:#15803D,stroke-width:1.5px
    class Manager actor
    class UC_Login,UC_ChangePwd,UC_Logout auth
    class UC_Dashboard,UC_Allocate,UC_End,UC_Projects,UC_TeamTS,UC_AISkill,UC_AIRisk uc
```

---

## Use case summary

| Use case | What Manager does |
|----------|-------------------|
| Resource Dashboard | Bench + allocated counts for **own team only** |
| Allocate Resource | Assign team member to own project with % and dates |
| End Allocation | End allocation on own project (set end date to today) |
| View My Projects and Health | Projects where `manager_user_id` = this manager; health flags |
| View Team Timesheets | Read-only SUBMITTED / MISSED status for team |
| AI Skill Match | Optional natural-language search for best team candidates |
| AI Risk Summary | Optional plain-English risk paragraph for a project |

---

## Relationships in this diagram

| Link | Type | Meaning |
|------|------|---------|
| Login → Change Password | `<<extend>>` | Only on first login |
| Allocate → AI Skill Match | `<<extend>>` | Manager **may** use AI; direct allocation without AI is also valid |
| My Projects → AI Risk Summary | `<<extend>>` | Manager **may** request AI summary; health flags show without AI |
| Dashboard → Allocate | `<<include>>` | Dashboard is the entry point that leads into allocation workflow |

---

## Business rules (viva)

| Rule | Detail |
|------|--------|
| Team scope | Only employees where `employee.manager_id` = manager's user id |
| Project scope | Only projects where `project.manager_user_id` = manager's user id |
| Utilization | Overlapping allocations for same employee must not exceed **100%** |
| Timesheets | **Read-only** — Manager cannot edit employee submissions |

---

## Manager cannot do

- Edit employee profiles or system config
- Create user accounts
- View company-wide allocations (Admin only)
