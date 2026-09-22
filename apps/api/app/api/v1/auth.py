from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from jwt.exceptions import PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import get_current_user, get_user_permission_codes
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.identity import Role, User
from app.schemas.identity import LoginRequest, RefreshTokenRequest, Token, UserOut
from app.services.audit_service import log_audit_event

router = APIRouter()


async def _authenticate_user(email: str, password: str, db: AsyncSession, request: Request) -> User:
    stmt = (
        select(User)
        .where(User.email == email)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        await log_audit_event(
            db=db,
            action="USER_LOGIN_FAILED",
            resource_type="auth",
            resource_id=email,
            request=request,
            status="DENIED",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        await log_audit_event(
            db=db,
            action="USER_LOGIN_INACTIVE",
            resource_type="auth",
            resource_id=str(user.id),
            user=user,
            request=request,
            status="DENIED",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    return user


@router.post("/login", response_model=Token)
async def login(
    login_req: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await _authenticate_user(login_req.email, login_req.password, db, request)

    access_token = create_access_token(
        subject=user.id,
        extra_claims={"role": user.primary_role, "org_id": user.organization_id},
    )
    refresh_token = create_refresh_token(subject=user.id)

    await log_audit_event(
        db=db,
        action="USER_LOGIN_SUCCESS",
        resource_type="auth",
        resource_id=str(user.id),
        user=user,
        request=request,
        status="SUCCESS",
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/session", response_model=Token)
async def session_login(
    request: Request,
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    # Support form-data or JSON payload for legacy/alternative callers
    login_email = username or email
    if not login_email or not password:
        try:
            body = await request.json()
            login_email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            pass

    if not login_email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email/username and password required")

    user = await _authenticate_user(login_email, password, db, request)

    access_token = create_access_token(
        subject=user.id,
        extra_claims={"role": user.primary_role, "org_id": user.organization_id},
    )
    refresh_token = create_refresh_token(subject=user.id)

    await log_audit_event(
        db=db,
        action="USER_LOGIN_SUCCESS",
        resource_type="auth",
        resource_id=str(user.id),
        user=user,
        request=request,
        status="SUCCESS",
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_token(refresh_req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for refresh",
            )
        user_id = int(payload.get("sub"))
    except (PyJWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    new_access_token = create_access_token(
        subject=user.id,
        extra_claims={"role": user.primary_role, "org_id": user.organization_id},
    )
    new_refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await log_audit_event(
        db=db,
        action="USER_LOGOUT",
        resource_type="auth",
        resource_id=str(current_user.id),
        user=current_user,
        request=request,
        status="SUCCESS",
    )
    return {"detail": "Successfully logged out"}


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    permissions = await get_user_permission_codes(current_user, db)
    user_out = UserOut.model_validate(current_user)
    user_out.permissions = permissions
    return user_out
