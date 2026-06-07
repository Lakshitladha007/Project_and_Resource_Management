import typer

from client import display
from client.api_client import ApiError, get, post

ROLE_MAP = {"1": "ADMIN", "2": "MANAGER", "3": "EMPLOYEE"}


def manage_users() -> None:
    while True:
        typer.echo("")
        display.banner(["MANAGE USERS"])
        display.menu(
            [
                ("1", "Create User Account"),
                ("2", "View All Users"),
                ("3", "Reset User Password"),
                ("4", "Deactivate User"),
                ("5", "Reactivate User"),
                ("6", "Back"),
            ]
        )
        choice = typer.prompt("Enter option").strip()
        if choice == "1":
            _create_user()
        elif choice == "2":
            _view_users()
        elif choice == "3":
            _reset_password()
        elif choice == "4":
            _set_active(activate=False)
        elif choice == "5":
            _set_active(activate=True)
        elif choice == "6":
            return
        else:
            display.error("Invalid option.")


def _create_user() -> None:
    typer.echo("")
    display.banner(["CREATE USER ACCOUNT"])
    full_name = typer.prompt("Full Name")
    email = typer.prompt("Email")
    username = typer.prompt("Username")
    temp_password = typer.prompt("Temporary Password")
    role_choice = typer.prompt("Role (1) Admin (2) Manager (3) Employee").strip()
    role = ROLE_MAP.get(role_choice)
    if role is None:
        display.error("Invalid role selection.")
        return
    try:
        post(
            "/admin/users",
            {
                "full_name": full_name,
                "email": email,
                "username": username,
                "temporary_password": temp_password,
                "role": role,
            },
            auth=True,
        )
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Account created. User must change password on first login.")


def _view_users() -> None:
    try:
        users = get("/admin/users")
    except ApiError as exc:
        display.error(str(exc))
        return
    typer.echo("")
    display.banner(["ALL USERS"])
    typer.echo(f"{'ID':<5} {'Username':<18} {'Role':<10} Status")
    display.rule()
    for u in users:
        status = "Active" if u["is_active"] else "Inactive"
        typer.echo(f"{u['id']:<5} {u['username']:<18} {u['role']:<10} {status}")
    display.rule()
    total = len(users)
    active = sum(1 for u in users if u["is_active"])
    typer.echo(f"Total: {total}   |   Active: {active}   |   Inactive: {total - active}")


def _reset_password() -> None:
    identifier = typer.prompt("Enter Username or User ID")
    new_pw = typer.prompt("New Temporary Password")
    try:
        post(
            f"/admin/users/{identifier}/reset-password",
            {"new_temporary_password": new_pw},
            auth=True,
        )
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Password reset. User will change it on next login.")


def _set_active(activate: bool) -> None:
    action = "reactivate" if activate else "deactivate"
    identifier = typer.prompt(f"Enter Username or User ID to {action}")
    confirm = typer.prompt(f"Confirm {action}? [Y/N]").strip().lower()
    if confirm != "y":
        display.info("Cancelled.")
        return
    try:
        post(f"/admin/users/{identifier}/{action}", {}, auth=True)
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success(f"User {action}d.")
