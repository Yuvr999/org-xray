import re
import math
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.core.logging import logger


def clean_text(text: str) -> str:
    """Normalize text whitespace and characters."""
    return re.sub(r'\s+', ' ', text).strip()


def extract_keywords(text: str) -> List[str]:
    """Extract significant lowercase keywords for keyword-based ranking."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stopwords = {
        "the", "and", "for", "with", "this", "that", "from", "are", "was", "will",
        "has", "have", "had", "can", "could", "should", "would", "which", "each", "into"
    }
    return list({w for w in words if w not in stopwords})


def chunk_document_text(text: str, chunk_size_words: int = 150) -> List[Dict[str, Any]]:
    """
    Split text into logical section-aware chunks.
    Preserves section headers denoted with '#' or capital headers.
    """
    lines = text.split("\n")
    chunks: List[Dict[str, Any]] = []
    
    current_section = "General Policy"
    current_words: List[str] = []
    chunk_index = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Detect section header
        if stripped.startswith("#") or (len(stripped) < 60 and stripped.isupper()):
            # If we already have accumulated words, emit previous chunk
            if current_words:
                content = " ".join(current_words)
                chunks.append({
                    "chunk_index": chunk_index,
                    "section_title": current_section,
                    "content": content,
                    "token_count": len(current_words),
                    "keywords": extract_keywords(content),
                })
                chunk_index += 1
                current_words = []
            current_section = stripped.lstrip("#").strip()
            continue

        words = stripped.split()
        current_words.extend(words)

        if len(current_words) >= chunk_size_words:
            content = " ".join(current_words)
            chunks.append({
                "chunk_index": chunk_index,
                "section_title": current_section,
                "content": content,
                "token_count": len(current_words),
                "keywords": extract_keywords(content),
            })
            chunk_index += 1
            current_words = []

    if current_words:
        content = " ".join(current_words)
        chunks.append({
            "chunk_index": chunk_index,
            "section_title": current_section,
            "content": content,
            "token_count": len(current_words),
            "keywords": extract_keywords(content),
        })

    return chunks


async def ingest_policy_document(
    db: AsyncSession,
    organization_id: int,
    title: str,
    content: str,
    category: str = "policy",
    version: str = "v1.0",
    source_filename: Optional[str] = None,
    description: Optional[str] = None,
) -> KnowledgeDocument:
    """
    Ingest a document into the organization's knowledge base and create structured chunks.
    """
    doc = KnowledgeDocument(
        organization_id=organization_id,
        title=title,
        category=category,
        version=version,
        source_filename=source_filename,
        description=description,
    )
    db.add(doc)
    await db.flush()

    raw_chunks = chunk_document_text(content)
    for c_info in raw_chunks:
        chunk = KnowledgeChunk(
            document_id=doc.id,
            chunk_index=c_info["chunk_index"],
            section_title=c_info["section_title"],
            content=c_info["content"],
            token_count=c_info["token_count"],
            keywords_json=c_info["keywords"],
        )
        db.add(chunk)

    await db.commit()
    await db.refresh(doc)
    logger.info(f"Ingested KnowledgeDocument #{doc.id} ('{doc.title}') with {len(raw_chunks)} chunks.")
    return doc


async def search_knowledge_base(
    db: AsyncSession,
    organization_id: int,
    query: str,
    top_k: int = 4,
    category_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve top relevant knowledge chunks matching the query with citation provenance.
    """
    query_keywords = set(extract_keywords(query))
    if not query_keywords:
        query_keywords = set(query.lower().split())

    stmt = (
        select(KnowledgeChunk)
        .join(KnowledgeDocument)
        .where(
            KnowledgeDocument.organization_id == organization_id,
            KnowledgeDocument.is_active == True,
        )
        .options(selectinload(KnowledgeChunk.document))
    )

    if category_filter:
        stmt = stmt.where(KnowledgeDocument.category == category_filter)

    result = await db.execute(stmt)
    chunks = result.scalars().all()

    # Score chunks based on keyword term frequency and section title matches
    scored_chunks: List[Dict[str, Any]] = []
    
    for chk in chunks:
        score = 0.0
        content_lower = chk.content.lower()
        section_lower = (chk.section_title or "").lower()
        
        # Check keyword matches
        for kw in query_keywords:
            if kw in content_lower:
                score += 1.0
            if kw in section_lower:
                score += 2.0  # Higher weight for section title relevance

        if score > 0:
            citation_label = f"[{chk.document.title} - Section: {chk.section_title or 'General'} (Chunk #{chk.chunk_index})]"
            scored_chunks.append({
                "chunk_id": chk.id,
                "document_id": chk.document_id,
                "document_title": chk.document.title,
                "category": chk.document.category,
                "version": chk.document.version,
                "section_title": chk.section_title,
                "content": chk.content,
                "score": round(score, 2),
                "citation": citation_label,
            })

    # Sort descending by relevance score
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_k]
