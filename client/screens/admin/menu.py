import typer

from client import display
from client.screens.admin import allocations as allocations_screen
from client.screens.admin import employees as employees_screen
from client.screens.admin import projects as projects_screen
from client.screens.admin import users as users_screen
from client.session import session

COMING_SOON = {"5"}


def admin_menu() -> None:
    while True:
        typer.echo("")
        display.banner(["ADMIN PANEL", f"Welcome, {session.username}"])
        display.menu(
            [
                ("1", "Manage Employees"),
                ("2", "Manage Projects"),
                ("3", "View All Allocations"),
                ("4", "Manage Users"),
                ("5", "System Configuration"),
                ("6", "Logout"),
            ]
        )
        choice = typer.prompt("Enter option").strip()
        if choice == "1":
            employees_screen.manage_employees()
        elif choice == "2":
            projects_screen.manage_projects()
        elif choice == "3":
            allocations_screen.view_allocations()
        elif choice == "4":
            users_screen.manage_users()
        elif choice == "6":
            session.clear()
            display.info("Logged out.")
            return
        elif choice in COMING_SOON:
            display.info("This section arrives in a later feature.")
        else:
            display.error("Invalid option.")
