from database.connection import SessionLocal
from database.models import Guard

db = SessionLocal()

try:
    guards = (
        db.query(Guard)
        .order_by(Guard.id)
        .all()
    )

    print("\n========== GUARDS ==========\n")

    for guard in guards:
        print(
            f"ID: {guard.id} | "
            f"Employee ID: {guard.employee_id} | "
            f"Name: {guard.name} | "
            f"Status: {guard.status} | "
            f"Joining: {guard.joining_date} | "
            f"Deactivation: {guard.deactivation_date}"
        )

finally:
    db.close()