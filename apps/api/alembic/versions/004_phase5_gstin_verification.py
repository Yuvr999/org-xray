"""004_phase5_gstin_verification

Revision ID: 004_phase5_gstin_verification
Revises: 003_phase4_invoice_intelligence
Create Date: 2026-09-22 15:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_phase5_gstin_verification'
down_revision: Union[str, None] = '003_phase4_invoice_intelligence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'gstin_verifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('requested_by_id', sa.Integer(), nullable=True),
        sa.Column('gstin', sa.String(length=20), nullable=False),
        sa.Column('is_format_valid', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_checksum_valid', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_live_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('legal_name', sa.String(length=500), nullable=True),
        sa.Column('trade_name', sa.String(length=500), nullable=True),
        sa.Column('state_code', sa.String(length=10), nullable=True),
        sa.Column('taxpayer_type', sa.String(length=100), nullable=True),
        sa.Column('provider_name', sa.String(length=100), nullable=True),
        sa.Column('raw_response', sa.JSON(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gstin_verifications_id'), 'gstin_verifications', ['id'], unique=False)
    op.create_index(op.f('ix_gstin_verifications_gstin'), 'gstin_verifications', ['gstin'], unique=False)
    op.create_index(op.f('ix_gstin_verifications_status'), 'gstin_verifications', ['status'], unique=False)
    op.create_index(op.f('ix_gstin_verifications_organization_id'), 'gstin_verifications', ['organization_id'], unique=False)
    op.create_index('ix_gstin_verifications_org_gstin', 'gstin_verifications', ['organization_id', 'gstin'])


def downgrade() -> None:
    op.drop_table('gstin_verifications')
