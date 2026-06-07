import typer

from client import display
from client.api_client import ApiError, get
from client.validators import format_date


def view_allocations() -> None:
    employee_filter = None
    project_filter = None
    while True:
        params = {}
        if employee_filter is not None:
            params["employee_id"] = employee_filter
        if project_filter is not None:
            params["project_id"] = project_filter
        try:
            rows = get("/admin/allocations", auth=True, params=params or None)
        except ApiError as exc:
            display.error(str(exc))
            return

        typer.echo("")
        display.banner(["ALL ALLOCATIONS"])
        typer.echo(
            f"{'Employee':<18} {'Project':<18} {'%':<6} {'From':<12} To"
        )
        display.rule()
        if rows:
            for row in rows:
                typer.echo(
                    f"{row['employee_name']:<18} {row['project_name']:<18} "
                    f"{row['utilization_percent']}%{'':<4} "
                    f"{format_date(row['alloc_start']):<12} "
                    f"{format_date(row['alloc_end'])}"
                )
        else:
            typer.echo("  (no active allocations)")
        display.rule()
        typer.echo(f"Total Active Allocations: {len(rows)}")
        typer.echo("")
        action = typer.prompt("[F] Filter by Employee/Project   [B] Back").strip().lower()
        if action == "b":
            return
        if action == "f":
            typer.echo("Leave blank to clear a filter.")
            emp = typer.prompt("Employee ID", default="", show_default=False).strip()
            proj = typer.prompt("Project ID", default="", show_default=False).strip()
            employee_filter = int(emp) if emp else None
            project_filter = int(proj) if proj else None
        else:
            display.error("Invalid option. Use F or B.")
