"""005_phase7_knowledge_assistant

Revision ID: 005_phase7_knowledge_assistant
Revises: 004_phase5_gstin_verification
Create Date: 2026-09-22 17:30:00.000000

Creates three new tables for the Phase 7 Procurement Assistant & Knowledge Base:
  - knowledge_documents  : versioned policy/catalog documents per organization
  - knowledge_chunks     : chunked text segments with keyword index for RAG retrieval
  - assistant_interactions : full audit log of every LLM-backed assistant query

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005_phase7_knowledge_assistant'
down_revision: Union[str, None] = '004_phase5_gstin_verification'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Knowledge Documents
    op.create_table(
        'knowledge_documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False, server_default='policy'),
        sa.Column('source_filename', sa.String(length=255), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=False, server_default='v1.0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_knowledge_documents_id'), 'knowledge_documents', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_documents_title'), 'knowledge_documents', ['title'], unique=False)
    op.create_index(op.f('ix_knowledge_documents_category'), 'knowledge_documents', ['category'], unique=False)
    op.create_index(op.f('ix_knowledge_documents_organization_id'), 'knowledge_documents', ['organization_id'], unique=False)

    # 2. Knowledge Chunks
    op.create_table(
        'knowledge_chunks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('section_title', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('keywords_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['knowledge_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_knowledge_chunks_id'), 'knowledge_chunks', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_chunks_document_id'), 'knowledge_chunks', ['document_id'], unique=False)
    op.create_index('ix_chunks_doc_index', 'knowledge_chunks', ['document_id', 'chunk_index'], unique=False)

    # 3. Assistant Interactions (full audit log)
    op.create_table(
        'assistant_interactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('model_version', sa.String(length=100), nullable=False, server_default='gemini-1.5-flash'),
        sa.Column('prompt_version', sa.String(length=100), nullable=False, server_default='procurement_assistant/v1'),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('citations', sa.JSON(), nullable=True),
        sa.Column('action_proposals', sa.JSON(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_assistant_interactions_id'), 'assistant_interactions', ['id'], unique=False)
    op.create_index(op.f('ix_assistant_interactions_organization_id'), 'assistant_interactions', ['organization_id'], unique=False)
    op.create_index(op.f('ix_assistant_interactions_user_id'), 'assistant_interactions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_assistant_interactions_user_id'), table_name='assistant_interactions')
    op.drop_index(op.f('ix_assistant_interactions_organization_id'), table_name='assistant_interactions')
    op.drop_index(op.f('ix_assistant_interactions_id'), table_name='assistant_interactions')
    op.drop_table('assistant_interactions')

    op.drop_index('ix_chunks_doc_index', table_name='knowledge_chunks')
    op.drop_index(op.f('ix_knowledge_chunks_document_id'), table_name='knowledge_chunks')
    op.drop_index(op.f('ix_knowledge_chunks_id'), table_name='knowledge_chunks')
    op.drop_table('knowledge_chunks')

    op.drop_index(op.f('ix_knowledge_documents_organization_id'), table_name='knowledge_documents')
    op.drop_index(op.f('ix_knowledge_documents_category'), table_name='knowledge_documents')
    op.drop_index(op.f('ix_knowledge_documents_title'), table_name='knowledge_documents')
    op.drop_index(op.f('ix_knowledge_documents_id'), table_name='knowledge_documents')
    op.drop_table('knowledge_documents')
