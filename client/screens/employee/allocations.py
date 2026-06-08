import typer

from client import display
from client.api_client import ApiError, get
from client.validators import format_date


def view_my_allocations() -> None:
    typer.echo("")
    display.banner(["MY ALLOCATIONS"])
    try:
        data = get("/employee/allocations")
    except ApiError as exc:
        display.error(str(exc))
        return

    rows = data.get("allocations") or []
    if not rows:
        display.info("No active allocations.")
        typer.echo("")
        typer.prompt("[B] Back", default="b")
        return

    typer.echo("")
    typer.echo(f"{'Project':<18} {'%':<6} {'From':<12} {'To':<12} Status")
    display.rule()
    for row in rows:
        typer.echo(
            f"{row['project_name']:<18} "
            f"{row['utilization_percent']}%{'':<4} "
            f"{format_date(row['alloc_start']):<12} "
            f"{format_date(row['alloc_end']):<12} "
            f"{row['status']}"
        )
    display.rule()
    typer.echo(f"Total Utilisation: {data['total_utilization']}%")
    typer.echo("")
    typer.prompt("[B] Back", default="b")
