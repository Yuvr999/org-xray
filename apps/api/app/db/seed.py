import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.identity import Department, Organization, Permission, Role, User
from app.models.demand import Vendor, Demand, DemandStatus, RoutingMethod


async def seed_data():
    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Seed Organization
        org_stmt = select(Organization).where(Organization.code == "ORG-GLOBAL")
        org_res = await db.execute(org_stmt)
        org = org_res.scalar_one_or_none()
        if not org:
            org = Organization(name="ORG-XRAY Global Enterprise", code="ORG-GLOBAL", is_active=True)
            db.add(org)
            await db.commit()
            await db.refresh(org)

        # 2. Seed Departments
        dept_names = [
            ("Finance", "FIN", 100000.0),
            ("Public Relations", "PR", 50000.0),
            ("Technical Engineering", "TECH", 150000.0),
            ("Operations", "OPS", 75000.0),
        ]
        dept_map = {}
        for dname, dcode, limit in dept_names:
            d_stmt = select(Department).where(Department.organization_id == org.id, Department.code == dcode)
            d_res = await db.execute(d_stmt)
            dept = d_res.scalar_one_or_none()
            if not dept:
                dept = Department(organization_id=org.id, name=dname, code=dcode, budget_limit=limit)
                db.add(dept)
                await db.commit()
                await db.refresh(dept)
            dept_map[dcode] = dept

        # 3. Seed Permissions
        permissions_def = [
            ("demand:create", "Create purchase/demand requests"),
            ("demand:read", "Read demand requests"),
            ("demand:approve", "Approve or reject demand requests"),
            ("demand:classify", "Classify demand requests"),
            ("invoice:submit", "Submit invoices"),
            ("invoice:read", "Read invoice processing results"),
            ("invoice:approve", "Approve invoice verification"),
            ("shadow:review", "Review and tag shadow process alerts"),
            ("procurement:recommend", "Access AI procurement recommendations"),
            ("purchase:approve", "Approve high-value purchase orders"),
            ("asset:reallocate", "Reallocate enterprise assets"),
            ("sensor:read", "Read physical IoT sensor metrics"),
            ("admin:configure", "Manage platform users, roles, and configuration"),
            ("audit:read", "Access immutable platform audit logs"),
        ]
        perm_map = {}
        for pcode, pdesc in permissions_def:
            p_stmt = select(Permission).where(Permission.code == pcode)
            p_res = await db.execute(p_stmt)
            perm = p_res.scalar_one_or_none()
            if not perm:
                perm = Permission(code=pcode, description=pdesc)
                db.add(perm)
                await db.commit()
                await db.refresh(perm)
            perm_map[pcode] = perm

        # 4. Seed Roles
        roles_def = [
            ("admin", "Administrator with full system privileges", list(perm_map.keys())),
            (
                "manager",
                "Departmental manager with approval and review authority",
                [
                    "demand:create",
                    "demand:read",
                    "demand:approve",
                    "demand:classify",
                    "invoice:submit",
                    "invoice:read",
                    "invoice:approve",
                    "shadow:review",
                    "procurement:recommend",
                    "purchase:approve",
                    "asset:reallocate",
                    "sensor:read",
                    "audit:read",
                ],
            ),
            (
                "employee",
                "Standard employee user",
                ["demand:create", "demand:read", "demand:classify", "invoice:submit", "invoice:read", "sensor:read"],
            ),
        ]
        role_map = {}
        for rname, rdesc, rperms in roles_def:
            r_stmt = select(Role).where(Role.name == rname)
            r_res = await db.execute(r_stmt)
            role = r_res.scalar_one_or_none()
            if not role:
                role = Role(name=rname, description=rdesc)
                db.add(role)
                await db.commit()
                await db.refresh(role)
            
            # Attach permissions
            role.permissions = [perm_map[code] for code in rperms if code in perm_map]
            await db.commit()
            role_map[rname] = role

        # 5. Seed Default Users
        users_def = [
            ("admin@orgxray.com", "Admin User", "Admin@123456", "admin", "TECH", True),
            ("manager@orgxray.com", "Finance Manager", "Manager@123456", "manager", "FIN", False),
            ("employee@orgxray.com", "Technical Employee", "Employee@123456", "employee", "TECH", False),
        ]

        user_map = {}
        for email, fullname, password, rname, dcode, is_super in users_def:
            u_stmt = select(User).where(User.email == email)
            u_res = await db.execute(u_stmt)
            user = u_res.scalar_one_or_none()
            if not user:
                user = User(
                    organization_id=org.id,
                    department_id=dept_map[dcode].id if dcode in dept_map else None,
                    email=email,
                    hashed_password=get_password_hash(password),
                    full_name=fullname,
                    primary_role=rname,
                    is_active=True,
                    is_superuser=is_super,
                )
                if rname in role_map:
                    user.roles.append(role_map[rname])
                db.add(user)
                await db.commit()
                await db.refresh(user)
                print(f"Seeded user: {email} ({rname})")
            user_map[email] = user

        # 6. Seed Approved Vendors
        vendors_def = [
            ("TechSupply Corp", "Technical", "National", "sales@techsupply.com", 4.8, "27AAACT1020A1ZB"),
            ("CloudScale Systems", "Technical", "APAC", "enterprise@cloudscale.io", 4.9, "29AABCC5544B1ZC"),
            ("Apex Audit Partners", "Finance", "National", "contact@apexaudit.com", 4.7, "07AAAAP9988C1ZD"),
            ("MediaPulse PR Agency", "PR", "Global", "hello@mediapulse.com", 4.6, "19AAAMP7766D1ZE"),
        ]
        for vname, vcat, vreg, vemail, vrating, vgstin in vendors_def:
            v_stmt = select(Vendor).where(Vendor.name == vname, Vendor.organization_id == org.id)
            v_res = await db.execute(v_stmt)
            if not v_res.scalar_one_or_none():
                v = Vendor(
                    organization_id=org.id,
                    name=vname,
                    category=vcat,
                    region=vreg,
                    contact_email=vemail,
                    rating=vrating,
                    status="ACTIVE",
                    gstin=vgstin,
                )
                db.add(v)
        await db.commit()

    print("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())
