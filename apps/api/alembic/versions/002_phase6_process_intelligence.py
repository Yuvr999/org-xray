"""002_phase6_process_intelligence

Revision ID: 002_phase6_process_intelligence
Revises: 001_phase2_identity_rbac
Create Date: 2026-09-22 15:33:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_phase6_process_intelligence'
down_revision: Union[str, None] = '001_phase2_identity_rbac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Process Definitions
    op.create_table(
        'process_definitions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('expected_activities', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_process_definitions_code'), 'process_definitions', ['code'], unique=False)
    op.create_index(op.f('ix_process_definitions_id'), 'process_definitions', ['id'], unique=False)

    # 2. Process Events
    op.create_table(
        'process_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(length=100), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('actor_role', sa.String(length=50), nullable=False, server_default='employee'),
        sa.Column('source_system', sa.String(length=100), nullable=False),
        sa.Column('process_name', sa.String(length=255), nullable=False),
        sa.Column('activity', sa.String(length=100), nullable=False),
        sa.Column('activity_category', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('object_id', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('correlation_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_process_events_activity'), 'process_events', ['activity'], unique=False)
    op.create_index(op.f('ix_process_events_case_id'), 'process_events', ['case_id'], unique=False)
    op.create_index(op.f('ix_process_events_id'), 'process_events', ['id'], unique=False)
    op.create_index(op.f('ix_process_events_process_name'), 'process_events', ['process_name'], unique=False)
    op.create_index(op.f('ix_process_events_source_system'), 'process_events', ['source_system'], unique=False)
    op.create_index(op.f('ix_process_events_timestamp'), 'process_events', ['timestamp'], unique=False)

    # 3. Process Cases
    op.create_table(
        'process_cases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(length=100), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('process_name', sa.String(length=255), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('variant_hash', sa.String(length=64), nullable=True),
        sa.Column('shadow_score', sa.Float(), nullable=True),
        sa.Column('anomaly_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_process_cases_case_id'), 'process_cases', ['case_id'], unique=True)
    op.create_index(op.f('ix_process_cases_id'), 'process_cases', ['id'], unique=False)

    # 4. Shadow Alerts
    op.create_table(
        'shadow_alerts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('alert_code', sa.String(length=50), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.String(length=100), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('process_name', sa.String(length=255), nullable=False),
        sa.Column('unapproved_tool', sa.String(length=255), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('estimated_leakage', sa.String(length=100), nullable=False),
        sa.Column('shadow_score', sa.Float(), nullable=False),
        sa.Column('score_band', sa.String(length=50), nullable=False),
        sa.Column('deviation_component', sa.Float(), nullable=False),
        sa.Column('recurrence_component', sa.Float(), nullable=False),
        sa.Column('consistency_component', sa.Float(), nullable=False),
        sa.Column('cross_system_component', sa.Float(), nullable=False),
        sa.Column('business_risk_component', sa.Float(), nullable=False),
        sa.Column('ml_anomaly_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Flagged'),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shadow_alerts_alert_code'), 'shadow_alerts', ['alert_code'], unique=True)
    op.create_index(op.f('ix_shadow_alerts_case_id'), 'shadow_alerts', ['case_id'], unique=False)
    op.create_index(op.f('ix_shadow_alerts_department'), 'shadow_alerts', ['department'], unique=False)
    op.create_index(op.f('ix_shadow_alerts_detected_at'), 'shadow_alerts', ['detected_at'], unique=False)
    op.create_index(op.f('ix_shadow_alerts_id'), 'shadow_alerts', ['id'], unique=False)
    op.create_index(op.f('ix_shadow_alerts_severity'), 'shadow_alerts', ['severity'], unique=False)
    op.create_index(op.f('ix_shadow_alerts_status'), 'shadow_alerts', ['status'], unique=False)

    # 5. Shadow Feedback
    op.create_table(
        'shadow_feedback',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('alert_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('feedback_label', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['alert_id'], ['shadow_alerts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shadow_feedback_id'), 'shadow_feedback', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_shadow_feedback_id'), table_name='shadow_feedback')
    op.drop_table('shadow_feedback')
    op.drop_index(op.f('ix_shadow_alerts_status'), table_name='shadow_alerts')
    op.drop_index(op.f('ix_shadow_alerts_severity'), table_name='shadow_alerts')
    op.drop_index(op.f('ix_shadow_alerts_id'), table_name='shadow_alerts')
    op.drop_index(op.f('ix_shadow_alerts_detected_at'), table_name='shadow_alerts')
    op.drop_index(op.f('ix_shadow_alerts_department'), table_name='shadow_alerts')
    op.drop_index(op.f('ix_shadow_alerts_case_id'), table_name='shadow_alerts')
    op.drop_index(op.f('ix_shadow_alerts_alert_code'), table_name='shadow_alerts')
    op.drop_table('shadow_alerts')
    op.drop_index(op.f('ix_process_cases_id'), table_name='process_cases')
    op.drop_index(op.f('ix_process_cases_case_id'), table_name='process_cases')
    op.drop_table('process_cases')
    op.drop_index(op.f('ix_process_events_timestamp'), table_name='process_events')
    op.drop_index(op.f('ix_process_events_source_system'), table_name='process_events')
    op.drop_index(op.f('ix_process_events_process_name'), table_name='process_events')
    op.drop_index(op.f('ix_process_events_id'), table_name='process_events')
    op.drop_index(op.f('ix_process_events_case_id'), table_name='process_events')
    op.drop_index(op.f('ix_process_events_activity'), table_name='process_events')
    op.drop_table('process_events')
    op.drop_index(op.f('ix_process_definitions_id'), table_name='process_definitions')
    op.drop_index(op.f('ix_process_definitions_code'), table_name='process_definitions')
    op.drop_table('process_definitions')
