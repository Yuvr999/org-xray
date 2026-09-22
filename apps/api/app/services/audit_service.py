from typing import Any, Dict, Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.models.identity import AuditLog, User


async def log_audit_event(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    user: Optional[User] = None,
    request: Optional[Request] = None,
    status: str = "SUCCESS",
    organization_id: Optional[int] = None,
) -> AuditLog:
    org_id = organization_id or (user.organization_id if user else None)
    user_id = user.id if user else None
    user_email = user.email if user else None
    user_role = user.primary_role if user else None

    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    audit_entry = AuditLog(
        organization_id=org_id,
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
    )
    db.add(audit_entry)
    try:
        await db.commit()
        await db.refresh(audit_entry)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to record audit log: {e}")
        raise e

    return audit_entry


class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        user: Optional[User] = None,
        request: Optional[Request] = None,
        status: str = "SUCCESS",
        organization_id: Optional[int] = None,
    ) -> AuditLog:
        return await log_audit_event(
            db=db,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            user=user,
            request=request,
            status=status,
            organization_id=organization_id,
        )


# Simplified alias used by service layers (no request context needed)
async def create_audit_log(
    db: AsyncSession,
    organization_id: int,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    status: str = "SUCCESS",
) -> AuditLog:
    audit_entry = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        old_values=old_values,
        new_values=new_values,
        status=status,
    )
    db.add(audit_entry)
    try:
        await db.commit()
        await db.refresh(audit_entry)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to record audit log: {e}")
        raise e
    return audit_entry
