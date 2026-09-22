"""003_phase4_invoice_intelligence

Revision ID: 003_phase4_invoice_intelligence
Revises: 002_phase3_demand_procurement
Create Date: 2026-09-22 15:53:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_phase4_invoice_intelligence'
down_revision: Union[str, None] = '002_phase3_demand_procurement'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Invoices
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='UPLOADED'),
        sa.Column('vendor_name', sa.String(length=500), nullable=True),
        sa.Column('vendor_gstin', sa.String(length=20), nullable=True),
        sa.Column('invoice_number', sa.String(length=255), nullable=True),
        sa.Column('invoice_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'),
        sa.Column('po_reference', sa.String(length=255), nullable=True),
        sa.Column('subtotal', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_tax', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('grand_total', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('extraction_confidence', sa.Float(), nullable=True),
        sa.Column('extraction_method', sa.String(length=50), nullable=True),
        sa.Column('document_hash', sa.String(length=128), nullable=True),
        sa.Column('reviewed_by_id', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)
    op.create_index(op.f('ix_invoices_status'), 'invoices', ['status'], unique=False)
    op.create_index(op.f('ix_invoices_vendor_gstin'), 'invoices', ['vendor_gstin'], unique=False)
    op.create_index(op.f('ix_invoices_invoice_number'), 'invoices', ['invoice_number'], unique=False)
    op.create_index(op.f('ix_invoices_document_hash'), 'invoices', ['document_hash'], unique=False)
    op.create_index(op.f('ix_invoices_organization_id'), 'invoices', ['organization_id'], unique=False)
    op.create_index('ix_invoices_org_status', 'invoices', ['organization_id', 'status'])
    op.create_index('ix_invoices_vendor_gstin_number', 'invoices', ['vendor_gstin', 'invoice_number'])

    # 2. Invoice Items
    op.create_table(
        'invoice_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('hsn_code', sa.String(length=20), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('unit_price', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('taxable_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('tax_rate', sa.Float(), nullable=True),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_items_id'), 'invoice_items', ['id'], unique=False)
    op.create_index(op.f('ix_invoice_items_invoice_id'), 'invoice_items', ['invoice_id'], unique=False)

    # 3. Invoice Documents
    op.create_table(
        'invoice_documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(length=500), nullable=False),
        sa.Column('stored_path', sa.String(length=1000), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('file_hash', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_documents_id'), 'invoice_documents', ['id'], unique=False)
    op.create_index(op.f('ix_invoice_documents_invoice_id'), 'invoice_documents', ['invoice_id'], unique=False)

    # 4. Invoice Extractions
    op.create_table(
        'invoice_extractions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('extraction_method', sa.String(length=50), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('extracted_fields', sa.JSON(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(length=100), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_extractions_id'), 'invoice_extractions', ['id'], unique=False)
    op.create_index(op.f('ix_invoice_extractions_invoice_id'), 'invoice_extractions', ['invoice_id'], unique=False)

    # 5. Invoice Validation Results
    op.create_table(
        'invoice_validation_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('rule_name', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='info'),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_validation_results_id'), 'invoice_validation_results', ['id'], unique=False)
    op.create_index(op.f('ix_invoice_validation_results_invoice_id'), 'invoice_validation_results', ['invoice_id'], unique=False)

    # 6. Invoice Duplicate Candidates
    op.create_table(
        'invoice_duplicate_candidates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('candidate_invoice_id', sa.Integer(), nullable=False),
        sa.Column('match_type', sa.String(length=50), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['candidate_invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_duplicate_candidates_id'), 'invoice_duplicate_candidates', ['id'], unique=False)
    op.create_index(op.f('ix_invoice_duplicate_candidates_invoice_id'), 'invoice_duplicate_candidates', ['invoice_id'], unique=False)
    op.create_index('ix_dup_candidates_pair', 'invoice_duplicate_candidates', ['invoice_id', 'candidate_invoice_id'], unique=True)

    # 7. Invoice Duplicate Decisions
    op.create_table(
        'invoice_duplicate_decisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('decided_by_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['candidate_id'], ['invoice_duplicate_candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['decided_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_duplicate_decisions_id'), 'invoice_duplicate_decisions', ['id'], unique=False)
    op.create_index(op.f('ix_invoice_duplicate_decisions_invoice_id'), 'invoice_duplicate_decisions', ['invoice_id'], unique=False)


def downgrade() -> None:
    op.drop_table('invoice_duplicate_decisions')
    op.drop_table('invoice_duplicate_candidates')
    op.drop_table('invoice_validation_results')
    op.drop_table('invoice_extractions')
    op.drop_table('invoice_documents')
    op.drop_table('invoice_items')
    op.drop_table('invoices')
