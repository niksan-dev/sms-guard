from sqlalchemy.orm import joinedload
from sqlalchemy import extract, func

from database.connection import SessionLocal
from database.guard_advance import GuardAdvance


# ==================================================
# CREATE GUARD ADVANCE
# ==================================================

def create_guard_advance(
    guard_id,
    category,
    amount,
    record_date,
    description=None
):

    db = SessionLocal()

    try:

        # ------------------------------------------
        # VALIDATE AMOUNT
        # ------------------------------------------

        amount = float(amount or 0)

        if amount <= 0:

            return (
                False,
                "Advance amount must be greater than zero."
            )

        # ------------------------------------------
        # VALIDATE CATEGORY
        # ------------------------------------------

        category = (
            str(category or "Other")
            .strip()
        )

        if not category:

            category = "Other"

        # ------------------------------------------
        # CREATE ADVANCE
        # ------------------------------------------

        advance = GuardAdvance(

            guard_id=int(guard_id),

            category=category,

            amount=amount,

            record_date=record_date,

            description=(
                str(description).strip()
                if description
                else None
            )
        )

        db.add(advance)

        db.commit()

        return (
            True,
            "Guard advance recorded successfully."
        )

    except Exception as e:

        db.rollback()

        return (
            False,
            f"Unable to record guard advance: {str(e)}"
        )

    finally:

        db.close()


# ==================================================
# GET ADVANCES BY DATE
# ==================================================

def get_guard_advances_by_date(record_date):

    db = SessionLocal()

    try:

        records = (

            db.query(GuardAdvance)

            .options(
                joinedload(
                    GuardAdvance.guard
                )
            )

            .filter(
                GuardAdvance.record_date
                == record_date
            )

            .order_by(
                GuardAdvance.id.desc()
            )

            .all()
        )

        return records

    finally:

        db.close()


# ==================================================
# GET ADVANCES BY GUARD
# ==================================================

def get_guard_advances(guard_id):

    db = SessionLocal()

    try:

        records = (

            db.query(GuardAdvance)

            .options(
                joinedload(
                    GuardAdvance.guard
                )
            )

            .filter(
                GuardAdvance.guard_id
                == guard_id
            )

            .order_by(
                GuardAdvance.record_date.desc(),
                GuardAdvance.id.desc()
            )

            .all()
        )

        return records

    finally:

        db.close()


# ==================================================
# GET MONTHLY ADVANCES
# ==================================================

def get_guard_monthly_advances(
    year,
    month
):

    db = SessionLocal()

    try:

        records = (

            db.query(GuardAdvance)

            .options(
                joinedload(
                    GuardAdvance.guard
                )
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

            .order_by(
                GuardAdvance.record_date.desc(),
                GuardAdvance.id.desc()
            )

            .all()
        )

        return records

    finally:

        db.close()


# ==================================================
# GET MONTHLY ADVANCE TOTAL FOR ONE GUARD
# ==================================================

def get_guard_monthly_advance_total(
    guard_id,
    year,
    month
):

    db = SessionLocal()

    try:

        total = (

            db.query(
                func.coalesce(
                    func.sum(
                        GuardAdvance.amount
                    ),
                    0.0
                )
            )

            .filter(

                GuardAdvance.guard_id
                == int(guard_id),

                extract(
                    "year",
                    GuardAdvance.record_date
                ) == int(year),

                extract(
                    "month",
                    GuardAdvance.record_date
                ) == int(month)

            )

            .scalar()
        )

        return float(total or 0.0)

    finally:

        db.close()


# ==================================================
# GET MONTHLY ADVANCE TOTALS FOR ALL GUARDS
#
# Returns:
#
# {
#     guard_id: total_advance
# }
# ==================================================

def get_monthly_advance_totals(
    year,
    month
):

    db = SessionLocal()

    try:

        results = (

            db.query(

                GuardAdvance.guard_id,

                func.coalesce(
                    func.sum(
                        GuardAdvance.amount
                    ),
                    0.0
                ).label(
                    "total_advance"
                )

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

            .group_by(
                GuardAdvance.guard_id
            )

            .all()
        )

        return {

            guard_id: float(
                total_advance or 0.0
            )

            for (
                guard_id,
                total_advance
            ) in results
        }

    finally:

        db.close()


# ==================================================
# GET MONTHLY CATEGORY TOTALS
#
# Returns:
#
# {
#     "Uniform": 2000.0,
#     "Kharchi": 500.0,
#     "Medical": 1000.0
# }
# ==================================================

def get_monthly_category_totals(
    year,
    month
):

    db = SessionLocal()

    try:

        results = (

            db.query(

                GuardAdvance.category,

                func.coalesce(
                    func.sum(
                        GuardAdvance.amount
                    ),
                    0.0
                ).label(
                    "total_amount"
                )

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

            .group_by(
                GuardAdvance.category
            )

            .order_by(
                GuardAdvance.category.asc()
            )

            .all()
        )

        return {

            category: float(
                total_amount or 0.0
            )

            for (
                category,
                total_amount
            ) in results
        }

    finally:

        db.close()


# ==================================================
# DELETE GUARD ADVANCE
# ==================================================

def delete_guard_advance(
    advance_id
):

    db = SessionLocal()

    try:

        advance = (

            db.query(GuardAdvance)

            .filter(
                GuardAdvance.id
                == int(advance_id)
            )

            .first()
        )

        if not advance:

            return (
                False,
                "Advance record not found."
            )

        db.delete(advance)

        db.commit()

        return (
            True,
            "Guard advance deleted successfully."
        )

    except Exception as e:

        db.rollback()

        return (
            False,
            f"Unable to delete guard advance: {str(e)}"
        )

    finally:

        db.close()