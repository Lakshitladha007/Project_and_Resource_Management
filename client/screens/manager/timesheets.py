import typer

from client import display
from client.api_client import ApiError, get
from client.validators import format_date, parse_date


def view_team_timesheets() -> None:
    typer.echo("")
    display.banner(["TIMESHEETS — MY TEAM"])

    week_input = typer.prompt(
        "Filter by week (DD-MM-YYYY) or press Enter for current week",
        default="",
    ).strip()
    params = None
    if week_input:
        try:
            week_start = parse_date(week_input, "Week")
        except ValueError as exc:
            display.error(str(exc))
            return
        params = {"week_start": week_start.isoformat()}

    try:
        data = get("/manager/timesheets", params=params)
    except ApiError as exc:
        display.error(str(exc))
        return

    typer.echo("")
    typer.echo(f"Week: {format_date(data['week_start'])}")
    rows = data.get("rows") or []
    if not rows:
        display.info("No team timesheet activity for this week.")
        typer.echo("")
        typer.prompt("[B] Back", default="b")
        return

    typer.echo("")
    typer.echo(f"{'Employee':<18} {'Project':<16} {'Hrs':<6} Status")
    display.rule()
    for row in rows:
        suffix = " ⚠" if row["status"] == "MISSED" else ""
        typer.echo(
            f"{row['employee_name']:<18} "
            f"{row['project_name']:<16} "
            f"{row['hours']:<6} "
            f"{row['status']}{suffix}"
        )
    display.rule()

    action = typer.prompt("[V] View employee timesheet detail     [B] Back").strip().lower()
    if action != "v":
        return

    employee_id_raw = typer.prompt("Enter employee ID from your team").strip()
    if not employee_id_raw.isdigit():
        display.error("Enter a valid employee ID.")
        return
    employee_id = int(employee_id_raw)

    detail_params = {"week_start": data["week_start"]}
    try:
        detail = get(
            f"/manager/timesheets/employees/{employee_id}",
            params=detail_params,
        )
    except ApiError as exc:
        display.error(str(exc))
        return

    typer.echo("")
    typer.echo(
        f"── {detail['employee_name']} — Week: {format_date(detail['week_start'])} — "
        f"Status: {detail['status']} ─────"
    )
    typer.echo("")
    typer.echo(f"{'Project':<16} {'Hrs':<6} Activity Tags")
    display.rule()
    for entry in detail["entries"]:
        tags_text = ", ".join(entry["activity_tags"]) or "-"
        typer.echo(
            f"{entry['project_name']:<16} {entry['hours']:<6} {tags_text}"
        )
    display.rule()
    typer.echo(f"Total: {detail['total_hours']} hrs")
    typer.echo("")
    typer.prompt("[B] Back", default="b")
