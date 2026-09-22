"""005_phase8_assets_iot

Revision ID: 005_phase8_assets_iot
Revises: 004_phase5_gstin_verification
Create Date: 2026-09-22 17:00:00.000000

Phase 8 — Asset Lifecycle & Physical Infrastructure / IoT Monitoring

Creates:
  - assets
  - asset_assignments
  - asset_returns
  - asset_reallocations
  - physical_areas
  - sensors
  - sensor_readings
  - infrastructure_alerts
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "005_phase8_assets_iot"
down_revision: Union[str, None] = "004_phase5_gstin_verification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ── Physical Areas ─────────────────────────────────────────────────────────
    op.create_table(
        "physical_areas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("building", sa.String(length=100), nullable=False),
        sa.Column("floor", sa.String(length=50), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("current_occupancy", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="NORMAL"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_physical_areas_id"), "physical_areas", ["id"], unique=False)
    op.create_index(op.f("ix_physical_areas_code"), "physical_areas", ["code"], unique=False)
    op.create_index(op.f("ix_physical_areas_status"), "physical_areas", ["status"], unique=False)

    # ── Assets ─────────────────────────────────────────────────────────────────
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("asset_tag", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="LAPTOP"),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("serial_number", sa.String(length=255), nullable=True),
        sa.Column("specifications", sa.JSON(), nullable=True),
        sa.Column("condition", sa.String(length=50), nullable=False, server_default="EXCELLENT"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="AVAILABLE"),
        sa.Column("purchase_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("purchase_price", sa.Float(), nullable=True),
        sa.Column("warranty_expiry", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expected_life_months", sa.Integer(), nullable=True, server_default="36"),
        sa.Column("current_assigned_user_id", sa.Integer(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("physical_area_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["current_assigned_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["physical_area_id"], ["physical_areas.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assets_id"), "assets", ["id"], unique=False)
    op.create_index(op.f("ix_assets_asset_tag"), "assets", ["asset_tag"], unique=True)
    op.create_index(op.f("ix_assets_category"), "assets", ["category"], unique=False)
    op.create_index(op.f("ix_assets_status"), "assets", ["status"], unique=False)
    op.create_index("ix_assets_org_status", "assets", ["organization_id", "status"])

    # ── Asset Assignments ──────────────────────────────────────────────────────
    op.create_table(
        "asset_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("demand_id", sa.Integer(), nullable=True),
        sa.Column("assigned_by_id", sa.Integer(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["demand_id"], ["demands.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assigned_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_asset_assignments_id"), "asset_assignments", ["id"], unique=False)
    op.create_index(op.f("ix_asset_assignments_asset_id"), "asset_assignments", ["asset_id"], unique=False)
    op.create_index(op.f("ix_asset_assignments_user_id"), "asset_assignments", ["user_id"], unique=False)

    # ── Asset Returns ──────────────────────────────────────────────────────────
    op.create_table(
        "asset_returns",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("returned_by_id", sa.Integer(), nullable=False),
        sa.Column("received_by_id", sa.Integer(), nullable=True),
        sa.Column("return_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("condition_on_return", sa.String(length=50), nullable=False, server_default="GOOD"),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("is_reusable", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["returned_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["received_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_asset_returns_id"), "asset_returns", ["id"], unique=False)
    op.create_index(op.f("ix_asset_returns_asset_id"), "asset_returns", ["asset_id"], unique=False)

    # ── Asset Reallocations ────────────────────────────────────────────────────
    op.create_table(
        "asset_reallocations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("demand_id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False, server_default="AVAILABLE_STOCK"),
        sa.Column("requested_by_id", sa.Integer(), nullable=False),
        sa.Column("approved_by_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PROPOSED"),
        sa.Column("reallocated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["demand_id"], ["demands.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_asset_reallocations_id"), "asset_reallocations", ["id"], unique=False)
    op.create_index(op.f("ix_asset_reallocations_asset_id"), "asset_reallocations", ["asset_id"], unique=False)
    op.create_index(op.f("ix_asset_reallocations_status"), "asset_reallocations", ["status"], unique=False)

    # ── Sensors ────────────────────────────────────────────────────────────────
    op.create_table(
        "sensors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("sensor_type", sa.String(length=50), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False, server_default="count"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ONLINE"),
        sa.Column("min_threshold", sa.Float(), nullable=True),
        sa.Column("max_threshold", sa.Float(), nullable=True),
        sa.Column("last_reading_value", sa.Float(), nullable=True),
        sa.Column("last_reading_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["area_id"], ["physical_areas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sensors_id"), "sensors", ["id"], unique=False)
    op.create_index(op.f("ix_sensors_device_id"), "sensors", ["device_id"], unique=True)
    op.create_index(op.f("ix_sensors_status"), "sensors", ["status"], unique=False)
    op.create_index(op.f("ix_sensors_sensor_type"), "sensors", ["sensor_type"], unique=False)

    # ── Sensor Readings ────────────────────────────────────────────────────────
    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("sensor_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=100), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metric_type", sa.String(length=50), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("quality", sa.String(length=50), nullable=False, server_default="GOOD"),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sensor_id"], ["sensors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sensor_readings_id"), "sensor_readings", ["id"], unique=False)
    op.create_index(op.f("ix_sensor_readings_sensor_id"), "sensor_readings", ["sensor_id"], unique=False)
    op.create_index(op.f("ix_sensor_readings_device_id"), "sensor_readings", ["device_id"], unique=False)
    op.create_index(op.f("ix_sensor_readings_timestamp"), "sensor_readings", ["timestamp"], unique=False)

    # ── Infrastructure Alerts ──────────────────────────────────────────────────
    op.create_table(
        "infrastructure_alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("sensor_id", sa.Integer(), nullable=True),
        sa.Column("area_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.String(length=100), nullable=True),
        sa.Column("alert_type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="WARNING"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=True),
        sa.Column("threshold_value", sa.Float(), nullable=True),
        sa.Column("condition_breached", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by_id", sa.Integer(), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("recommended_action", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sensor_id"], ["sensors.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["area_id"], ["physical_areas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolved_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_infrastructure_alerts_id"), "infrastructure_alerts", ["id"], unique=False)
    op.create_index(op.f("ix_infrastructure_alerts_status"), "infrastructure_alerts", ["status"], unique=False)
    op.create_index(op.f("ix_infrastructure_alerts_triggered_at"), "infrastructure_alerts", ["triggered_at"], unique=False)
    op.create_index("ix_infra_alerts_org_status", "infrastructure_alerts", ["organization_id", "status"])


def downgrade() -> None:
    op.drop_table("infrastructure_alerts")
    op.drop_table("sensor_readings")
    op.drop_table("sensors")
    op.drop_table("asset_reallocations")
    op.drop_table("asset_returns")
    op.drop_table("asset_assignments")
    op.drop_table("assets")
    op.drop_table("physical_areas")
