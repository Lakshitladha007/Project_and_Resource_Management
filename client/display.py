import sys

import typer

try:
    import msvcrt
except ImportError:
    msvcrt = None

WIDTH = 50


def banner(lines: list[str]) -> None:
    inner = max(len(line) for line in lines) + 6
    typer.echo("\u2554" + "\u2550" * inner + "\u2557")
    for line in lines:
        typer.echo("\u2551" + ("   " + line).ljust(inner) + "\u2551")
    typer.echo("\u255a" + "\u2550" * inner + "\u255d")


def header(title: str) -> None:
    typer.echo("=" * WIDTH)
    typer.echo(title.center(WIDTH))
    typer.echo("=" * WIDTH)


def menu(options: list[tuple[str, str]]) -> None:
    typer.echo("")
    for key, label in options:
        typer.echo(f"{key}. {label}")
    typer.echo("")


def rule() -> None:
    typer.echo("_" * WIDTH)


def mask_prompt(label: str) -> str:
    """Prompt for hidden input, echoing '*' per character typed."""
    sys.stdout.write(f"{label}: ")
    sys.stdout.flush()

    if msvcrt is None:
        import getpass

        return getpass.getpass("")

    chars: list[str] = []
    while True:
        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            break
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch in ("\x00", "\xe0"):
            msvcrt.getwch()
            continue
        if ch in ("\b", "\x7f"):
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue
        chars.append(ch)
        sys.stdout.write("*")
        sys.stdout.flush()
    return "".join(chars)


def info(message: str) -> None:
    typer.echo(message)


def error(message: str) -> None:
    typer.secho(f"Error: {message}", fg=typer.colors.RED)


def success(message: str) -> None:
    typer.secho(message, fg=typer.colors.GREEN)
