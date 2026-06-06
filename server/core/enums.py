from enum import Enum


class Role(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class LLMProvider(str, Enum):
    GEMINI = "GEMINI"
    GROQ = "GROQ"
