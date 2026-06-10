# Admin Actor — Use Case Diagram

The **Admin** is the system operator (HR/ops). In PRM this is the role that manages **user accounts** and **master data**. Admin does not allocate resources or submit timesheets.

Shared authentication (Login, Logout, Change Password) is shown here because Admin must authenticate like any other role.

---

## Use Case Diagram

```mermaid
flowchart TB
    Admin(["Admin"])

    subgraph Auth["Authentication"]
        UC_Login(["Login"])
        UC_ChangePwd(["Force Password Change"])
        UC_Logout(["Logout"])
    end

    subgraph AdminUC["Admin — Master Data"]
        UC_CreateUser(["Manage Users"])
        UC_ResetPwd(["Reset User Password"])
        UC_Employees(["Manage Employees"])
        UC_DeactivateEmp(["Deactivate Employee"])
        UC_Skills(["Manage Employee Skills"])
        UC_AssignMgr(["Assign Manager"])
        UC_Projects(["Manage Projects and Story Points"])
        UC_Milestones(["Manage Milestones and Story Points"])
        UC_ViewAlloc(["View All Allocations"])
        UC_Config(["System Configuration"])
    end

    Admin --> UC_Login
    Admin --> UC_Logout
    Admin --> UC_CreateUser
    Admin --> UC_Employees
    Admin --> UC_Skills
    Admin --> UC_AssignMgr
    Admin --> UC_Projects
    Admin --> UC_Milestones
    Admin --> UC_ViewAlloc
    Admin --> UC_Config

    UC_Login -.->|"<<extend>>"| UC_ChangePwd
    UC_CreateUser -.->|"<<include>>"| UC_ResetPwd
    UC_Employees -.->|"<<include>>"| UC_DeactivateEmp
    UC_Employees -.->|"<<include>>"| UC_Skills
    UC_Projects -.->|"<<include>>"| UC_Milestones
    UC_CreateUser -.->|"<<include>>"| UC_Employees

    classDef actor fill:#F3F4F6,stroke:#374151,stroke-width:2px
    classDef auth fill:#FFF7E6,stroke:#D97706,stroke-width:1.5px
    classDef uc fill:#E0F2FE,stroke:#0369A1,stroke-width:1.5px
    class Admin actor
    class UC_Login,UC_ChangePwd,UC_Logout auth
    class UC_CreateUser,UC_ResetPwd,UC_Employees,UC_DeactivateEmp,UC_Skills,UC_AssignMgr,UC_Projects,UC_Milestones,UC_ViewAlloc,UC_Config uc
```

---

## Use case summary

| Use case | What Admin does |
|----------|-----------------|
| Login / Logout | Authenticate into Admin menu |
| Force Password Change | Required on first login for Admin-created accounts |
| Manage Users | Create, view, deactivate/reactivate accounts (Admin, Manager, Employee roles) |
| Reset User Password | Set temporary password; user must change on next login |
| Manage Employees | View all, update profile fields |
| Deactivate Employee | Soft-deactivate profile; active allocations ended |
| Manage Employee Skills | Add/update/remove skills and proficiency |
| Assign Manager | Set `manager_id` so Manager sees only their team |
| Manage Projects | Create, view, update projects and total story points |
| Manage Milestones | Add/update milestones and story points per project |
| View All Allocations | Company-wide allocation matrix (read-only) |
| System Configuration | LLM provider/key, scheduler interval, max weekly hours |

---

## Relationships in this diagram

| Link | Type | Meaning |
|------|------|---------|
| Login → Change Password | `<<extend>>` | Password change runs **only when** first-login flag is set |
| Manage Users → Manage Employees | `<<include>>` | Creating Manager/Employee role **always** creates an employee profile |
| Manage Users → Reset Password | `<<include>>` | User management flow **includes** password reset as a sub-action |
| Manage Employees → Deactivate / Skills | `<<include>>` | Employee management **includes** these sub-features |
| Manage Projects → Manage Milestones | `<<include>>` | Project management **includes** milestone management |

---

## Admin cannot do

- Create allocations (Manager only)
- Submit or edit timesheets
- Use Manager AI dashboard for day-to-day allocation
