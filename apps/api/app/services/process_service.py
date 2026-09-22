from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.logging import logger
from app.ml.process_anomaly import compute_ml_anomaly_score
from app.models.process import (
    ProcessCase,
    ProcessDefinition,
    ProcessEvent,
    ShadowAlert,
    ShadowFeedback,
)
from app.schemas.process import (
    CaseAnalysisResult,
    ProcessEventCreate,
    ScoreComponents,
)


def get_score_band(shadow_score: float) -> str:
    if shadow_score <= 30.0:
        return "Normal"
    elif shadow_score <= 60.0:
        return "Process Variation"
    elif shadow_score <= 80.0:
        return "Suspicious"
    else:
        return "Strong Shadow Process"


def calculate_shadow_score(
    events: List[ProcessEvent],
    expected_activities: List[str],
) -> Tuple[float, ScoreComponents, List[str], List[str], List[str]]:
    actual_activities = [e.activity for e in events]
    expected_set = set(expected_activities)
    actual_set = set(actual_activities)

    # 1. Deviation
    missing_steps = [act for act in expected_activities if act not in actual_set]
    unexpected_steps = [act for act in actual_activities if act not in expected_set]
    
    # Repetitions
    seen = set()
    repeated_steps = []
    for act in actual_activities:
        if act in seen:
            repeated_steps.append(act)
        seen.add(act)

    dev_ratio = (len(missing_steps) + len(unexpected_steps)) / max(len(expected_activities), 1)
    deviation_comp = min(dev_ratio * 100.0, 100.0)

    # 2. Recurrence
    unapproved_events = [
        e for e in events
        if "unapproved" in e.activity_category.lower()
        or "manual" in e.source_system.lower()
        or "excel" in e.source_system.lower()
        or "personal" in e.activity.lower()
    ]
    recurrence_comp = min(len(unapproved_events) * 25.0, 100.0)

    # 3. Consistency
    roles = set(e.actor_role for e in events)
    consistency_comp = 20.0 if len(roles) <= 2 else min(len(roles) * 25.0, 100.0)

    # 4. CrossSystemActivity
    source_systems = set(e.source_system for e in events)
    cross_system_comp = min(len(source_systems) * 30.0, 100.0)

    # 5. BusinessRisk
    total_amount = sum(e.amount for e in events if e.amount)
    unapproved_tool_count = len(unapproved_events)
    risk_comp = 20.0
    if unapproved_tool_count > 0:
        risk_comp += 40.0
    if total_amount > 10000.0:
        risk_comp += 40.0
    business_risk_comp = min(risk_comp, 100.0)

    # Documented Weighted Formula:
    # Shadow Score = 0.25*Deviation + 0.20*Recurrence + 0.15*Consistency + 0.15*CrossSystemActivity + 0.25*BusinessRisk
    composite_score = round(
        (0.25 * deviation_comp)
        + (0.20 * recurrence_comp)
        + (0.15 * consistency_comp)
        + (0.15 * cross_system_comp)
        + (0.25 * business_risk_comp),
        2,
    )

    score_components = ScoreComponents(
        deviation=round(deviation_comp, 2),
        recurrence=round(recurrence_comp, 2),
        consistency=round(consistency_comp, 2),
        cross_system_activity=round(cross_system_comp, 2),
        business_risk=round(business_risk_comp, 2),
    )

    return composite_score, score_components, missing_steps, unexpected_steps, repeated_steps


