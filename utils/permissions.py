from utils.constants import UserRole


ROLE_PERMISSIONS = {

    # ============================================================
    # SUPER ADMIN
    # ============================================================
    UserRole.SUPER_ADMIN.value: [
        "Dashboard",
        "Guards",
        "Sites",
        "Guard Work",
        "Billing & Payroll",
        "Company Settings",
    ],

    # ============================================================
    # ADMIN / MANAGER
    # ============================================================
    UserRole.ADMIN_MANAGER.value: [
        "Dashboard",
        "Guards",
        "Sites",
        "Guard Work",
    ],

    # ============================================================
    # SUPERVISOR
    # ============================================================
    UserRole.SUPERVISOR.value: [
        "Dashboard",
        "Guards",
        "Sites",
        "Guard Work",
    ],

    # ============================================================
    # SECURITY GUARD
    # ============================================================
    UserRole.SECURITY_GUARD.value: [
        "Dashboard",
        "My Shift",
    ],

    # ============================================================
    # CLIENT
    # ============================================================
    UserRole.CLIENT.value: [
        "Dashboard",
        "Guards",
        "Reports",
    ],
}


def normalize_role(role: str) -> str:
    """
    Normalize role values coming from the database/session.

    The application stores the Super Admin role as 'Admin',
    but older code or sessions may contain 'Super Admin'.
    """

    if role is None:
        return ""

    # Handle Enum values
    if isinstance(role, UserRole):
        role = role.value

    role = str(role).strip()

    # Backward compatibility
    if role == "Super Admin":
        return UserRole.SUPER_ADMIN.value

    return role


def get_allowed_pages(role: str) -> list:
    """
    Return pages available to the supplied role.
    """

    normalized_role = normalize_role(role)

    return ROLE_PERMISSIONS.get(
        normalized_role,
        []
    )


def has_permission(
    role: str,
    page: str
) -> bool:
    """
    Check whether a role has access to a specific page.
    """

    return page in get_allowed_pages(role)