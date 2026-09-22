import pytest
from fastapi import HTTPException
from app.core.deps import RequirePermission, RequireRole
from app.models.identity import User


@pytest.mark.asyncio
async def test_require_role_granted():
    user = User(id=1, email="admin@test.com", primary_role="admin", is_superuser=False)
    checker = RequireRole(allowed_roles=["admin", "manager"])
    result = await checker(current_user=user)
    assert result == user


@pytest.mark.asyncio
async def test_require_role_denied():
    user = User(id=2, email="employee@test.com", primary_role="employee", is_superuser=False)
    checker = RequireRole(allowed_roles=["admin", "manager"])
    with pytest.raises(HTTPException) as exc_info:
        await checker(current_user=user)
    assert exc_info.value.status_code == 403
    assert "lacks required permissions" in exc_info.value.detail


@pytest.mark.asyncio
async def test_superuser_bypasses_role_restriction():
    user = User(id=3, email="super@test.com", primary_role="employee", is_superuser=True)
    checker = RequireRole(allowed_roles=["admin"])
    result = await checker(current_user=user)
    assert result == user


@pytest.mark.asyncio
async def test_api_rbac_employee_denied_user_creation(client):
    emp_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "emp@test.com", "password": "EmpPass123!"},
    )
    emp_token = emp_login.json()["access_token"]

    create_resp = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {emp_token}"},
        json={
            "email": "newuser@test.com",
            "password": "Password123!",
            "full_name": "New User",
            "primary_role": "employee",
            "organization_id": 1,
        },
    )
    assert create_resp.status_code == 403


@pytest.mark.asyncio
async def test_api_rbac_admin_can_list_users_and_audit(client):
    admin_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    admin_token = admin_login.json()["access_token"]

    users_resp = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert users_resp.status_code == 200
    assert len(users_resp.json()) >= 2

    audit_resp = await client.get(
        "/api/v1/audit-log",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert audit_resp.status_code == 200
    assert isinstance(audit_resp.json(), list)
