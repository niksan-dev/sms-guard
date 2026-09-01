"""
Monthly Salary Master Service

Builds a monthly payroll master with one row per guard.

Data sources:
    Guard
    GuardDailyWork
    GuardAdvance

Rules:
    Shift 1:
        Present records with shift_number = 1

    Shift 2:
        Present records with shift_number = 2

    Total Shifts:
        Shift 1 + Shift 2

    Earned:
        Total Shifts × (monthly_salary / calendar_days)

    Advances:
        GuardAdvance records for the selected month,
        grouped by category

    Net Payable:
        Earned - Total Advances
"""

from __future__ import annotations

import calendar
from datetime import date
from typing import Any

from sqlalchemy import extract

from database.connection import SessionLocal
from database.models import (
    Guard,
    GuardDailyWork,
    GuardAdvance,
)


# ============================================================
# HELPERS
# ============================================================

def _number(value: Any) -> float:
    """Safely convert a value to float."""

    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _month_start(year: int, month: int) -> date:
    return date(
        int(year),
        int(month),
        1
    )


def _calendar_days(year: int, month: int) -> int:
    return calendar.monthrange(
        int(year),
        int(month)
    )[1]


# ============================================================
# GET ADVANCE CATEGORIES
# ============================================================

def get_monthly_advance_categories(
    year: int,
    month: int
) -> list[str]:

    db = SessionLocal()

    try:

        rows = (
            db.query(
                GuardAdvance.category
            )
            .filter(
                extract(
                    "year",
                    GuardAdvance.record_date
                ) == int(year),

                extract(
                    "month",
                    GuardAdvance.record_date
                ) == int(month)
            )
            .distinct()
            .order_by(
                GuardAdvance.category.asc()
            )
            .all()
        )

        categories = []

        for row in rows:

            category = (
                row[0]
                if row
                else None
            )

            if category:

                category = str(
                    category
                ).strip()

                if category:
                    categories.append(
                        category
                    )

        return categories

    finally:
        db.close()


# ============================================================
# BUILD MONTHLY SALARY MASTER
# ============================================================

