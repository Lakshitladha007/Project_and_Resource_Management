import typer

from client import display
from client.api_client import ApiError, get, post, put


def manage_employees() -> None:
    while True:
        typer.echo("")
        display.banner(["MANAGE EMPLOYEES"])
        display.menu(
            [
                ("1", "View All Employees"),
                ("2", "Update Employee"),
                ("3", "Deactivate Employee"),
                ("4", "Manage Employee Skills"),
                ("5", "Assign Manager"),
                ("6", "Back"),
            ]
        )
        choice = typer.prompt("Enter option").strip()
        if choice == "1":
            _view_employees()
        elif choice == "2":
            _update_employee()
        elif choice == "3":
            _deactivate_employee()
        elif choice == "4":
            display.info("Skills management arrives in the next sub-step.")
        elif choice == "5":
            _assign_manager()
        elif choice == "6":
            return
        else:
            display.error("Invalid option.")


def _view_employees() -> None:
    try:
        employees = get("/admin/employees")
    except ApiError as exc:
        display.error(str(exc))
        return
    typer.echo("")
    display.banner(["ALL EMPLOYEES"])
    typer.echo(f"{'ID':<5} {'Name':<20} {'Department':<14} {'Mgr':<5} Status")
    display.rule()
    for e in employees:
        dept = e["department"] or "-"
        mgr = e["manager_id"] if e["manager_id"] is not None else "-"
        suffix = "" if e["is_active"] else " (inactive)"
        typer.echo(
            f"{e['id']:<5} {e['full_name']:<20} {dept:<14} {str(mgr):<5} "
            f"{e['status']}{suffix}"
        )
    display.rule()
    total = len(employees)
    allocated = sum(1 for e in employees if e["status"] == "ALLOCATED")
    bench = sum(1 for e in employees if e["status"] == "BENCH")
    typer.echo(f"Total: {total}   |   Allocated: {allocated}   |   Bench: {bench}")


def _optional(prompt_text: str) -> str | None:
    value = typer.prompt(prompt_text, default="", show_default=False).strip()
    return value or None


def _update_employee() -> None:
    typer.echo("")
    display.banner(["UPDATE EMPLOYEE"])
    employee_id = typer.prompt("Enter Employee ID")
    typer.echo("Leave a field blank to keep the current value.")
    payload = {
        "full_name": _optional("Full Name"),
        "department": _optional("Department"),
        "designation": _optional("Designation"),
    }
    try:
        put(f"/admin/employees/{employee_id}", payload, auth=True)
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Employee updated.")


def _assign_manager() -> None:
    typer.echo("")
    display.banner(["ASSIGN MANAGER"])
    employee_user_id = typer.prompt("Employee User ID")
    manager_user_id = typer.prompt("Manager User ID")
    try:
        post(
            "/admin/employees/assign-manager",
            {
                "employee_user_id": int(employee_user_id),
                "manager_user_id": int(manager_user_id),
            },
            auth=True,
        )
    except (ApiError, ValueError) as exc:
        display.error(str(exc))
        return
    display.success("Manager assigned.")


def _deactivate_employee() -> None:
    typer.echo("")
    display.banner(["DEACTIVATE EMPLOYEE"])
    employee_id = typer.prompt("Enter Employee ID")
    confirm = typer.prompt("Confirm deactivation? [Y/N]").strip().lower()
    if confirm != "y":
        display.info("Cancelled.")
        return
    try:
        post(f"/admin/employees/{employee_id}/deactivate", {}, auth=True)
    except ApiError as exc:
        display.error(str(exc))
        return
    display.success("Employee deactivated. Their login is now blocked.")
