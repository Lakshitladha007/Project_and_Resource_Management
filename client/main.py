import typer

from client import display
from client.screens.admin.menu import admin_menu
from client.screens.login import login_screen
from client.session import session

TITLE_LINES = [
    "PROJECT & RESOURCE MANAGEMENT TOOL",
    "Learn & Code - Final Project",
]


def run() -> None:
    """Launch the PRM console client with the welcome menu."""
    while True:
        display.banner(TITLE_LINES)
        display.menu([("1", "Login"), ("2", "Exit")])
        choice = typer.prompt("Enter option").strip()

        if choice == "1":
            if login_screen():
                _route_after_login()
                return
        elif choice == "2":
            display.info("Goodbye.")
            return
        else:
            display.error("Invalid option. Please choose 1 or 2.\n")


def _route_after_login() -> None:
    if session.role == "ADMIN":
        admin_menu()
    else:
        display.info(f"\n{session.role} menu is coming in a later feature.")


if __name__ == "__main__":
    run()
