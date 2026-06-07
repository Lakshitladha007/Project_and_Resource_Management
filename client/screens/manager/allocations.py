import typer

from client import display
from client.api_client import ApiError, get, post
from client.validators import format_date, parse_date


def allocate_resource() -> None:
    while True:
        typer.echo("")
        display.banner(["ALLOCATE RESOURCE"])
        display.menu(
            [
                ("1", "Find resource using AI (recommended)"),
                ("2", "Allocate directly"),
                ("3", "End an existing allocation"),
                ("4", "Back"),
            ]
        )
        choice = typer.prompt("Enter option").strip()
        if choice == "1":
            display.info("AI matching arrives in a later feature.")
        elif choice == "2":
            _allocate_direct()
        elif choice == "3":
            _end_allocation()
        elif choice == "4":
            return
        else:
            display.error("Invalid option.")


def _show_team() -> None:
    try:
        team = get("/manager/employees")
    except ApiError as exc:
        display.error(str(exc))
        return
    typer.echo("")
    typer.echo("Your team:")
    typer.echo(f"{'ID':<5} {'Name':<20} {'Dept':<14} {'Util':<6} Status")
    display.rule()
    for e in team:
        dept = e["department"] or "-"
        typer.echo(
            f"{e['id']:<5} {e['full_name']:<20} {dept:<14} "
            f"{e['current_utilization']}%{'':<4} {e['status']}"
        )
    display.rule()


def _show_projects(allocatable_only: bool = False) -> bool:
    try:
        projects = get("/manager/projects")
    except ApiError as exc:
        display.error(str(exc))
        return False
    if allocatable_only:
        projects = [p for p in projects if p["status"] in ("PLANNED", "ACTIVE")]
    typer.echo("")
    if allocatable_only:
        typer.echo("Your projects (PLANNED or ACTIVE only):")
    else:
        typer.echo("Your projects:")
    if not projects:
        display.info("No projects available.")
        return False
    typer.echo(f"{'ID':<5} {'Name':<20} Status")
    display.rule()
    for p in projects:
        typer.echo(f"{p['id']:<5} {p['name']:<20} {p['status']}")
    display.rule()
    return True


def _allocate_direct() -> None:
    typer.echo("")
    display.banner(["DIRECT ALLOCATION"])
    if not _show_projects(allocatable_only=True):
        return
    project_id = typer.prompt("Select Project ID")
    _show_team()
    employee_id = typer.prompt("Enter Employee ID")
    utilization = typer.prompt("Utilisation %")
    try:
        alloc_start = parse_date(
            typer.prompt("From Date (DD-MM-YYYY)"), "From Date"
        )
        alloc_end = parse_date(typer.prompt("To Date (DD-MM-YYYY)"), "To Date")
    except ValueError as exc:
        display.error(str(exc))
        return
    confirm = typer.prompt("[C] Confirm   [B] Back").strip().lower()
    if confirm != "c":
        display.info("Cancelled.")
        return
    try:
        post(
            "/manager/allocations",
            {
                "project_id": int(project_id),
                "employee_id": int(employee_id),
                "utilization_percent": int(utilization),
                "alloc_start": alloc_start.isoformat(),
                "alloc_end": alloc_end.isoformat(),
            },
            auth=True,
        )
    except (ApiError, ValueError) as exc:
        display.error(str(exc))
        return
    display.success("Allocation saved.")


def _end_allocation() -> None:
    typer.echo("")
    display.banner(["END ALLOCATION"])
    _show_projects()
    project_id = typer.prompt("Select Project ID")
    try:
        rows = get(f"/manager/projects/{project_id}/allocations")
    except ApiError as exc:
        display.error(str(exc))
        return
    if not rows:
        display.info("No active allocations on this project.")
        return
    typer.echo("")
    typer.echo(f"{'#':<4} {'Employee':<18} {'%':<6} {'From':<12} To")
    display.rule()
    for idx, row in enumerate(rows, start=1):
        typer.echo(
            f"{idx:<4} {row['employee_name']:<18} {row['utilization_percent']}%{'':<4} "
            f"{format_date(row['alloc_start']):<12} {format_date(row['alloc_end'])}"
        )
    display.rule()
    pick = typer.prompt("Select allocation to end (#)")
    if not pick.isdigit() or int(pick) < 1 or int(pick) > len(rows):
        display.error("Invalid selection.")
        return
    row = rows[int(pick) - 1]
    confirm = typer.prompt(
        f"End {row['employee_name']}'s allocation on {row['project_name']}? [Y/N]"
    ).strip().lower()
    if confirm != "y":
        display.info("Cancelled.")
        return
    try:
        post(f"/manager/allocations/{row['id']}/end", {}, auth=True)
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Allocation ended.")
