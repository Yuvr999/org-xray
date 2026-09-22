import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models.identity import Department, Organization, Permission, Role, User
from app.models.demand import Vendor

# In-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Seed test organization
        org = Organization(id=1, name="Test Org", code="TEST-ORG", is_active=True)
        session.add(org)
        await session.commit()

        # Seed test department
        dept = Department(id=1, organization_id=1, name="Finance", code="FIN", budget_limit=100000.0)
        session.add(dept)

        # Seed permissions
        permissions_def = [
            ("admin:configure", "Admin permissions"),
            ("audit:read", "Audit logs permissions"),
            ("demand:create", "Demand creation"),
            ("demand:classify", "Demand classification"),
            ("demand:submit", "Demand submit"),
            ("purchase:approve", "Purchase approve"),
            ("vendor:read", "Vendor read"),
            ("shadow:review", "Shadow review permission"),
            ("invoice:submit", "Invoice submit permission"),
            ("invoice:approve", "Invoice approve permission"),
        ]
        perm_objs = []
        for idx, (pcode, pdesc) in enumerate(permissions_def, start=1):
            perm_objs.append(Permission(id=idx, code=pcode, description=pdesc))
        session.add_all(perm_objs)
        await session.commit()

        # Seed roles
        r_admin = Role(id=1, name="admin", description="Admin role", permissions=perm_objs)
        r_mgr = Role(
            id=2, 
            name="manager", 
            description="Manager role", 
            permissions=[p for p in perm_objs if p.code in ["demand:create", "demand:classify", "demand:submit", "purchase:approve", "vendor:read", "audit:read", "invoice:submit", "invoice:approve"]]
        )
        r_emp = Role(
            id=3, 
            name="employee", 
            description="Employee role", 
            permissions=[p for p in perm_objs if p.code in ["demand:create", "demand:classify", "demand:submit", "vendor:read", "invoice:submit"]]
        )
        session.add_all([r_admin, r_mgr, r_emp])
        await session.commit()

        # Seed users
        admin_user = User(
            id=1,
            organization_id=1,
            department_id=1,
            email="admin@test.com",
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="Test Admin",
            primary_role="admin",
            is_active=True,
            is_superuser=True,
            roles=[r_admin],
        )
        mgr_user = User(
            id=2,
            organization_id=1,
            department_id=1,
            email="mgr@test.com",
            hashed_password=get_password_hash("MgrPass123!"),
            full_name="Test Manager",
            primary_role="manager",
            is_active=True,
            is_superuser=False,
            roles=[r_mgr],
        )
        emp_user = User(
            id=3,
            organization_id=1,
            department_id=1,
            email="emp@test.com",
            hashed_password=get_password_hash("EmpPass123!"),
            full_name="Test Employee",
            primary_role="employee",
            is_active=True,
            is_superuser=False,
            roles=[r_emp],
        )
        session.add_all([admin_user, mgr_user, emp_user])

        # Seed vendors
        vendor1 = Vendor(
            id=1,
            organization_id=1,
            name="TechCorp Solutions",
            category="Technical",
            region="National",
            contact_email="sales@techcorp.com",
            rating=4.9,
            status="ACTIVE",
            gstin="27AAACT1020A1ZB",
        )
        vendor2 = Vendor(
            id=2,
            organization_id=1,
            name="Global Audit Services",
            category="Finance",
            region="Global",
            contact_email="info@globalaudit.com",
            rating=4.8,
            status="ACTIVE",
            gstin="07AAAAP9988C1ZD",
        )
        session.add_all([vendor1, vendor2])
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    async def _get_test_db():
        yield test_db

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
