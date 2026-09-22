from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.identity import User
from app.schemas.assistant import (
    AssistantQueryRequest,
    AssistantQueryResponse,
    AssistantActionPreviewRequest,
    AssistantActionPreviewResponse,
)
from app.services.procurement_assistant import (
    execute_assistant_query,
    tool_preview_draft_purchase_request,
)

router = APIRouter(prefix="/assistant", tags=["Procurement AI Assistant"])


@router.post(
    "/query",
    response_model=AssistantQueryResponse,
    summary="Ask procurement assistant with RAG knowledge search and controlled tools",
)
async def query_procurement_assistant(
    request: AssistantQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await execute_assistant_query(
            db=db,
            organization_id=current_user.organization_id,
            user=current_user,
            query_text=request.query,
        )
        return AssistantQueryResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assistant processing failed: {str(e)}"
        )


@router.post(
    "/actions/preview",
    response_model=AssistantActionPreviewResponse,
    summary="Preview a draft purchase request without executing binding mutations",
)
async def preview_assistant_action(
    request: AssistantActionPreviewRequest,
    current_user: User = Depends(get_current_user),
):
    preview = tool_preview_draft_purchase_request(
        title=request.title,
        description=request.description,
        category=request.category,
        estimated_amount=request.estimated_amount,
        department=request.department,
        suggested_vendor=request.suggested_vendor,
    )
    return AssistantActionPreviewResponse(**preview)
