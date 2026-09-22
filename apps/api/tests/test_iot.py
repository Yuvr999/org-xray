"""
Phase 8 – IoT / Physical Infrastructure Tests

Tests:
  - Sensor reading ingestion and persistence
  - Max threshold breach → WARNING alert
  - Critical breach (>120% of max) → CRITICAL alert
  - Min threshold breach → WARNING alert
  - Within threshold → ONLINE status maintained, no alert
  - OCCUPANCY sensor updates area current_occupancy + triggers CRITICAL area alert when over capacity
  - Batch ingestion returns correct counts
  - Alert resolve lifecycle (ACTIVE → ACKNOWLEDGED → RESOLVED)
  - Sensor registration validation (unknown area)
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from app.models.iot import (
    AlertSeverity,
    AlertStatus,
    AreaStatus,
    InfrastructureAlert,
    PhysicalArea,
    Sensor,
    SensorReading,
    SensorStatus,
    SensorType,
)
from app.schemas.iot import PhysicalAreaCreate, SensorCreate, SensorReadingCreate
from app.services.iot_service import IoTService
from app.models.identity import User


def make_user(uid=1, org_id=1, role="admin") -> User:
    u = MagicMock(spec=User)
    u.id = uid
    u.organization_id = org_id
    u.primary_role = role
    u.email = "admin@test.com"
    u.is_superuser = True
    return u


def make_area(area_id=1, org_id=1, capacity=50, occupancy=0) -> PhysicalArea:
    a = MagicMock(spec=PhysicalArea)
    a.id = area_id
    a.organization_id = org_id
    a.name = "Server Room A"
    a.code = "SR-A"
    a.building = "HQ"
    a.capacity = capacity
    a.current_occupancy = occupancy
    a.status = AreaStatus.NORMAL.value
    return a


def make_sensor(
    sensor_id=1, org_id=1, device_id="DEV-001",
    sensor_type=SensorType.OCCUPANCY.value,
    min_thresh=None, max_thresh=None,
    area=None, unit="persons"
) -> Sensor:
    s = MagicMock(spec=Sensor)
    s.id = sensor_id
    s.organization_id = org_id
    s.device_id = device_id
    s.name = f"Sensor {device_id}"
    s.sensor_type = sensor_type
    s.unit = unit
    s.status = SensorStatus.ONLINE.value
    s.min_threshold = min_thresh
    s.max_threshold = max_thresh
    s.last_reading_value = None
    s.last_reading_at = None
    s.area_id = area.id if area else 1
    s.area = area or make_area()
    return s


# ── Threshold Evaluation ───────────────────────────────────────────────────────

class TestThresholdEvaluation:
    @pytest.mark.asyncio
    async def test_no_thresholds_no_alert(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()

        sensor = make_sensor(min_thresh=None, max_thresh=None, sensor_type=SensorType.TEMPERATURE.value)
        alert = await IoTService._evaluate_thresholds(db, sensor, value=25.0)

        assert alert is None
        assert sensor.status == SensorStatus.ONLINE.value

    @pytest.mark.asyncio
    async def test_max_threshold_warning_alert(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()

        sensor = make_sensor(max_thresh=30.0, sensor_type=SensorType.TEMPERATURE.value, unit="°C")
        alert = await IoTService._evaluate_thresholds(db, sensor, value=32.0)

        assert alert is not None
        assert alert.alert_type == "THRESHOLD_BREACH_MAX"
        assert alert.severity == AlertSeverity.WARNING.value
        assert alert.metric_value == 32.0
        assert alert.threshold_value == 30.0
        assert sensor.status == SensorStatus.WARNING.value

    @pytest.mark.asyncio
    async def test_max_threshold_critical_alert_above_120_percent(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()

        # max_thresh=30, value=37 → 37/30 = 123% > 120% → CRITICAL
        sensor = make_sensor(max_thresh=30.0, sensor_type=SensorType.TEMPERATURE.value, unit="°C")
        alert = await IoTService._evaluate_thresholds(db, sensor, value=37.0)

        assert alert is not None
        assert alert.severity == AlertSeverity.CRITICAL.value
        assert sensor.status == SensorStatus.MAINTENANCE.value

    @pytest.mark.asyncio
    async def test_min_threshold_warning_alert(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()

        sensor = make_sensor(min_thresh=10.0, sensor_type=SensorType.POWER.value, unit="W")
        alert = await IoTService._evaluate_thresholds(db, sensor, value=8.0)

        assert alert is not None
        assert alert.alert_type == "THRESHOLD_BREACH_MIN"
        assert alert.severity == AlertSeverity.WARNING.value
        assert alert.metric_value == 8.0
        assert alert.threshold_value == 10.0

    @pytest.mark.asyncio
    async def test_min_threshold_critical_below_80_percent(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()

        # min=10, value=7 → 7 < 10*0.8=8 → CRITICAL
        sensor = make_sensor(min_thresh=10.0, sensor_type=SensorType.POWER.value, unit="W")
        alert = await IoTService._evaluate_thresholds(db, sensor, value=7.0)

        assert alert is not None
        assert alert.severity == AlertSeverity.CRITICAL.value
        assert sensor.status == SensorStatus.MAINTENANCE.value

    @pytest.mark.asyncio
    async def test_within_threshold_restores_online_status(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()

        sensor = make_sensor(min_thresh=5.0, max_thresh=40.0, sensor_type=SensorType.TEMPERATURE.value)
        sensor.status = SensorStatus.WARNING.value  # Was in warning
        alert = await IoTService._evaluate_thresholds(db, sensor, value=22.0)

        assert alert is None
        assert sensor.status == SensorStatus.ONLINE.value

    @pytest.mark.asyncio
    async def test_occupancy_sensor_updates_area_occupancy(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()

        area = make_area(capacity=50, occupancy=0)
        sensor = make_sensor(
            sensor_type=SensorType.OCCUPANCY.value, area=area, unit="persons"
        )
        alert = await IoTService._evaluate_thresholds(db, sensor, value=30.0)

        assert area.current_occupancy == 30
        assert area.status == AreaStatus.NORMAL.value
        assert alert is None  # Below capacity, no alert

    @pytest.mark.asyncio
    async def test_occupancy_sensor_exceeds_capacity_creates_critical_alert(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()

        area = make_area(capacity=50, occupancy=45)
        sensor = make_sensor(
            sensor_type=SensorType.OCCUPANCY.value, area=area, unit="persons"
        )
        alert = await IoTService._evaluate_thresholds(db, sensor, value=55.0)

        assert area.current_occupancy == 55
        assert area.status == AreaStatus.CRITICAL.value
        assert alert is not None
        assert alert.alert_type == "OCCUPANCY_EXCEEDED"
        assert alert.severity == AlertSeverity.CRITICAL.value


# ── Batch Ingestion ────────────────────────────────────────────────────────────

class TestBatchIngestion:
    @pytest.mark.asyncio
    async def test_batch_counts_match(self):
        org_id = 1
        events = [
            SensorReadingCreate(device_id="DEV-001", metric_type="OCCUPANCY", metric_value=20.0),
            SensorReadingCreate(device_id="DEV-002", metric_type="TEMPERATURE", metric_value=22.0),
            SensorReadingCreate(device_id="DEV-003", metric_type="POWER", metric_value=100.0),
        ]

        with patch.object(
            IoTService,
            "ingest_event",
            new=AsyncMock(return_value=(MagicMock(spec=SensorReading), None)),
        ):
            result = await IoTService.ingest_batch_events(
                db=AsyncMock(), org_id=org_id, events=events
            )

        assert result.readings_processed == 3
        assert result.alerts_generated == 0
        assert result.status == "SUCCESS"

    @pytest.mark.asyncio
    async def test_batch_counts_alerts(self):
        """
        Batch ingestion counts alert objects returned by ingest_event.
        We test the count only — Pydantic serialization of alerts is
        covered by the API layer tests. Here we verify the service's
        orchestration logic: readings_processed and alerts_generated counts.
        """
        org_id = 1
        events = [
            SensorReadingCreate(device_id="DEV-001", metric_type="TEMPERATURE", metric_value=80.0),
            SensorReadingCreate(device_id="DEV-002", metric_type="TEMPERATURE", metric_value=22.0),
        ]

        # Use a properly-populated InfrastructureAlert so Pydantic can
        # validate the IngestionResult.alerts list via from_attributes=True
        alert_stub = InfrastructureAlert(
            organization_id=org_id,
            device_id="DEV-001",
            alert_type="THRESHOLD_BREACH_MAX",
            severity=AlertSeverity.WARNING.value,
            message="High temperature: 80°C (Threshold: >75)",
            metric_value=80.0,
            threshold_value=75.0,
            condition_breached="Value 80 > Max 75",
            status=AlertStatus.ACTIVE.value,
            triggered_at=datetime.now(timezone.utc),
            recommended_action="Check cooling system",
        )

        # First call generates alert, second doesn't
        with patch.object(
            IoTService,
            "ingest_event",
            new=AsyncMock(
                side_effect=[
                    (MagicMock(spec=SensorReading), alert_stub),
                    (MagicMock(spec=SensorReading), None),
                ]
            ),
        ):
            result = await IoTService.ingest_batch_events(
                db=AsyncMock(), org_id=org_id, events=events
            )

        assert result.readings_processed == 2
        assert result.alerts_generated == 1

    @pytest.mark.asyncio
    async def test_batch_skips_unknown_device_error(self):
        org_id = 1
        events = [
            SensorReadingCreate(device_id="UNKNOWN-DEV", metric_type="OCCUPANCY", metric_value=10.0),
            SensorReadingCreate(device_id="DEV-001", metric_type="OCCUPANCY", metric_value=10.0),
        ]

        with patch.object(
            IoTService,
            "ingest_event",
            new=AsyncMock(
                side_effect=[
                    ValueError("Sensor device 'UNKNOWN-DEV' is not registered"),
                    (MagicMock(spec=SensorReading), None),
                ]
            ),
        ):
            result = await IoTService.ingest_batch_events(
                db=AsyncMock(), org_id=org_id, events=events
            )

        # Unknown device error skipped; valid reading counted
        assert result.readings_processed == 1


# ── Alert Lifecycle ────────────────────────────────────────────────────────────

class TestAlertLifecycle:
    @pytest.mark.asyncio
    async def test_acknowledge_alert_changes_status(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        alert = MagicMock(spec=InfrastructureAlert)
        alert.id = 5
        alert.organization_id = 1
        alert.status = AlertStatus.ACTIVE.value

        alert_result = MagicMock()
        alert_result.scalar_one_or_none.return_value = alert
        db.execute = AsyncMock(return_value=alert_result)

        user = make_user()

        with patch("app.services.iot_service.create_audit_log", new_callable=AsyncMock):
            result = await IoTService.acknowledge_alert(db, alert_id=5, org_id=1, user=user)

        assert result.status == AlertStatus.ACKNOWLEDGED.value

    @pytest.mark.asyncio
    async def test_resolve_alert_sets_resolved_fields(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        alert = MagicMock(spec=InfrastructureAlert)
        alert.id = 6
        alert.organization_id = 1
        alert.status = AlertStatus.ACTIVE.value
        alert.resolved_at = None
        alert.resolved_by_id = None
        alert.resolution_notes = None

        alert_result = MagicMock()
        alert_result.scalar_one_or_none.return_value = alert
        db.execute = AsyncMock(return_value=alert_result)

        user = make_user(uid=5)

        with patch("app.services.iot_service.create_audit_log", new_callable=AsyncMock):
            result = await IoTService.resolve_alert(
                db, alert_id=6, org_id=1, user=user,
                resolution_notes="Cooling unit repaired"
            )

        assert result.status == AlertStatus.RESOLVED.value
        assert result.resolved_by_id == 5
        assert result.resolution_notes == "Cooling unit repaired"

    @pytest.mark.asyncio
    async def test_acknowledge_missing_alert_raises(self):
        db = AsyncMock()
        no_result = MagicMock()
        no_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=no_result)

        user = make_user()
        with pytest.raises(ValueError, match="not found"):
            await IoTService.acknowledge_alert(db, alert_id=999, org_id=1, user=user)

    @pytest.mark.asyncio
    async def test_ingest_event_unknown_device_raises(self):
        db = AsyncMock()
        no_result = MagicMock()
        no_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=no_result)

        event = SensorReadingCreate(
            device_id="GHOST-DEVICE",
            metric_type="TEMPERATURE",
            metric_value=25.0,
        )

        with pytest.raises(ValueError, match="not registered"):
            await IoTService.ingest_event(db=db, org_id=1, event_in=event)
