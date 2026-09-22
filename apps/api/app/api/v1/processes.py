from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.deps import RequirePermission, RequireRole, get_current_user
from app.models.identity import User
from app.models.process import ProcessDefinition, ProcessEvent, ShadowAlert, ShadowFeedback
from app.schemas.process import (
    CaseAnalysisRequest,
    CaseAnalysisResult,
    ProcessDefinitionCreate,
    ProcessDefinitionOut,
    ProcessEventCreate,
    ProcessEventOut,
    ShadowAlertOut,
    ShadowFeedbackCreate,
    ShadowFeedbackOut,
)
from app.services.audit_service import log_audit_event
from app.services.process_service import analyze_process_case

router = APIRouter()


@router.post("/process-events", response_model=ProcessEventOut, status_code=status.HTTP_201_CREATED)
async def ingest_process_event(
    event_in: ProcessEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_time = event_in.timestamp or datetime.now(timezone.utc)
    event = ProcessEvent(
        case_id=event_in.case_id,
        organization_id=current_user.organization_id,
        actor_id=event_in.actor_id or current_user.id,
        actor_role=event_in.actor_role or current_user.primary_role,
        source_system=event_in.source_system,
        process_name=event_in.process_name,
        activity=event_in.activity,
        activity_category=event_in.activity_category,
        timestamp=event_time,
        object_id=event_in.object_id,
        amount=event_in.amount,
        metadata_json=event_in.metadata_json,
        correlation_id=event_in.correlation_id,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.post("/process-events/analyze", response_model=CaseAnalysisResult)
async def analyze_case_events(
    analysis_req: CaseAnalysisRequest,
    department: str = Query("General"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = await analyze_process_case(
            db=db,
            case_id=analysis_req.case_id,
            organization_id=current_user.organization_id,
            department=department,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/processes", response_model=List[ProcessDefinitionOut])
async def list_process_definitions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(ProcessDefinition).where(ProcessDefinition.organization_id == current_user.organization_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/processes", response_model=ProcessDefinitionOut, status_code=status.HTTP_201_CREATED)
async def create_process_definition(
    def_in: ProcessDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("admin:configure")),
):
    proc_def = ProcessDefinition(
        organization_id=current_user.organization_id,
        name=def_in.name,
        code=def_in.code,
        description=def_in.description,
        expected_activities=def_in.expected_activities,
    )
    db.add(proc_def)
    await db.commit()
    await db.refresh(proc_def)
    return proc_def


@router.get("/shadow-alerts", response_model=List[ShadowAlertOut])
async def list_shadow_alerts(
    severity: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    department: Optional[str] = None,
    score_band: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("shadow:review")),
):
    stmt = (
        select(ShadowAlert)
        .where(ShadowAlert.organization_id == current_user.organization_id)
        .options(selectinload(ShadowAlert.feedbacks))
        .order_by(ShadowAlert.detected_at.desc())
    )

    if severity:
        stmt = stmt.where(ShadowAlert.severity == severity)
    if status_filter:
        stmt = stmt.where(ShadowAlert.status == status_filter)
    if department:
        stmt = stmt.where(ShadowAlert.department == department)
    if score_band:
        stmt = stmt.where(ShadowAlert.score_band == score_band)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/shadow-alerts/{alert_id}", response_model=ShadowAlertOut)
async def get_shadow_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("shadow:review")),
):
    stmt = (
        select(ShadowAlert)
        .where(ShadowAlert.id == alert_id, ShadowAlert.organization_id == current_user.organization_id)
        .options(selectinload(ShadowAlert.feedbacks))
    )
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shadow alert not found")

    return alert


@router.post("/shadow-alerts/{alert_id}/feedback", response_model=ShadowFeedbackOut)
async def submit_shadow_feedback(
    alert_id: int,
    feedback_in: ShadowFeedbackCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequirePermission("shadow:review")),
):
    valid_labels = ["Valid Shadow Process", "Normal Variation", "False Alert", "Needs Investigation"]
    if feedback_in.feedback_label not in valid_labels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feedback label. Must be one of: {valid_labels}",
        )

    stmt = select(ShadowAlert).where(ShadowAlert.id == alert_id, ShadowAlert.organization_id == current_user.organization_id)
    res = await db.execute(stmt)
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shadow alert not found")

    # Update alert status based on feedback tag
    if feedback_in.feedback_label == "Valid Shadow Process":
        alert.status = "Flagged"
    elif feedback_in.feedback_label == "False Alert":
        alert.status = "Resolved"
    else:
        alert.status = "Investigating"

    feedback = ShadowFeedback(
        alert_id=alert.id,
        user_id=current_user.id,
        feedback_label=feedback_in.feedback_label,
        notes=feedback_in.notes,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    await log_audit_event(
        db=db,
        action="SHADOW_FEEDBACK_SUBMIT",
        resource_type="shadow_alert",
        resource_id=str(alert.id),
        new_values={"label": feedback.feedback_label, "notes": feedback.notes},
        user=current_user,
        request=request,
    )

    return feedback
