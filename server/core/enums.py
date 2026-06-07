from enum import Enum


class Role(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class EmployeeStatus(str, Enum):
    BENCH = "BENCH"
    ALLOCATED = "ALLOCATED"


class SkillCategory(str, Enum):
    BACKEND = "BACKEND"
    FRONTEND = "FRONTEND"
    DEVOPS = "DEVOPS"
    QA = "QA"
    OTHER = "OTHER"


class ProficiencyLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class LLMProvider(str, Enum):
    GEMINI = "GEMINI"
    GROQ = "GROQ"
