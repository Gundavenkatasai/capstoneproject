"""
CivicMind AI — Idempotent Development Demo Account Seeder
Seeds standard role-based accounts (Admin, Officer, Citizen) and baseline departments.
Refuses to seed in production environments.
"""

import sys
import uuid
import asyncio
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import select
from app.core.config import settings
from app.core.database import AsyncSessionFactory
from app.core.security import get_password_hash
from app.models.user import User
from app.models.department import Department
from app.models.officer import Officer

DEMO_DEPARTMENTS = [
    {
        "id": "dept_pwd",
        "code": "PWD-RDS",
        "name": "Public Works Department (PWD)",
        "head_name": "Er. Alok Mathur",
        "officer_count": 42,
        "zone": "All Zones",
        "workload_status": "optimal",
        "sla_compliance_rate": 91.20,
    },
    {
        "id": "dept_sanitation",
        "code": "MC-SWM",
        "name": "Municipal Solid Waste Management",
        "head_name": "Dr. Ramesh Nair",
        "officer_count": 58,
        "zone": "All Zones",
        "workload_status": "heavy",
        "sla_compliance_rate": 84.50,
    },
    {
        "id": "dept_wssb",
        "code": "WSSB-OPS",
        "name": "Water Supply & Sewerage Board",
        "head_name": "Smt. Geeta Reddy",
        "officer_count": 35,
        "zone": "All Zones",
        "workload_status": "optimal",
        "sla_compliance_rate": 89.00,
    },
]

DEMO_ACCOUNTS = [
    # Required Standard Demo Accounts
    {
        "email": "admin@civicmind.gov",
        "name": "System Administrator",
        "role": "admin",
        "password": settings.DEMO_ADMIN_PASSWORD,
        "phone": "+91 99000 00001",
        "ward": "Command HQ",
        "badge": "Principal Administrator",
    },
    {
        "email": "officer@civicmind.gov",
        "name": "Inspector Rajesh Verma",
        "role": "officer",
        "password": settings.DEMO_OFFICER_PASSWORD,
        "phone": "+91 99000 00002",
        "ward": "Ward 14 (Central)",
        "badge": "Superintending Engineer",
        "department_id": "dept_pwd",
    },
    {
        "email": "citizen@civicmind.gov",
        "name": "Aarav Sharma",
        "role": "citizen",
        "password": settings.DEMO_CITIZEN_PASSWORD,
        "phone": "+91 99000 00003",
        "ward": "Ward 14 (Central)",
        "badge": "Verified Resident",
    },
    # Frontend Preset Accounts for Seamless 1-Click Login
    {
        "email": "commissioner.grievance@gov.in",
        "name": "Dr. Sunita Rao, IAS",
        "role": "admin",
        "password": settings.DEMO_ADMIN_PASSWORD,
        "phone": "+91 99988 77665",
        "ward": "Apex Command HQ",
        "badge": "Principal Commissioner",
    },
    {
        "email": "rajesh.verma@pwd.gov.in",
        "name": "Er. Rajesh Verma",
        "role": "officer",
        "password": settings.DEMO_OFFICER_PASSWORD,
        "phone": "+91 94123 45678",
        "ward": "Central Division - Roads",
        "badge": "Superintending Engineer",
        "department_id": "dept_pwd",
    },
    {
        "email": "aarav.sharma@example.com",
        "name": "Aarav Sharma",
        "role": "citizen",
        "password": settings.DEMO_CITIZEN_PASSWORD,
        "phone": "+91 98765 43210",
        "ward": "Ward 14 (Vasant Kunj)",
        "badge": "Verified Resident",
    },
]


async def seed_demo_accounts() -> None:
    if settings.ENVIRONMENT == "production":
        print("[ERROR] Refusing to seed demo accounts in PRODUCTION environment.")
        sys.exit(1)

    print(f"[*] Starting CivicMind AI Demo Account Seeding (Environment: {settings.ENVIRONMENT})...")

    async with AsyncSessionFactory() as session:
        # 1. Seed baseline departments
        for dept_data in DEMO_DEPARTMENTS:
            existing_dept = await session.execute(
                select(Department).where(Department.id == dept_data["id"])
            )
            if not existing_dept.scalar_one_or_none():
                dept = Department(**dept_data)
                session.add(dept)
                print(f"    [+] Created department: {dept_data['name']} ({dept_data['code']})")

        await session.commit()

        # 2. Seed demo accounts
        created_count = 0
        skipped_count = 0

        for account in DEMO_ACCOUNTS:
            normalized_email = account["email"].lower().strip()
            existing_user = await session.execute(
                select(User).where(User.email == normalized_email)
            )
            user = existing_user.scalar_one_or_none()

            if user:
                skipped_count += 1
                continue

            user_id = uuid.uuid4()
            pwd_hash = get_password_hash(account["password"])

            new_user = User(
                id=user_id,
                name=account["name"],
                email=normalized_email,
                password_hash=pwd_hash,
                role=account["role"],
                phone=account.get("phone"),
                ward=account.get("ward"),
                badge=account.get("badge"),
                is_active=True,
            )
            session.add(new_user)

            if account["role"] == "officer":
                officer_profile = Officer(
                    id=user_id,
                    department_id=account.get("department_id", "dept_pwd"),
                    assigned_ward=account.get("ward", "Ward 14 (Central)"),
                    active_cases=12,
                    resolved_mtd=28,
                    avg_resolution_hours=36.5,
                    rating=4.85,
                    status="active",
                )
                session.add(officer_profile)

            created_count += 1
            print(f"    [+] Created user: {account['name']} <{normalized_email}> [{account['role']}]")

        await session.commit()

        print(f"\n[OK] Seeding complete! Created: {created_count}, Skipped (Already existed): {skipped_count}")

        if settings.PRINT_DEMO_CREDENTIALS:
            print("\n" + "=" * 60)
            print("  CIVICMIND AI — DEVELOPMENT DEMO CREDENTIALS")
            print("=" * 60)
            print(f"  ADMINISTRATOR: admin@civicmind.gov / {settings.DEMO_ADMIN_PASSWORD}")
            print(f"  OFFICER:       officer@civicmind.gov / {settings.DEMO_OFFICER_PASSWORD}")
            print(f"  CITIZEN:       citizen@civicmind.gov / {settings.DEMO_CITIZEN_PASSWORD}")
            print("  FRONTEND PRESET CREDENTIALS:")
            print(f"  Admin:   commissioner.grievance@gov.in / {settings.DEMO_ADMIN_PASSWORD}")
            print(f"  Officer: rajesh.verma@pwd.gov.in / {settings.DEMO_OFFICER_PASSWORD}")
            print(f"  Citizen: aarav.sharma@example.com / {settings.DEMO_CITIZEN_PASSWORD}")
            print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(seed_demo_accounts())
