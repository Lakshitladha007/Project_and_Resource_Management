import typer

from client import display
from client.screens.manager import allocations as allocations_screen
from client.session import session

COMING_SOON = {"1", "3", "4", "5"}


def manager_menu() -> None:
    while True:
        typer.echo("")
        display.banner(["MANAGER PANEL", f"Welcome, {session.username}"])
        display.menu(
            [
                ("1", "Resource Dashboard"),
                ("2", "Allocate Resource"),
                ("3", "My Projects"),
                ("4", "Timesheets"),
                ("5", "AI Assistant"),
                ("6", "Logout"),
            ]
        )
        choice = typer.prompt("Enter option").strip()
        if choice == "2":
            allocations_screen.allocate_resource()
        elif choice == "6":
            session.clear()
            display.info("Logged out.")
            return
        elif choice in COMING_SOON:
            display.info("This section arrives in a later feature.")
        else:
            display.error("Invalid option.")
