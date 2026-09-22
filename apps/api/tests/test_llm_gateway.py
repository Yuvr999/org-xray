import pytest
from app.core.prompts import get_prompt_template, PROMPT_REGISTRY
from app.services.llm_gateway import llm_gateway


def test_prompt_registry_lookups():
    assert "procurement_assistant/v1" in PROMPT_REGISTRY
    assert "policy_rag/v1" in PROMPT_REGISTRY
    assert "demand_classifier/v1" in PROMPT_REGISTRY
    assert "action_proposal/v1" in PROMPT_REGISTRY

    spec = get_prompt_template("procurement_assistant/v1")
    assert "system_prompt" in spec
    assert "COMPLIANCE GUARDRAILS" in spec["system_prompt"]


def test_prompt_registry_invalid_key():
    with pytest.raises(KeyError):
        get_prompt_template("non_existent_prompt/v99")


@pytest.mark.asyncio
async def test_llm_gateway_fallback_generation():
    result = await llm_gateway.generate_response(
        prompt_id="procurement_assistant/v1",
        user_message="What is my purchase approval limit?",
    )
    assert "response" in result
    assert "model_version" in result
    assert "prompt_version" in result
    assert result["prompt_version"] == "procurement_assistant/v1"
    assert "latency_ms" in result
    assert result["latency_ms"] >= 0
    assert len(result["response"]) > 10


@pytest.mark.asyncio
async def test_llm_gateway_rag_synthesis_fallback():
    mock_context = {
        "chunks": [
            {
                "document_title": "IT Procurement Policy 2026",
                "section_title": "Hardware Refresh",
                "content": "Laptops may be replaced after 36 months of active service upon manager approval.",
            }
        ]
    }
    result = await llm_gateway.generate_response(
        prompt_id="policy_rag/v1",
        user_message="When can I get a laptop replaced?",
        context_data=mock_context,
    )
    assert "IT Procurement Policy 2026" in result["response"]
    assert "Hardware Refresh" in result["response"]
