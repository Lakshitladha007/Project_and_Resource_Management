import typer

from client import display
from client.api_client import ApiError, get, post, put
from client.screens.admin import milestones as milestones_screen
from client.validators import format_date, parse_date

CREATE_STATUS_MAP = {"1": "PLANNED", "2": "ACTIVE", "3": "ON_HOLD"}
UPDATE_STATUS_MAP = {
    "1": "PLANNED",
    "2": "ACTIVE",
    "3": "ON_HOLD",
    "4": "COMPLETED",
}


def manage_projects() -> None:
    while True:
        typer.echo("")
        display.banner(["MANAGE PROJECTS"])
        display.menu(
            [
                ("1", "Create Project"),
                ("2", "View All Projects"),
                ("3", "Update Project Details"),
                ("4", "Manage Milestones"),
                ("5", "Back"),
            ]
        )
        choice = typer.prompt("Enter option").strip()
        if choice == "1":
            _create_project()
        elif choice == "2":
            _view_projects()
        elif choice == "3":
            _update_project()
        elif choice == "4":
            milestones_screen.manage_milestones()
        elif choice == "5":
            return
        else:
            display.error("Invalid option.")


def _create_project() -> None:
    typer.echo("")
    display.banner(["CREATE PROJECT"])
    name = typer.prompt("Project Name")
    description = typer.prompt("Description", default="", show_default=False)
    try:
        start_date = parse_date(typer.prompt("Start Date (DD-MM-YYYY)"), "Start Date")
        end_date = parse_date(typer.prompt("End Date (DD-MM-YYYY)"), "End Date")
    except ValueError as exc:
        display.error(str(exc))
        return
    status_choice = typer.prompt(
        "Status (1) PLANNED (2) ACTIVE (3) ON_HOLD"
    ).strip()
    status = CREATE_STATUS_MAP.get(status_choice)
    if status is None:
        display.error("Invalid status selection.")
        return
    manager_user_id = typer.prompt("Assign Manager (Manager User ID)")
    total_sp = typer.prompt("Total Story Points")
    try:
        post(
            "/admin/projects",
            {
                "name": name,
                "description": description,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "status": status,
                "manager_user_id": int(manager_user_id),
                "total_story_points": int(total_sp),
            },
            auth=True,
        )
    except (ApiError, ValueError) as exc:
        display.error(str(exc))
        return
    display.success("Project created.")


def _view_projects() -> None:
    try:
        projects = get("/admin/projects")
    except ApiError as exc:
        display.error(str(exc))
        return
    typer.echo("")
    display.banner(["ALL PROJECTS"])
    typer.echo(
        f"{'ID':<5} {'Name':<18} {'Manager':<14} {'End Date':<12} "
        f"{'Status':<10} SP Done/Total"
    )
    display.rule()
    for p in projects:
        typer.echo(
            f"{p['id']:<5} {p['name']:<18} {p['manager_name']:<14} "
            f"{format_date(p['end_date']):<12} {p['status']:<10} "
            f"{p['story_points_done']} / {p['total_story_points']}"
        )
    display.rule()


def _optional_date(prompt_text: str):
    value = typer.prompt(prompt_text, default="", show_default=False).strip()
    if not value:
        return None
    return parse_date(value, prompt_text)


def _update_project() -> None:
    typer.echo("")
    display.banner(["UPDATE PROJECT DETAILS"])
    project_id = typer.prompt("Enter Project ID")
    typer.echo("Leave a field blank to keep the current value.")
    payload = {}
    name = typer.prompt("Project Name", default="", show_default=False).strip()
    if name:
        payload["name"] = name
    description = typer.prompt("Description", default="", show_default=False).strip()
    if description:
        payload["description"] = description
    try:
        start_date = _optional_date("Start Date (DD-MM-YYYY)")
        if start_date:
            payload["start_date"] = start_date.isoformat()
        end_date = _optional_date("End Date (DD-MM-YYYY)")
        if end_date:
            payload["end_date"] = end_date.isoformat()
    except ValueError as exc:
        display.error(str(exc))
        return
    status_choice = typer.prompt(
        "Status (1) PLANNED (2) ACTIVE (3) ON_HOLD (4) COMPLETED",
        default="",
        show_default=False,
    ).strip()
    if status_choice:
        status = UPDATE_STATUS_MAP.get(status_choice)
        if status is None:
            display.error("Invalid status selection.")
            return
        payload["status"] = status
    manager_user_id = typer.prompt(
        "Assign Manager (Manager User ID)", default="", show_default=False
    ).strip()
    if manager_user_id:
        payload["manager_user_id"] = int(manager_user_id)
    total_sp = typer.prompt("Total Story Points", default="", show_default=False).strip()
    if total_sp:
        payload["total_story_points"] = int(total_sp)
    if not payload:
        display.info("Nothing to update.")
        return
    try:
        put(f"/admin/projects/{project_id}", payload, auth=True)
    except (ApiError, ValueError) as exc:
        display.error(str(exc))
        return
    display.success("Project updated.")
