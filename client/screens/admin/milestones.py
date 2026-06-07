import typer

from client import display
from client.api_client import ApiError, get, post, put
from client.validators import format_date, parse_date

STATUS_LABEL = {
    "NOT_STARTED": "NOT_STARTED",
    "IN_PROGRESS": "IN_PROGRESS",
    "DONE": "DONE",
}
UPDATE_STATUS_MAP = {"1": "NOT_STARTED", "2": "IN_PROGRESS", "3": "DONE"}


def manage_milestones() -> None:
    typer.echo("")
    display.banner(["MILESTONES"])
    project_id = typer.prompt("Enter Project ID")
    try:
        data = get(f"/admin/projects/{project_id}/milestones")
    except ApiError as exc:
        display.error(str(exc))
        return

    while True:
        try:
            data = get(f"/admin/projects/{project_id}/milestones")
        except ApiError as exc:
            display.error(str(exc))
            return

        typer.echo("")
        display.banner(["MILESTONES"])
        typer.echo(f"-- {data['project_name']} " + "-" * 30)
        typer.echo(f"{'#':<4} {'Title':<20} {'Due Date':<12} {'Story Pts':<10} Status")
        display.rule()
        milestones = data["milestones"]
        for idx, m in enumerate(milestones, start=1):
            typer.echo(
                f"{idx:<4} {m['title']:<20} {format_date(m['due_date']):<12} "
                f"{m['story_points']:<10} {STATUS_LABEL.get(m['status'], m['status'])}"
            )
        display.rule()
        typer.echo(
            f"Total: {data['total_story_points']} SP   |   "
            f"Completed: {data['completed_story_points']} SP   |   "
            f"Remaining: {data['remaining_story_points']} SP"
        )
        display.menu(
            [
                ("1", "Add Milestone"),
                ("2", "Update Milestone Status"),
                ("3", "Back"),
            ]
        )
        choice = typer.prompt("Enter option").strip()
        if choice == "1":
            _add_milestone(project_id)
        elif choice == "2":
            _update_status(project_id, milestones)
        elif choice == "3":
            return
        else:
            display.error("Invalid option.")


def _add_milestone(project_id: str) -> None:
    title = typer.prompt("Milestone Title")
    try:
        due_date = parse_date(typer.prompt("Due Date (DD-MM-YYYY)"), "Due Date")
        story_points = int(typer.prompt("Story Points"))
    except (ValueError, TypeError) as exc:
        display.error(str(exc))
        return
    try:
        post(
            f"/admin/projects/{project_id}/milestones",
            {
                "title": title,
                "due_date": due_date.isoformat(),
                "story_points": story_points,
            },
            auth=True,
        )
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Milestone added.")


def _update_status(project_id: str, milestones: list) -> None:
    if not milestones:
        display.error("No milestones to update.")
        return
    pick = typer.prompt("Enter Milestone #")
    if not pick.isdigit() or int(pick) < 1 or int(pick) > len(milestones):
        display.error("Invalid milestone number.")
        return
    milestone = milestones[int(pick) - 1]
    status_choice = typer.prompt(
        "New Status (1) NOT_STARTED (2) IN_PROGRESS (3) DONE"
    ).strip()
    status = UPDATE_STATUS_MAP.get(status_choice)
    if status is None:
        display.error("Invalid status selection.")
        return
    try:
        put(
            f"/admin/projects/{project_id}/milestones/{milestone['id']}",
            {"status": status},
            auth=True,
        )
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Milestone updated.")
