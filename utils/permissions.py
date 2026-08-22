from utils.constants import UserRole


ROLE_PERMISSIONS = {

    UserRole.SUPER_ADMIN.value: [
        "Dashboard",
        "Guards",
        "Sites",
        "Payments",
        "Shifts",
        "Attendance",
        "Incidents",
        "Users",
        "Reports",
        "Settings",
        "Company Settings"
    ],

    UserRole.ADMIN_MANAGER.value: [
        "Dashboard",
        "Guards",
        "Sites",
        "Shifts",
        "Attendance",
        "Incidents",
        "Reports"
    ],

    UserRole.SUPERVISOR.value: [
        "Dashboard",
        "Guards",
        "Sites",
        "Shifts",
        "Attendance",
        "Incidents"
    ],

    UserRole.SECURITY_GUARD.value: [
        "Dashboard",
        "My Shift",
        "Check In / Out",
        "Incidents"
    ],

    UserRole.CLIENT.value: [
        "Dashboard",
        "Guards",
        "Reports"
    ]
}


def get_allowed_pages(role: str) -> list:

    return ROLE_PERMISSIONS.get(
        role,
        []
    )


def has_permission(
    role: str,
    page: str
) -> bool:

    return page in get_allowed_pages(role)