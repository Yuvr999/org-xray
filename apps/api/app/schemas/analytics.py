from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class OverviewAnalytics(BaseModel):
    time_window: str
    composite_shadow_risk_index: float
    total_estimated_leakage: str
    flagged_bypasses_count: int
    purchase_request_volume: int
    total_approved_spend: float
    invoice_verification_pass_rate: float
    gstin_verification_rate: float
    asset_reuse_rate: float
    avoided_purchase_value: float


class CategorySpendBreakdown(BaseModel):
    category: str
    amount: float
    percentage: float


class DepartmentSpendBreakdown(BaseModel):
    department: str
    amount: float
    count: int


class ProcurementAnalytics(BaseModel):
    time_window: str
    purchase_request_volume: int
    approved_requests_count: int
    rejected_requests_count: int
    total_requested_amount: float
    total_approved_amount: float
    avg_approval_turnaround_hours: float
    avoided_purchase_count: int
    avoided_purchase_value: float
    category_spend: List[CategorySpendBreakdown]
    department_spend: List[DepartmentSpendBreakdown]


class ShadowFeedbackDistribution(BaseModel):
    label: str
    count: int
    percentage: float


class ProcessAnalytics(BaseModel):
    time_window: str
    total_cases_analyzed: int
    shadow_process_cases_count: int
    shadow_process_rate: float
    active_shadow_alerts_count: int
    total_estimated_leakage: str
    score_band_distribution: Dict[str, int]
    top_unapproved_tools: List[Dict[str, Any]]
    feedback_distribution: List[ShadowFeedbackDistribution]


class ModelPerformanceMetrics(BaseModel):
    model_name: str
    model_version: str
    predictions_count: int
    accuracy_or_confidence_avg: float
    recommendation_acceptance_rate: float
    human_override_rate: float


class ModelPerformanceAnalytics(BaseModel):
    time_window: str
    routing_classifier: ModelPerformanceMetrics
    shadow_anomaly_detector: ModelPerformanceMetrics
    overall_human_override_rate: float
    human_acceptance_rate: float


class AuditSummaryAnalytics(BaseModel):
    time_window: str
    total_audit_events: int
    success_events_count: int
    denied_events_count: int
    actions_breakdown: Dict[str, int]
    resource_breakdown: Dict[str, int]
