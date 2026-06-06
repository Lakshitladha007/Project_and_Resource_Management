import typer

from client import display
from client.api_client import ApiError, post
from client.session import session


def login_screen() -> bool:
    display.header("PRM Tool - Login")
    username = typer.prompt("Username")
    password = display.mask_prompt("Password")

    try:
        data = post("/auth/login", {"username": username, "password": password})
    except ApiError as exc:
        display.error(str(exc))
        return False

    session.set(token=data["access_token"], username=username, role=data["role"])
    display.success(f"Welcome, {username} ({data['role']})")

    if data.get("force_password_change"):
        _change_password_flow(current_password=password)
    return True


def _change_password_flow(current_password: str) -> None:
    typer.echo("")
    display.banner(["CHANGE PASSWORD", "You must set a new password to continue."])
    while True:
        typer.echo("")
        new = display.mask_prompt("New Password    ")
        confirm = display.mask_prompt("Confirm Password")
        display.rule()
        while True:
            action = typer.prompt("[S] Save and Continue   [V] View passwords").strip().lower()
            if action == "v":
                display.info(f"  Current password : {current_password}")
                display.info(f"  New password     : {new}")
                display.info(f"  Confirm password : {confirm}")
                continue
            if action == "s":
                break
            display.error("Invalid option. Choose S or V.")
        if new != confirm:
            display.error("Passwords do not match. Try again.")
            continue
        try:
            post(
                "/auth/change-password",
                {"current_password": current_password, "new_password": new},
                auth=True,
            )
        except ApiError as exc:
            display.error(str(exc))
            continue
        display.success("Password updated. Welcome! \u2713")
        break
