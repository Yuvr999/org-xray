from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeIngestRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: str = Field(..., min_length=20, description="Full text or policy documentation to ingest")
    category: str = Field("policy", description="Category: policy, approval_matrix, vendor_list, catalog, sop")
    version: str = Field("v1.0", max_length=50)
    source_filename: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class KnowledgeDocumentResponse(BaseModel):
    id: int
    title: str
    category: str
    version: str
    source_filename: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    chunk_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    category: str
    version: str
    section_title: Optional[str] = None
    content: str
    score: float
    citation: str