def get_monthly_salary_master(
    year: int,
    month: int,
    include_inactive: bool = False
) -> dict[str, Any]:
    """
    Build the complete monthly salary master.

    Returns:

        {
            "year": 2026,
            "month": 8,
            "month_name": "AUGUST 2026",
            "calendar_days": 31,
            "advance_categories": [...],
            "rows": [...],
            "totals": {...}
        }
    """

    year = int(year)
    month = int(month)

    if month < 1 or month > 12:
        raise ValueError(
            "Month must be between 1 and 12."
        )

    db = SessionLocal()

    try:

        # ====================================================
        # CALENDAR
        # ====================================================

        calendar_days = _calendar_days(
            year,
            month
        )

        month_start = _month_start(
            year,
            month
        )

        # ====================================================
        # GET GUARDS
        # ====================================================

        guard_query = (
            db.query(Guard)
        )

        if not include_inactive:

            guard_query = guard_query.filter(
                Guard.status == "Active"
            )

        guards = (
            guard_query
            .order_by(
                Guard.employee_id.asc(),
                Guard.name.asc()
            )
            .all()
        )

        # ====================================================
        # GET DAILY WORK
        # ====================================================

        work_records = (
            db.query(
                GuardDailyWork
            )
            .filter(

                extract(
                    "year",
                    GuardDailyWork.work_date
                ) == year,

                extract(
                    "month",
                    GuardDailyWork.work_date
                ) == month
            )
            .all()
        )

        # ====================================================
        # GET ADVANCES
        # ====================================================

        advance_records = (
            db.query(
                GuardAdvance
            )
            .filter(

                extract(
                    "year",
                    GuardAdvance.record_date
                ) == year,

                extract(
                    "month",
                    GuardAdvance.record_date
                ) == month
            )
            .all()
        )

        # ====================================================
        # GROUP WORK BY GUARD
        # ====================================================

        work_by_guard: dict[
            int,
            list[Any]
        ] = {}

        for record in work_records:

            guard_id = int(
                record.guard_id
            )

            work_by_guard.setdefault(
                guard_id,
                []
            ).append(record)

        # ====================================================
        # GROUP ADVANCES BY GUARD
        # ====================================================

        advances_by_guard: dict[
            int,
            list[Any]
        ] = {}

        for advance in advance_records:

            guard_id = int(
                advance.guard_id
            )

            advances_by_guard.setdefault(
                guard_id,
                []
            ).append(advance)

        # ====================================================
        # DISCOVER ALL ADVANCE CATEGORIES
        # ====================================================

        advance_categories_set: set[str] = set()

        for advance in advance_records:

            category = (
                str(
                    advance.category
                ).strip()
                if advance.category
                else "Other"
            )

            advance_categories_set.add(
                category
            )

        advance_categories = sorted(
            advance_categories_set
        )

        # ====================================================
        # BUILD GUARD ROWS
        # ====================================================

        rows: list[dict[str, Any]] = []

        # ====================================================
        # TOTALS
        # ====================================================

        total_shift_1 = 0
        total_shift_2 = 0
        total_shifts = 0

        total_earned = 0.0
        total_advances = 0.0
        total_net_payable = 0.0

        category_totals: dict[
            str,
            float
        ] = {
            category: 0.0
            for category
            in advance_categories
        }

        # ====================================================
        # PROCESS EACH GUARD
        # ====================================================

        for guard in guards:

            guard_id = guard.id

            guard_name = (
                guard.name or ""
            )

            employee_id = (
                guard.employee_id or ""
            )

            monthly_salary = _number(
                guard.monthly_salary
            )

            # -----------------------------------------------
            # DAILY WORK
            # -----------------------------------------------

            guard_work = (
                work_by_guard.get(
                    guard_id,
                    []
                )
            )

            shift_1_count = 0
            shift_2_count = 0

            # -----------------------------------------------
            # Count PRESENT shifts only.
            #
            # shift_number = 1 -> Shift 1
            # shift_number = 2 -> Shift 2
            # -----------------------------------------------

            for record in guard_work:

                status = (
                    str(
                        record.status
                    ).strip().lower()
                    if record.status
                    else ""
                )

                # Only Present counts toward salary.
                if status != "present":
                    continue

                shift_number = int(
                    record.shift_number or 0
                )

                if shift_number == 1:

                    shift_1_count += 1

                elif shift_number == 2:

                    shift_2_count += 1

            total_guard_shifts = (
                shift_1_count
                + shift_2_count
            )

            # -----------------------------------------------
            # EARNED
            #
            # Monthly salary is divided by the actual
            # calendar days in that month.
            #
            # Each worked shift earns one daily rate.
            # -----------------------------------------------

            daily_rate = (
                monthly_salary
                / calendar_days
                if calendar_days > 0
                else 0.0
            )

            earned = round(
                daily_rate
                * total_guard_shifts,
                2
            )

            # -----------------------------------------------
            # ADVANCES
            # -----------------------------------------------

            guard_advances = (
                advances_by_guard.get(
                    guard_id,
                    []
                )
            )

            advance_values: dict[
                str,
                float
            ] = {
                category: 0.0
                for category
                in advance_categories
            }

            for advance in guard_advances:

                category = (
                    str(
                        advance.category
                    ).strip()
                    if advance.category
                    else "Other"
                )

                amount = _number(
                    advance.amount
                )

                # In case a category appeared after
                # the initial category discovery.
                if category not in advance_values:

                    advance_values[
                        category
                    ] = 0.0

                advance_values[
                    category
                ] += amount

                category_totals[
                    category
                ] = (
                    category_totals.get(
                        category,
                        0.0
                    )
                    + amount
                )

            # -----------------------------------------------
            # TOTAL ADVANCES
            # -----------------------------------------------

            advance_total = round(
                sum(
                    advance_values.values()
                ),
                2
            )

            # -----------------------------------------------
            # NET PAYABLE
            # -----------------------------------------------

            net_payable = round(
                earned
                - advance_total,
                2
            )

            # -----------------------------------------------
            # ROW
            # -----------------------------------------------

            row = {

                "guard_id": guard_id,

                "employee_id": employee_id,

                "guard_name": guard_name,

                "monthly_salary": round(
                    monthly_salary,
                    2
                ),

                "shift_1": shift_1_count,

                "shift_2": shift_2_count,

                "total_shifts": (
                    total_guard_shifts
                ),

                "daily_rate": round(
                    daily_rate,
                    2
                ),

                "earned": earned,

                "advance_total": (
                    advance_total
                ),

                "net_payable": (
                    net_payable
                ),

                "advance_categories": (
                    advance_values
                )
            }

            # -----------------------------------------------
            # ALSO PUT CATEGORY VALUES DIRECTLY IN ROW
            #
            # Makes the row easier to use with
            # Streamlit / pandas / Excel later.
            # -----------------------------------------------

            for category in advance_categories:

                row[
                    f"advance_{category}"
                ] = round(
                    advance_values.get(
                        category,
                        0.0
                    ),
                    2
                )

            rows.append(row)

            # -----------------------------------------------
            # MASTER TOTALS
            # -----------------------------------------------

            total_shift_1 += (
                shift_1_count
            )

            total_shift_2 += (
                shift_2_count
            )

            total_shifts += (
                total_guard_shifts
            )

            total_earned += earned

            total_advances += (
                advance_total
            )

            total_net_payable += (
                net_payable
            )

        # ====================================================
        # ROUND MASTER TOTALS
        # ====================================================

        total_earned = round(
            total_earned,
            2
        )

        total_advances = round(
            total_advances,
            2
        )

        total_net_payable = round(
            total_net_payable,
            2
        )

        category_totals = {
            category: round(
                amount,
                2
            )
            for category, amount
            in category_totals.items()
        }

        # ====================================================
        # RETURN MASTER
        # ====================================================

        return {

            "year": year,

            "month": month,

            "month_name": date(
                year,
                month,
                1
            ).strftime(
                "%B %Y"
            ),

            "calendar_days": (
                calendar_days
            ),

            "month_start": (
                month_start
            ),

            "guard_count": len(
                rows
            ),

            "advance_categories": (
                advance_categories
            ),

            "rows": rows,

            "totals": {

                "shift_1": (
                    total_shift_1
                ),

                "shift_2": (
                    total_shift_2
                ),

                "total_shifts": (
                    total_shifts
                ),

                "earned": (
                    total_earned
                ),

                "advances": (
                    total_advances
                ),

                "net_payable": (
                    total_net_payable
                ),

                "advance_categories": (
                    category_totals
                )
            }
        }

    finally:

        db.close()


# ============================================================
# SIMPLE HELPER
# ============================================================

def get_monthly_salary_rows(
    year: int,
    month: int,
    include_inactive: bool = False
) -> list[dict[str, Any]]:
    """
    Convenience function when only the rows are required.
    """

    master = get_monthly_salary_master(
        year=year,
        month=month,
        include_inactive=include_inactive
    )

    return master["rows"]