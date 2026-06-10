# Employee Actor — Use Case Diagram

The **Employee** is the individual contributor: submits weekly timesheets with hours and activity tags, and views own allocations. No access to other employees, projects, or allocation management.

---

## Use Case Diagram

```mermaid
flowchart TB
    Employee(["Employee"])

    subgraph Auth["Authentication"]
        UC_Login(["Login"])
        UC_ChangePwd(["Force Password Change"])
        UC_Logout(["Logout"])
    end

    subgraph EmpUC["Employee — Self Service"]
        UC_Submit(["Submit Weekly Timesheet"])
        UC_Tags(["Select Activity Tags"])
        UC_ViewTS(["View My Timesheet History"])
        UC_ViewAlloc(["View My Allocations"])
        UC_Reminder(["Timesheet Missed Reminder"])
    end

    Employee --> UC_Login
    Employee --> UC_Logout
    Employee --> UC_Submit
    Employee --> UC_ViewTS
    Employee --> UC_ViewAlloc

    UC_Login -.->|"<<extend>>"| UC_ChangePwd
    UC_Submit -.->|"<<include>>"| UC_Tags
    UC_Reminder -.->|"<<extend>>"| UC_Submit

    classDef actor fill:#F3F4F6,stroke:#374151,stroke-width:2px
    classDef auth fill:#FFF7E6,stroke:#D97706,stroke-width:1.5px
    classDef uc fill:#F5F3FF,stroke:#6D28D9,stroke-width:1.5px
    class Employee actor
    class UC_Login,UC_ChangePwd,UC_Logout auth
    class UC_Submit,UC_Tags,UC_ViewTS,UC_ViewAlloc,UC_Reminder uc
```

---

## Use case summary

| Use case | What Employee does |
|----------|-------------------|
| Submit Weekly Timesheet | Log hours per allocated project for a week |
| Select Activity Tags | Tag work type (e.g. API Development, Bug Fixing) |
| View My Timesheet History | Past weeks with SUBMITTED / MISSED status |
| View My Allocations | Own project assignments, %, dates, ACTIVE flag |
| Timesheet Missed Reminder | Menu warning if previous week was not submitted |

---

## Relationships in this diagram

| Link | Type | Meaning |
|------|------|---------|
| Login → Change Password | `<<extend>>` | Only on first login |
| Submit → Select Activity Tags | `<<include>>` | Every submission **must** attach activity tags to entries |
| Missed Reminder → Submit | `<<extend>>` | Reminder **optionally** prompts employee to submit when a week was missed |

---

## Validation rules

| Rule | Detail |
|------|--------|
| Projects | Only projects the employee was allocated to that week |
| Hours per project | ≤ allocation % × max weekly hours |
| Total hours | ≤ max weekly hours (default 40 from system config) |
| Duplicate | One timesheet per employee per week |
| Future weeks | Cannot submit for a week that has not started |

---

## Employee cannot do

- View other employees' data
- Create or edit allocations
- Manage projects or system settings
