from fastapi import APIRouter
from app.api.v1 import (
    analytics,
    assistant,
    assets,
    audit,
    auth,
    demands,
    gstin,
    health,
    invoices,
    knowledge,
    metrics,
    physical,
    processes,
    users,
    vendors,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(metrics.router)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, tags=["Users & Organization"])
api_router.include_router(audit.router, tags=["Audit Log"])
api_router.include_router(demands.router, prefix="/demands", tags=["Demands"])
api_router.include_router(vendors.router, prefix="/vendors", tags=["Vendors"])
api_router.include_router(invoices.router, tags=["Invoices"])
api_router.include_router(gstin.router, tags=["GSTIN Verification"])
api_router.include_router(processes.router, tags=["Process Intelligence & Shadow Mining"])
api_router.include_router(assistant.router, tags=["Procurement AI Assistant"])
api_router.include_router(knowledge.router, tags=["Policy Knowledge Base & RAG"])
api_router.include_router(assets.router, tags=["Asset Lifecycle & Reallocation"])
api_router.include_router(physical.router, tags=["Physical Infrastructure & IoT"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Governance Reporting"])
