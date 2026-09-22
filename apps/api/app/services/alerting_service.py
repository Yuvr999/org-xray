import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.core.logging import logger


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AlertEvent(BaseModel):
    title: str
    severity: AlertSeverity
    message: str
    source_module: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = ""

    def __init__(self, **data):
        if not data.get("timestamp"):
            data["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        super().__init__(**data)


class AlertingService:
    """
    Central dispatcher for operational and infrastructure alerts.
    Dispatches alerts to structured loggers, webhook sinks, and on-call notification channels.
    """

    def __init__(self):
        self.alert_history: List[AlertEvent] = []
        self.webhook_url: Optional[str] = None

    def configure_webhook(self, url: str):
        self.webhook_url = url

    async def emit_alert(
        self,
        title: str,
        severity: AlertSeverity,
        message: str,
        source_module: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AlertEvent:
        event = AlertEvent(
            title=title,
            severity=severity,
            message=message,
            source_module=source_module,
            details=details or {}
        )
        
        # Keep in local ring buffer (last 500 alerts)
        self.alert_history.append(event)
        if len(self.alert_history) > 500:
            self.alert_history.pop(0)

        # Log with appropriate level
        log_payload = {
            "alert_title": event.title,
            "severity": event.severity.value,
            "source": event.source_module,
            "details": event.details
        }
        
        if severity == AlertSeverity.CRITICAL:
            logger.critical(f"ALERT [{severity.value}] {title}: {message}", extra=log_payload)
        elif severity == AlertSeverity.ERROR:
            logger.error(f"ALERT [{severity.value}] {title}: {message}", extra=log_payload)
        elif severity == AlertSeverity.WARNING:
            logger.warning(f"ALERT [{severity.value}] {title}: {message}", extra=log_payload)
        else:
            logger.info(f"ALERT [{severity.value}] {title}: {message}", extra=log_payload)

        # Dispatch external webhook if configured
        if self.webhook_url:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        self.webhook_url,
                        json=event.model_dump()
                    )
            except Exception as e:
                logger.warning(f"Failed to post alert to external webhook: {e}")

        return event

    def get_recent_alerts(self, limit: int = 50, min_severity: Optional[AlertSeverity] = None) -> List[AlertEvent]:
        alerts = self.alert_history
        if min_severity:
            sev_levels = {
                AlertSeverity.INFO: 1,
                AlertSeverity.WARNING: 2,
                AlertSeverity.ERROR: 3,
                AlertSeverity.CRITICAL: 4,
            }
            target_level = sev_levels.get(min_severity, 1)
            alerts = [a for a in alerts if sev_levels.get(a.severity, 1) >= target_level]
        return alerts[-limit:]


alerting_service = AlertingService()
