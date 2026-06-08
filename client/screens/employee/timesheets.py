from datetime import date, timedelta

import typer

from client import display
from client.api_client import ApiError, get, post
from client.validators import format_date, parse_date


def show_reminder() -> None:
    try:
        data = get("/employee/reminder")
    except ApiError:
        return
    if data.get("show_reminder"):
        week = format_date(data["week_start"])
        display.info(
            f"\n  Reminder: Timesheet for week {week} has not been submitted."
        )


def _load_activity_tags() -> list[dict]:
    return get("/employee/activity-tags")


def _show_activity_tags(tags: list[dict]) -> None:
    typer.echo("")
    typer.echo("What did you work on? Select activity tags:")
    typer.echo("")
    for index, tag in enumerate(tags, start=1):
        typer.echo(f"  {index}.  {tag['label']}")
    typer.echo(f"  {len(tags) + 1}.  Other (type manually)")


def _parse_tag_selection(raw: str, tags: list[dict]) -> list[dict]:
    raw = (raw or "").strip()
    if not raw:
        return []
    selected: list[dict] = []
    other_index = len(tags) + 1
    for part in raw.split(","):
        part = part.strip()
        if not part.isdigit():
            raise ValueError(f"Invalid tag selection: {part}")
        choice = int(part)
        if choice == other_index:
            custom = typer.prompt("Describe other activity").strip()
            if not custom:
                raise ValueError("Custom activity tag cannot be empty")
            selected.append({"custom_label": custom})
        elif 1 <= choice <= len(tags):
            selected.append({"activity_tag_id": tags[choice - 1]["id"]})
        else:
            raise ValueError(f"Invalid tag number: {choice}")
    return selected


def submit_timesheet() -> None:
    typer.echo("")
    display.banner(["SUBMIT TIMESHEET"])

    week_input = typer.prompt(
        "Week Start (DD-MM-YYYY, Enter for this week's Monday)",
        default="",
    ).strip()
    params = None
    if week_input:
        try:
            week_start = parse_date(week_input, "Week Start")
        except ValueError as exc:
            display.error(str(exc))
            return
        params = {"week_start": week_start.isoformat()}

    try:
        preview = get("/employee/timesheets/preview", params=params)
        tags = _load_activity_tags()
    except ApiError as exc:
        display.error(str(exc))
        return

    typer.echo("")
    typer.echo(f"Employee  : {preview['employee_name']}")
    typer.echo(f"Week Start: {format_date(preview['week_start'])}")
    typer.echo("")
    display.info("Checking your active allocations for this week...")

    entries_payload: list[dict] = []
    summary_rows: list[tuple[str, int, list[str]]] = []
    total_hours = 0
    max_weekly = preview["max_weekly_hours"]
    projects = preview["projects"]
    tag_labels_by_id = {tag["id"]: tag["label"] for tag in tags}

    for index, project in enumerate(projects, start=1):
        typer.echo("")
        display.rule()
        typer.echo(
            f"PROJECT {index} OF {len(projects)} — {project['project_name']}"
        )
        typer.echo(
            f"  Allocation: {project['utilization_percent']}%   |   "
            f"Expected: {project['max_hours']} hrs max"
        )
        display.rule()

        while True:
            hours_raw = typer.prompt("Hours worked this week").strip()
            if not hours_raw.isdigit():
                display.error("Enter a whole number of hours.")
                continue
            hours = int(hours_raw)
            if hours > project["max_hours"]:
                display.error(
                    f"Hours cannot exceed {project['max_hours']} for this project."
                )
                continue
            break

        entry_tags: list[dict] = []
        tag_names: list[str] = []
        if hours > 0:
            _show_activity_tags(tags)
            while True:
                raw = typer.prompt("Select tags (comma-separated)")
                try:
                    entry_tags = _parse_tag_selection(raw, tags)
                except ValueError as exc:
                    display.error(str(exc))
                    continue
                if not entry_tags:
                    display.error("Select at least one tag when hours > 0.")
                    continue
                for tag in entry_tags:
                    if tag.get("custom_label"):
                        tag_names.append(tag["custom_label"])
                    else:
                        tag_names.append(
                            tag_labels_by_id[tag["activity_tag_id"]]
                        )
                break

        entries_payload.append(
            {
                "project_id": project["project_id"],
                "hours": hours,
                "tags": entry_tags,
            }
        )
        summary_rows.append((project["project_name"], hours, tag_names))
        total_hours += hours

    typer.echo("")
    display.rule()
    typer.echo("SUMMARY")
    for name, hours, tag_names in summary_rows:
        tags_text = ", ".join(tag_names) if tag_names else "-"
        typer.echo(f"  {name:<16} {hours:>3} hrs    [{tags_text}]")
    typer.echo("  " + "─" * 41)
    status = "✓" if total_hours <= max_weekly else "!"
    typer.echo(
        f"  Total           {total_hours:>3} hrs / {max_weekly} hrs max   {status}"
    )
    display.rule()

    action = typer.prompt("[S] Submit Timesheet     [B] Back").strip().lower()
    if action != "s":
        return

    try:
        result = post(
            "/employee/timesheets",
            {
                "week_start": preview["week_start"],
                "entries": entries_payload,
            },
            auth=True,
        )
    except ApiError as exc:
        display.error(str(exc))
        return

    display.success(
        f"Timesheet submitted successfully. Status: {result['status']} ✓"
    )


def view_my_timesheets() -> None:
    typer.echo("")
    display.banner(["MY TIMESHEETS"])
    try:
        rows = get("/employee/timesheets")
    except ApiError as exc:
        display.error(str(exc))
        return

    if not rows:
        display.info("No timesheet history yet.")
        typer.echo("")
        typer.prompt("[B] Back", default="b")
        return

    typer.echo("")
    typer.echo(f"{'Week Start':<14} {'Total Hrs':<12} Status")
    display.rule()
    for row in rows:
        hours_label = f"{row['total_hours']} hrs"
        suffix = "    ⚠" if row["status"] == "MISSED" else ""
        typer.echo(
            f"{format_date(row['week_start']):<14} "
            f"{hours_label:<12} "
            f"{row['status']}{suffix}"
        )
    display.rule()

    action = typer.prompt("[V] View week details     [B] Back").strip().lower()
    if action != "v":
        return

    week_input = typer.prompt("Enter week start (DD-MM-YYYY)").strip()
    try:
        week_start = parse_date(week_input, "Week Start")
    except ValueError as exc:
        display.error(str(exc))
        return

    try:
        detail = get(f"/employee/timesheets/{week_start.isoformat()}")
    except ApiError as exc:
        display.error(str(exc))
        return

    typer.echo("")
    typer.echo(
        f"── Week: {format_date(detail['week_start'])} — "
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
