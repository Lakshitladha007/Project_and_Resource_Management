import typer

from client import display
from client.api_client import ApiError, delete, get, post, put

CATEGORY_MAP = {
    "1": "BACKEND",
    "2": "FRONTEND",
    "3": "DEVOPS",
    "4": "QA",
    "5": "OTHER",
}
PROFICIENCY_MAP = {
    "1": "BEGINNER",
    "2": "INTERMEDIATE",
    "3": "ADVANCED",
}
PROFICIENCY_LABEL = {
    "BEGINNER": "Beginner",
    "INTERMEDIATE": "Intermediate",
    "ADVANCED": "Advanced",
}


def manage_skills() -> None:
    typer.echo("")
    display.banner(["MANAGE SKILLS"])
    employee_id = typer.prompt("Enter Employee ID")
    try:
        employees = get("/admin/employees")
    except ApiError as exc:
        display.error(str(exc))
        return
    employee = next((e for e in employees if str(e["id"]) == employee_id), None)
    if employee is None:
        display.error(f"No employee with id {employee_id}")
        return

    while True:
        try:
            skills = get(f"/admin/employees/{employee_id}/skills")
        except ApiError as exc:
            display.error(str(exc))
            return

        typer.echo("")
        display.banner(["MANAGE SKILLS"])
        typer.echo(f"-- {employee['full_name']} " + "-" * 30)
        typer.echo("Current Skills:")
        if skills:
            for idx, skill in enumerate(skills, start=1):
                label = PROFICIENCY_LABEL.get(skill["proficiency"], skill["proficiency"])
                typer.echo(f"  {idx}.  {skill['skill_name']:<18} {label}")
        else:
            typer.echo("  (none)")
        display.rule()
        display.menu(
            [
                ("1", "Add Skill"),
                ("2", "Update Proficiency Level"),
                ("3", "Remove Skill"),
                ("4", "Back"),
            ]
        )
        choice = typer.prompt("Enter option").strip()
        if choice == "1":
            _add_skill(employee_id)
        elif choice == "2":
            _update_proficiency(employee_id, skills)
        elif choice == "3":
            _remove_skill(employee_id, skills)
        elif choice == "4":
            return
        else:
            display.error("Invalid option.")


def _add_skill(employee_id: str) -> None:
    typer.echo("")
    skill_name = typer.prompt("Skill Name")
    category_choice = typer.prompt(
        "Category (1) Backend (2) Frontend (3) DevOps (4) QA (5) Other"
    ).strip()
    proficiency_choice = typer.prompt(
        "Proficiency Level (1) Beginner (2) Intermediate (3) Advanced"
    ).strip()
    category = CATEGORY_MAP.get(category_choice)
    proficiency = PROFICIENCY_MAP.get(proficiency_choice)
    if category is None or proficiency is None:
        display.error("Invalid category or proficiency selection.")
        return
    try:
        post(
            f"/admin/employees/{employee_id}/skills",
            {
                "skill_name": skill_name,
                "category": category,
                "proficiency": proficiency,
            },
            auth=True,
        )
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Skill added.")


def _update_proficiency(employee_id: str, skills: list) -> None:
    if not skills:
        display.error("This employee has no skills to update.")
        return
    skill_id = typer.prompt("Enter skill number from the list above")
    if not skill_id.isdigit() or int(skill_id) < 1 or int(skill_id) > len(skills):
        display.error("Invalid skill number.")
        return
    row = skills[int(skill_id) - 1]
    proficiency_choice = typer.prompt(
        "New Proficiency (1) Beginner (2) Intermediate (3) Advanced"
    ).strip()
    proficiency = PROFICIENCY_MAP.get(proficiency_choice)
    if proficiency is None:
        display.error("Invalid proficiency selection.")
        return
    try:
        put(
            f"/admin/employees/{employee_id}/skills/{row['id']}",
            {"proficiency": proficiency},
            auth=True,
        )
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Proficiency updated.")


def _remove_skill(employee_id: str, skills: list) -> None:
    if not skills:
        display.error("This employee has no skills to remove.")
        return
    skill_id = typer.prompt("Enter skill number from the list above")
    if not skill_id.isdigit() or int(skill_id) < 1 or int(skill_id) > len(skills):
        display.error("Invalid skill number.")
        return
    row = skills[int(skill_id) - 1]
    confirm = typer.prompt(f"Remove {row['skill_name']}? [Y/N]").strip().lower()
    if confirm != "y":
        display.info("Cancelled.")
        return
    try:
        delete(f"/admin/employees/{employee_id}/skills/{row['id']}", auth=True)
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Skill removed.")