async def analyze_process_case(
    db: AsyncSession,
    case_id: str,
    organization_id: int,
    department: str = "General",
) -> CaseAnalysisResult:
    # Fetch events for case
    stmt = (
        select(ProcessEvent)
        .where(ProcessEvent.case_id == case_id, ProcessEvent.organization_id == organization_id)
        .order_by(ProcessEvent.timestamp.asc())
    )
    result = await db.execute(stmt)
    events = list(result.scalars().all())

    if not events:
        raise ValueError(f"No events found for case_id '{case_id}'")

    process_name = events[0].process_name

    # Fetch official process definition if exists
    def_stmt = select(ProcessDefinition).where(
        ProcessDefinition.organization_id == organization_id,
        ProcessDefinition.name == process_name,
    )
    def_res = await db.execute(def_stmt)
    process_def = def_res.scalar_one_or_none()
    expected_activities = process_def.expected_activities if process_def else ["request", "approve", "fulfill"]

    # Calculate documented composite score
    shadow_score, score_components, missing_steps, unexpected_steps, repeated_steps = calculate_shadow_score(
        events, expected_activities
    )
    score_band = get_score_band(shadow_score)

    # ML Anomaly calculation
    raw_events_dict = [
        {
            "activity": e.activity,
            "activity_category": e.activity_category,
            "source_system": e.source_system,
            "timestamp": e.timestamp,
        }
        for e in events
    ]
    ml_anomaly_score = compute_ml_anomaly_score(raw_events_dict, expected_activities)

    # Create/update ProcessCase record
    case_stmt = select(ProcessCase).where(ProcessCase.case_id == case_id)
    case_res = await db.execute(case_stmt)
    case_obj = case_res.scalar_one_or_none()
    if not case_obj:
        case_obj = ProcessCase(
            case_id=case_id,
            organization_id=organization_id,
            process_name=process_name,
            start_time=events[0].timestamp,
            end_time=events[-1].timestamp,
            event_count=len(events),
            shadow_score=shadow_score,
            anomaly_score=ml_anomaly_score,
        )
        db.add(case_obj)
    else:
        case_obj.event_count = len(events)
        case_obj.end_time = events[-1].timestamp
        case_obj.shadow_score = shadow_score
        case_obj.anomaly_score = ml_anomaly_score

    await db.commit()

    # Generate Shadow Alert if score > 30 (Process Variation or higher)
    alert_created = False
    alert_id = None
    if shadow_score > 30.0:
        unapproved_tools = [e.source_system for e in events if "manual" in e.source_system.lower() or "excel" in e.source_system.lower() or "personal" in e.activity.lower()]
        tool_name = unapproved_tools[0] if unapproved_tools else events[0].source_system
        severity = "Critical" if shadow_score >= 81.0 else ("High" if shadow_score >= 61.0 else "Medium")

        alert_stmt = select(ShadowAlert).where(ShadowAlert.case_id == case_id)
        alert_res = await db.execute(alert_stmt)
        existing_alert = alert_res.scalar_one_or_none()

        total_leakage = sum(e.amount for e in events if e.amount) or 14200.0

        if not existing_alert:
            alert_code = f"SHD-{case_id[-4:]}"
            alert = ShadowAlert(
                alert_code=alert_code,
                organization_id=organization_id,
                case_id=case_id,
                department=department,
                process_name=process_name,
                unapproved_tool=f"{tool_name} (Unsanctioned Bypassed Workflow)",
                severity=severity,
                estimated_leakage=f"${total_leakage:,.2f}",
                shadow_score=shadow_score,
                score_band=score_band,
                deviation_component=score_components.deviation,
                recurrence_component=score_components.recurrence,
                consistency_component=score_components.consistency,
                cross_system_component=score_components.cross_system_activity,
                business_risk_component=score_components.business_risk,
                ml_anomaly_score=ml_anomaly_score,
                evidence={
                    "missing_steps": missing_steps,
                    "unexpected_steps": unexpected_steps,
                    "repeated_steps": repeated_steps,
                    "events_count": len(events),
                },
                status="Flagged",
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
            alert_created = True
            alert_id = alert.id
        else:
            existing_alert.shadow_score = shadow_score
            existing_alert.score_band = score_band
            existing_alert.severity = severity
            existing_alert.ml_anomaly_score = ml_anomaly_score
            await db.commit()
            alert_id = existing_alert.id

    return CaseAnalysisResult(
        case_id=case_id,
        process_name=process_name,
        shadow_score=shadow_score,
        score_band=score_band,
        score_components=score_components,
        ml_anomaly_score=ml_anomaly_score,
        missing_steps=missing_steps,
        unexpected_steps=unexpected_steps,
        repeated_steps=repeated_steps,
        alert_created=alert_created,
        alert_id=alert_id,
    )
