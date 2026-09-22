import json
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.identity import User, Department
from app.models.demand import Vendor, Demand, DemandStatus
from app.models.knowledge import AssistantInteraction
from app.services.llm_gateway import llm_gateway
from app.services.rag_service import search_knowledge_base
from app.core.logging import logger


# --- Tool Definitions ---

async def tool_get_purchase_limit(
    db: AsyncSession,
    user: User,
    department_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Retrieve purchase authorization limits for the user and department."""
    dept_id = department_id or user.department_id
    dept_budget = 100000.0
    dept_name = "General Department"

    if dept_id:
        stmt = select(Department).where(Department.id == dept_id)
        res = await db.execute(stmt)
        dept = res.scalar_one_or_none()
        if dept:
            dept_budget = dept.budget_limit
            dept_name = dept.name

    role_limits = {
        "employee": 50000.0,
        "manager": 500000.0,
        "admin": 2500000.0,
    }
    user_single_tx_limit = role_limits.get(user.primary_role.lower(), 50000.0)

    return {
        "user_id": user.id,
        "user_name": user.full_name,
        "role": user.primary_role,
        "single_transaction_limit_inr": user_single_tx_limit,
        "department_id": dept_id,
        "department_name": dept_name,
        "department_budget_limit_inr": dept_budget,
        "approval_tiers": [
            {"tier": 1, "max_amount": 50000.0, "approver_role": "manager"},
            {"tier": 2, "max_amount": 500000.0, "approver_role": "department_head"},
            {"tier": 3, "max_amount": 2500000.0, "approver_role": "admin_or_vp"},
        ]
    }


async def tool_search_approved_vendors(
    db: AsyncSession,
    organization_id: int,
    category: Optional[str] = None,
    region: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search registered and approved vendors for the organization."""
    stmt = select(Vendor).where(
        Vendor.organization_id == organization_id,
        Vendor.status == "ACTIVE",
    )
    if category and category.lower() != "all":
        stmt = stmt.where(Vendor.category.ilike(f"%{category}%"))
    if region and region.lower() != "all":
        stmt = stmt.where(Vendor.region.ilike(f"%{region}%"))

    res = await db.execute(stmt)
    vendors = res.scalars().all()

    return [
        {
            "id": v.id,
            "name": v.name,
            "category": v.category,
            "region": v.region,
            "rating": v.rating,
            "gstin": v.gstin,
            "status": v.status,
        }
        for v in vendors
    ]


async def tool_get_recent_prices(
    db: AsyncSession,
    organization_id: int,
    item_keyword: str,
) -> Dict[str, Any]:
    """Retrieve historical benchmark pricing for items."""
    # Deterministic price benchmarks and historical demands
    stmt = select(Demand).where(
        Demand.organization_id == organization_id,
        Demand.title.ilike(f"%{item_keyword}%"),
    ).order_by(Demand.created_at.desc()).limit(5)
    
    res = await db.execute(stmt)
    demands = res.scalars().all()

    historical_prices = [
        {
            "demand_id": d.id,
            "title": d.title,
            "estimated_amount": d.estimated_amount,
            "status": d.status.value if hasattr(d.status, "value") else str(d.status),
            "date": d.created_at.isoformat(),
        }
        for d in demands
    ]

    # Benchmark estimates
    benchmark_catalog = {
        "laptop": 85000.0,
        "macbook": 165000.0,
        "server": 350000.0,
        "monitor": 18000.0,
        "gpu": 120000.0,
        "router": 25000.0,
        "license": 15000.0,
    }
    suggested_unit_price = 50000.0
    for k, v in benchmark_catalog.items():
        if k in item_keyword.lower():
            suggested_unit_price = v
            break

    return {
        "item_query": item_keyword,
        "suggested_benchmark_price_inr": suggested_unit_price,
        "historical_records": historical_prices,
    }


async def tool_get_asset_reuse_candidates(
    db: AsyncSession,
    organization_id: int,
    item_name: str,
) -> List[Dict[str, Any]]:
    """Identify existing unassigned or returned assets available for reallocation."""
    # Mock asset recovery registry matching requirements
    mock_assets = [
        {"id": 101, "asset_tag": "AST-LAP-042", "model": "Dell Latitude 5420", "condition": "EXCELLENT", "status": "AVAILABLE", "location": "Bangalore Office Warehouse"},
        {"id": 102, "asset_tag": "AST-MON-019", "model": "Dell 27-inch 4K Monitor", "condition": "LIKE_NEW", "status": "AVAILABLE", "location": "Mumbai IT Depot"},
        {"id": 103, "asset_tag": "AST-SVR-007", "model": "HPE ProLiant DL380 Server", "condition": "REFURBISHED", "status": "AVAILABLE", "location": "Chennai Data Center"},
    ]
    matches = []
    item_lower = item_name.lower()
    for a in mock_assets:
        if any(term in a["model"].lower() for term in item_lower.split()):
            matches.append(a)
    return matches


def tool_preview_draft_purchase_request(
    title: str,
    description: str,
    category: str,
    estimated_amount: float,
    department: Optional[str] = None,
    suggested_vendor: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a non-binding draft purchase request specification."""
    return {
        "action_type": "DRAFT_PURCHASE_REQUEST",
        "is_executable": False,  # Strict Guardrail: Assistant cannot auto-execute final orders
        "draft_data": {
            "title": title,
            "description": description,
            "category": category,
            "estimated_amount": estimated_amount,
            "department": department or "Technical",
            "suggested_vendor": suggested_vendor or "Approved Vendor",
            "status": "DRAFT",
        },
        "compliance_note": "This draft requires human manager sign-off prior to PO generation.",
    }


# --- Assistant Query Orchestration ---

async def execute_assistant_query(
    db: AsyncSession,
    organization_id: int,
    user: User,
    query_text: str,
) -> Dict[str, Any]:
    """
    Main assistant pipeline:
    1. Search policy knowledge base via RAG.
    2. Determine needed tools (limits, vendors, prices, asset reuse).
    3. Generate grounded response with citations.
    4. Guardrails: No direct SQL or autonomous binding approvals.
    5. Log interaction audit trail.
    """
    executed_tools: List[Dict[str, Any]] = []
    citations: List[str] = []
    action_proposals: List[Dict[str, Any]] = []
    q_lower = query_text.lower()

    # 1. RAG Search for Policy Context
    try:
        rag_chunks = await search_knowledge_base(
            db=db,
            organization_id=organization_id,
            query=query_text,
            top_k=3,
        )
        for rc in rag_chunks:
            citations.append(rc.get("citation", ""))
    except Exception as e:
        logger.warning(f"RAG search error (ignoring for resilience): {e}")
        rag_chunks = []

    # 2. Tool Execution Logic based on query intent
    context_for_llm: Dict[str, Any] = {
        "user_role": getattr(user, "primary_role", "admin"),
        "chunks": rag_chunks,
    }

    try:
        if any(k in q_lower for k in ["limit", "budget", "tier", "approval", "policy", "can i buy"]):
            limit_data = await tool_get_purchase_limit(db, user)
            executed_tools.append({"tool": "get_purchase_limit", "output": limit_data})
            context_for_llm["limits"] = limit_data

        if any(k in q_lower for k in ["vendor", "supplier", "seller"]):
            vendor_data = await tool_search_approved_vendors(db, organization_id)
            executed_tools.append({"tool": "search_approved_vendors", "count": len(vendor_data)})
            context_for_llm["vendors"] = vendor_data

        if any(k in q_lower for k in ["price", "cost", "estimate", "rate", "how much"]):
            item_term = query_text
            for word in ["price", "cost", "of", "what", "is", "the", "for"]:
                item_term = item_term.replace(word, "")
            price_data = await tool_get_recent_prices(db, organization_id, item_term.strip())
            executed_tools.append({"tool": "get_recent_prices", "output": price_data})
            context_for_llm["pricing"] = price_data

        if any(k in q_lower for k in ["reuse", "existing asset", "warehouse", "reallocate"]):
            asset_matches = await tool_get_asset_reuse_candidates(db, organization_id, query_text)
            executed_tools.append({"tool": "get_asset_reuse_candidates", "matches": len(asset_matches)})
            context_for_llm["reusable_assets"] = asset_matches
    except Exception as e:
        logger.warning(f"Tool execution warning: {e}")

    if any(k in q_lower for k in ["draft", "create request", "raise po", "order"]):
        draft_action = tool_preview_draft_purchase_request(
            title=f"Purchase Request: {query_text[:50]}",
            description=query_text,
            category="Technical" if "laptop" in q_lower or "server" in q_lower else "General",
            estimated_amount=85000.0,
        )
        action_proposals.append(draft_action)

    # 3. LLM Synthesis via Gateway
    generation = await llm_gateway.generate_response(
        prompt_id="procurement_assistant/v1",
        user_message=query_text,
        context_data=context_for_llm,
    )

    answer_text = generation["response"]

    # Append citations if RAG chunks were used and not already included
    if citations and "According to" not in answer_text:
        answer_text += "\n\n**Sources & Policy Citations:**\n" + "\n".join([f"- {c}" for c in citations if c])

    # 4. Log Interaction for Audit & Provenance (best-effort)
    try:
        interaction = AssistantInteraction(
            organization_id=organization_id,
            user_id=getattr(user, "id", 1),
            prompt=query_text,
            response=answer_text,
            model_version=generation["model_version"],
            prompt_version=generation["prompt_version"],
            tool_calls=executed_tools,
            citations=citations,
            action_proposals=action_proposals,
            latency_ms=generation["latency_ms"],
        )
        db.add(interaction)
        await db.commit()
    except Exception as e:
        logger.warning(f"Interaction log warning (skipped): {e}")

    return {
        "answer": answer_text,
        "citations": citations,
        "tool_calls": executed_tools,
        "action_proposals": action_proposals,
        "model_version": generation["model_version"],
        "prompt_version": generation["prompt_version"],
        "latency_ms": generation["latency_ms"],
        "provider": generation["provider"],
    }
