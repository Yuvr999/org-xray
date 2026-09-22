"""002_phase3_demand_procurement

Revision ID: 002_phase3_demand_procurement
Revises: 001_phase2_identity_rbac
Create Date: 2026-09-22 15:22:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_phase3_demand_procurement'
down_revision: Union[str, None] = '001_phase2_identity_rbac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Demands
    op.create_table(
        'demands',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False, server_default='General'),
        sa.Column('estimated_amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('routed_department', sa.String(length=100), nullable=True),
        sa.Column('routing_confidence', sa.Float(), nullable=True),
        sa.Column('routing_method', sa.String(length=50), nullable=True),
        sa.Column('routing_explanation', sa.Text(), nullable=True),
        sa.Column('matched_asset_id', sa.Integer(), nullable=True),
        sa.Column('ai_recommendation', sa.Text(), nullable=True),
        sa.Column('suggested_action', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demands_id'), 'demands', ['id'], unique=False)

    # 2. Approvals
    op.create_table(
        'approvals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('demand_id', sa.Integer(), nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['demand_id'], ['demands.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_approvals_id'), 'approvals', ['id'], unique=False)

    # 3. Vendors
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=False, server_default='National'),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('rating', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('gstin', sa.String(length=20), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vendors_id'), 'vendors', ['id'], unique=False)
    op.create_index(op.f('ix_vendors_name'), 'vendors', ['name'], unique=False)
    op.create_index(op.f('ix_vendors_category'), 'vendors', ['category'], unique=False)
    op.create_index(op.f('ix_vendors_region'), 'vendors', ['region'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_vendors_region'), table_name='vendors')
    op.drop_index(op.f('ix_vendors_category'), table_name='vendors')
    op.drop_index(op.f('ix_vendors_name'), table_name='vendors')
    op.drop_index(op.f('ix_vendors_id'), table_name='vendors')
    op.drop_table('vendors')

    op.drop_index(op.f('ix_approvals_id'), table_name='approvals')
    op.drop_table('approvals')

    op.drop_index(op.f('ix_demands_id'), table_name='demands')
    op.drop_table('demands')
