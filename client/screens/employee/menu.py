import typer

from client import display
from client.screens.employee import allocations as allocations_screen
from client.screens.employee import timesheets as timesheets_screen
from client.session import session


def employee_menu() -> None:
    while True:
        typer.echo("")
        display.banner(["EMPLOYEE PANEL", f"Welcome, {session.username}"])
        timesheets_screen.show_reminder()
        display.menu(
            [
                ("1", "Submit Timesheet"),
                ("2", "View My Timesheets"),
                ("3", "View My Allocations"),
                ("4", "Logout"),
            ]
        )
        choice = typer.prompt("Enter option").strip()
        if choice == "1":
            timesheets_screen.submit_timesheet()
        elif choice == "2":
            timesheets_screen.view_my_timesheets()
        elif choice == "3":
            allocations_screen.view_my_allocations()
        elif choice == "4":
            session.clear()
            display.info("Logged out.")
            return
        else:
            display.error("Invalid option.")
