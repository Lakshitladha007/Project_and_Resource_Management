# Sequence Diagrams - All Roles

## 1) Admin - Create User, Assign Manager, and Skills

```mermaid
sequenceDiagram
    autonumber
    actor A as Admin
    participant C as Console Client
    participant API as REST API
    participant Auth as Auth Service
    participant UserS as User Service
    participant EmpS as Employee Service
    participant SkillS as Skill Service
    participant DB as Database

    A->>C: Create User Account
    C->>API: POST /users
    API->>Auth: validate admin token and role
    API->>UserS: createUser
    UserS->>DB: insert user with force_password_change
    UserS->>EmpS: auto create employee profile if role is MANAGER or EMPLOYEE
    EmpS->>DB: insert employee status BENCH linked by user_id
    DB-->>UserS: user_id and employee_id
    UserS-->>API: created
    API-->>C: 201 Created

    A->>C: Assign Manager to Employee
    C->>API: PUT /employees/by-id/manager
    API->>EmpS: assignManager
    EmpS->>DB: validate manager user has MANAGER role
    EmpS->>DB: set employee manager_id
    DB-->>EmpS: success
    EmpS-->>API: success
    API-->>C: 200 OK

    A->>C: Add Employee Skill
    C->>API: POST /employees/by-id/skills
    API->>SkillS: addSkill
    SkillS->>DB: upsert skill proficiency category
    DB-->>SkillS: success
    SkillS-->>API: success
    API-->>C: 200 OK
```

> Note: V4 removed the separate "Add Employee" screen. The employee profile is created automatically when an Admin creates a MANAGER or EMPLOYEE user account, then enriched via Update Employee, Assign Manager, and Manage Skills.

## 2) Manager - AI Assisted Allocation

```mermaid
sequenceDiagram
    autonumber
    actor M as Manager
    participant C as Console Client
    participant API as REST API
    participant AllocS as Allocation Service
    participant CapS as Capacity Service
    participant AIS as AI Match Service
    participant DB as Database

    M->>C: Enter project and NL requirement
    C->>API: POST /ai/skill-match
    API->>AllocS: validate manager owns project
    AllocS->>DB: fetch project and team candidates by manager_id
    DB-->>AllocS: own team employees and allocations
    AllocS->>CapS: filter by free capacity
    CapS-->>AllocS: eligible candidates
    AllocS->>AIS: rank candidates with reasons
    AIS-->>AllocS: ranked suggestions
    AllocS-->>API: match response
    API-->>C: suggestions

    M->>C: Confirm employee and allocation
    C->>API: POST /allocations
    API->>AllocS: createAllocation
    AllocS->>DB: validate employee is in manager team
    AllocS->>DB: validate overlap max 100 percent
    AllocS->>DB: insert allocation
    DB-->>AllocS: success
    AllocS-->>API: allocation created
    API-->>C: 201 Created
```

## 3) Manager - Project Risk Summary

```mermaid
sequenceDiagram
    autonumber
    actor M as Manager
    participant C as Console Client
    participant API as REST API
    participant HealthS as Project Health Service
    participant AIS as AI Risk Service
    participant DB as Database

    M->>C: Request AI risk summary
    C->>API: GET /projects/by-id/risk-summary
    API->>HealthS: buildRiskContext
    HealthS->>DB: fetch milestones allocations timesheets
    DB-->>HealthS: factual project data
    HealthS->>AIS: summarize risks from facts
    AIS-->>HealthS: plain English summary
    HealthS-->>API: summary and risk flags
    API-->>C: 200 OK
```

## 4) Employee - Weekly Timesheet Submission

```mermaid
sequenceDiagram
    autonumber
    actor E as Employee
    participant C as Console Client
    participant API as REST API
    participant TS as Timesheet Service
    participant Rule as Timesheet Rules Engine
    participant DB as Database

    E->>C: Submit week entries and tags
    C->>API: POST /timesheets
    API->>TS: submitTimesheet
    TS->>DB: fetch active allocations for week
    DB-->>TS: allocation set
    TS->>Rule: validate per project and total hours
    Rule-->>TS: valid
    TS->>DB: check duplicate timesheet
    DB-->>TS: no duplicate
    TS->>DB: insert timesheet entries tags
    DB-->>TS: success
    TS-->>API: submitted
    API-->>C: 201 Created
```

## 5) Scheduler - Health and Utilization Recompute

```mermaid
sequenceDiagram
    autonumber
    participant Sch as Scheduler
    participant Job as Recompute Job
    participant HealthS as Project Health Service
    participant UtilS as Utilization Service
    participant DB as Database

    Sch->>Job: trigger at configured interval
    Job->>UtilS: recompute employee utilization
    UtilS->>DB: read allocations update status
    DB-->>UtilS: done
    Job->>HealthS: recompute project health flags
    HealthS->>DB: read milestones and effort signals
    DB-->>HealthS: done
    Job-->>Sch: job complete
```
