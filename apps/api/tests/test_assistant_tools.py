import pytest
from app.services.procurement_assistant import (
    tool_preview_draft_purchase_request,
)


def test_preview_draft_purchase_request_guardrail():
    preview = tool_preview_draft_purchase_request(
        title="10 Developer Laptops",
        description="High-performance laptops for engineering team",
        category="Technical",
        estimated_amount=1200000.0,
        department="Engineering",
        suggested_vendor="Dell Technologies",
    )
    
    assert preview["action_type"] == "DRAFT_PURCHASE_REQUEST"
    # STRICT GUARDRAIL: Must NOT be directly executable without human manager approval
    assert preview["is_executable"] is False
    assert "draft_data" in preview
    assert preview["draft_data"]["estimated_amount"] == 1200000.0
    assert "compliance_note" in preview
