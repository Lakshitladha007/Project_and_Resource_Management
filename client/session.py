class Session:
    """Holds the JWT token and current user in memory for the CLI session."""

    def __init__(self) -> None:
        self.token: str | None = None
        self.username: str | None = None
        self.role: str | None = None

    def set(self, token: str, username: str, role: str) -> None:
        self.token = token
        self.username = username
        self.role = role

    def clear(self) -> None:
        self.token = None
        self.username = None
        self.role = None


session = Session()
