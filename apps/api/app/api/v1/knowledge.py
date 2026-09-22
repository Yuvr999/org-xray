from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, RequirePermission
from app.models.identity import User
from app.models.knowledge import KnowledgeDocument
from app.schemas.knowledge import (
    KnowledgeIngestRequest,
    KnowledgeDocumentResponse,
    KnowledgeSearchResult,
)
from app.services.rag_service import (
    ingest_policy_document,
    search_knowledge_base,
)

router = APIRouter(prefix="/knowledge", tags=["Policy Knowledge Base & RAG"])


@router.post(
    "/ingest",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a policy document into the knowledge base",
)
async def ingest_document(
    request: KnowledgeIngestRequest,
    current_user: User = Depends(RequirePermission("admin:configure")),
    db: AsyncSession = Depends(get_db),
):
    doc = await ingest_policy_document(
        db=db,
        organization_id=current_user.organization_id,
        title=request.title,
        content=request.content,
        category=request.category,
        version=request.version,
        source_filename=request.source_filename,
        description=request.description,
    )
    return KnowledgeDocumentResponse(
        id=doc.id,
        title=doc.title,
        category=doc.category,
        version=doc.version,
        source_filename=doc.source_filename,
        description=doc.description,
        is_active=doc.is_active,
        created_at=doc.created_at,
        chunk_count=len(doc.chunks) if doc.chunks else 0,
    )


@router.get(
    "/documents",
    response_model=List[KnowledgeDocumentResponse],
    summary="List active policy documents in organization knowledge base",
)
async def list_knowledge_documents(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(KnowledgeDocument)
        .where(
            KnowledgeDocument.organization_id == current_user.organization_id,
            KnowledgeDocument.is_active == True,
        )
        .options(selectinload(KnowledgeDocument.chunks))
    )
    if category:
        stmt = stmt.where(KnowledgeDocument.category == category)
        
    res = await db.execute(stmt)
    docs = res.scalars().all()
    
    return [
        KnowledgeDocumentResponse(
            id=d.id,
            title=d.title,
            category=d.category,
            version=d.version,
            source_filename=d.source_filename,
            description=d.description,
            is_active=d.is_active,
            created_at=d.created_at,
            chunk_count=len(d.chunks),
        )
        for d in docs
    ]


@router.get(
    "/search",
    response_model=List[KnowledgeSearchResult],
    summary="Search knowledge base with citation provenance",
)
async def search_knowledge(
    q: str = Query(..., min_length=2, description="Search query"),
    top_k: int = Query(4, ge=1, le=10),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chunks = await search_knowledge_base(
        db=db,
        organization_id=current_user.organization_id,
        query=q,
        top_k=top_k,
        category_filter=category,
    )
    return [KnowledgeSearchResult(**c) for c in chunks]
