from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import RequirePermission, RequireRole, get_current_user, get_user_permission_codes
from app.core.security import get_password_hash
from app.models.identity import Department, Permission, Role, User
from app.schemas.identity import (
    DepartmentOut,
    PermissionOut,
    RoleOut,
    UserCreate,
    UserOut,
    UserUpdate,
)
from app.services.audit_service import log_audit_event

router = APIRouter()


@router.get("/users", response_model=List[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireRole(["admin", "manager"])),
):
    stmt = (
        select(User)
        .where(User.organization_id == current_user.organization_id)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    result = await db.execute(stmt)
    users = result.scalars().all()

    users_out = []
    for u in users:
        perms = await get_user_permission_codes(u, db)
        uo = UserOut.model_validate(u)
        uo.permissions = perms
        users_out.append(uo)
        
    return users_out


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("admin:configure")),
):
    # Check if email exists
    stmt = select(User).where(User.email == user_in.email)
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Assign role if exists
    role_stmt = select(Role).where(Role.name == user_in.primary_role)
    role_res = await db.execute(role_stmt)
    role_obj = role_res.scalar_one_or_none()

    new_user = User(
        organization_id=user_in.organization_id,
        department_id=user_in.department_id,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        primary_role=user_in.primary_role,
        is_active=True,
    )
    if role_obj:
        new_user.roles.append(role_obj)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    await log_audit_event(
        db=db,
        action="USER_CREATE",
        resource_type="user",
        resource_id=str(new_user.id),
        new_values={"email": new_user.email, "role": new_user.primary_role},
        user=current_user,
        request=request,
    )

    perms = await get_user_permission_codes(new_user, db)
    uo = UserOut.model_validate(new_user)
    uo.permissions = perms
    return uo


@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.primary_role not in ["admin", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view user details")

    stmt = (
        select(User)
        .where(User.id == user_id, User.organization_id == current_user.organization_id)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    res = await db.execute(stmt)
    target_user = res.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    perms = await get_user_permission_codes(target_user, db)
    uo = UserOut.model_validate(target_user)
    uo.permissions = perms
    return uo


@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("admin:configure")),
):
    stmt = select(User).where(User.id == user_id).options(selectinload(User.roles))
    res = await db.execute(stmt)
    target_user = res.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    old_values = {
        "full_name": target_user.full_name,
        "primary_role": target_user.primary_role,
        "department_id": target_user.department_id,
        "is_active": target_user.is_active,
    }

    if user_update.full_name is not None:
        target_user.full_name = user_update.full_name
    if user_update.department_id is not None:
        target_user.department_id = user_update.department_id
    if user_update.is_active is not None:
        target_user.is_active = user_update.is_active
    if user_update.password is not None:
        target_user.hashed_password = get_password_hash(user_update.password)
    if user_update.primary_role is not None:
        target_user.primary_role = user_update.primary_role
        role_stmt = select(Role).where(Role.name == user_update.primary_role)
        role_res = await db.execute(role_stmt)
        role_obj = role_res.scalar_one_or_none()
        if role_obj:
            target_user.roles = [role_obj]

    await db.commit()
    await db.refresh(target_user)

    new_values = {
        "full_name": target_user.full_name,
        "primary_role": target_user.primary_role,
        "department_id": target_user.department_id,
        "is_active": target_user.is_active,
    }

    await log_audit_event(
        db=db,
        action="USER_UPDATE",
        resource_type="user",
        resource_id=str(target_user.id),
        old_values=old_values,
        new_values=new_values,
        user=current_user,
        request=request,
    )

    perms = await get_user_permission_codes(target_user, db)
    uo = UserOut.model_validate(target_user)
    uo.permissions = perms
    return uo


@router.get("/departments", response_model=List[DepartmentOut])
async def list_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Department).where(Department.organization_id == current_user.organization_id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/roles", response_model=List[RoleOut])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Role).options(selectinload(Role.permissions))
    res = await db.execute(stmt)
    return res.scalars().all()
