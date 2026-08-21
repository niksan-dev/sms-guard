from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "Admin"
    ADMIN_MANAGER = "Manager"
    SUPERVISOR = "Supervisor"
    SECURITY_GUARD = "Guard"
    CLIENT = "Client"


class GuardStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ON_LEAVE = "On Leave"
    RESIGNED = "Resigned"


class IncidentStatus(str, Enum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    CLOSED = "Closed"