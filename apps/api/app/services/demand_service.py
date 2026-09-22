from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.demand import Demand, DemandStatus, Approval, ApprovalStatus, RoutingMethod
from app.models.identity import User, Department
from app.schemas.demand import DemandCreate, DemandUpdate
from app.services.routing_service import routing_pipeline
from app.services.audit_service import AuditService


class DemandService:
    @staticmethod
    async def create_demand(
        db: AsyncSession,
        user: User,
        demand_in: DemandCreate,
    ) -> Demand:
        department_id = demand_in.department_id or user.department_id
        
        demand = Demand(
            organization_id=user.organization_id,
            requester_id=user.id,
            department_id=department_id,
            title=demand_in.title,
            description=demand_in.description,
            category=demand_in.category,
            estimated_amount=demand_in.estimated_amount,
            status=DemandStatus.DRAFT,
        )
        db.add(demand)
        await db.commit()
        await db.refresh(demand)

        # Audit log
        await AuditService.log_action(
            db=db,
            user=user,
            action="demand:create",
            resource_type="demand",
            resource_id=str(demand.id),
            new_values={
                "title": demand.title,
                "category": demand.category,
                "estimated_amount": demand.estimated_amount,
                "status": demand.status.value,
            }
        )
        
        return await DemandService.get_demand_by_id(db, demand.id, user.organization_id)

    @staticmethod
    async def get_demand_by_id(
        db: AsyncSession,
        demand_id: int,
        organization_id: int,
    ) -> Optional[Demand]:
        stmt = (
            select(Demand)
            .options(selectinload(Demand.approvals))
            .where(
                Demand.id == demand_id,
                Demand.organization_id == organization_id
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_demands(
        db: AsyncSession,
        organization_id: int,
        user_id: Optional[int] = None,
        department_id: Optional[int] = None,
        status: Optional[DemandStatus] = None,
    ) -> List[Demand]:
        stmt = (
            select(Demand)
            .options(selectinload(Demand.approvals))
            .where(Demand.organization_id == organization_id)
        )
        if user_id:
            stmt = stmt.where(Demand.requester_id == user_id)
        if department_id:
            stmt = stmt.where(Demand.department_id == department_id)
        if status:
            stmt = stmt.where(Demand.status == status)

        stmt = stmt.order_by(Demand.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def classify_demand(
        db: AsyncSession,
        user: User,
        demand_id: int,
    ) -> Demand:
        demand = await DemandService.get_demand_by_id(db, demand_id, user.organization_id)
        if not demand:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demand ticket not found")

        route_res = routing_pipeline.route_demand(demand.title, demand.description)
        
        demand.routed_department = route_res["routed_department"]
        demand.routing_confidence = route_res["confidence"]
        demand.routing_method = route_res["method"]
        demand.routing_explanation = route_res["explanation"]
        
        if demand.status == DemandStatus.DRAFT:
            demand.status = DemandStatus.CLASSIFIED
            
        await db.commit()
        await db.refresh(demand)

        await AuditService.log_action(
            db=db,
            user=user,
            action="demand:classify",
            resource_type="demand",
            resource_id=str(demand.id),
            new_values={
                "routed_department": demand.routed_department,
                "routing_confidence": demand.routing_confidence,
                "routing_method": demand.routing_method.value if demand.routing_method else None,
                "status": demand.status.value,
            }
        )

        return await DemandService.get_demand_by_id(db, demand.id, user.organization_id)

    @staticmethod
    async def submit_demand(
        db: AsyncSession,
        user: User,
        demand_id: int,
    ) -> Demand:
        demand = await DemandService.get_demand_by_id(db, demand_id, user.organization_id)
        if not demand:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demand ticket not found")

        if demand.status in [DemandStatus.SUBMITTED, DemandStatus.PENDING_APPROVAL, DemandStatus.APPROVED]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Demand is already in {demand.status.value} status")

        # Purchase limit verification against Department budget / purchase limit
        if demand.department_id:
            dept_res = await db.execute(select(Department).where(Department.id == demand.department_id))
            department = dept_res.scalar_one_or_none()
            if department and department.budget_limit > 0 and demand.estimated_amount > department.budget_limit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estimated amount (${demand.estimated_amount:,.2f}) exceeds department purchase limit (${department.budget_limit:,.2f})"
                )

        # Auto-classify if not classified yet
        if not demand.routed_department:
            route_res = routing_pipeline.route_demand(demand.title, demand.description)
            demand.routed_department = route_res["routed_department"]
            demand.routing_confidence = route_res["confidence"]
            demand.routing_method = route_res["method"]
            demand.routing_explanation = route_res["explanation"]

        demand.status = DemandStatus.PENDING_APPROVAL

        # Create Approval Record
        approval = Approval(
            demand_id=demand.id,
            status=ApprovalStatus.PENDING,
            comments="Demand submitted for approval"
        )
        db.add(approval)
        await db.commit()
        await db.refresh(demand)

        await AuditService.log_action(
            db=db,
            user=user,
            action="demand:submit",
            resource_type="demand",
            resource_id=str(demand.id),
            new_values={
                "status": demand.status.value,
                "estimated_amount": demand.estimated_amount,
                "routed_department": demand.routed_department,
            }
        )

        return await DemandService.get_demand_by_id(db, demand.id, user.organization_id)

    @staticmethod
    async def approve_demand(
        db: AsyncSession,
        user: User,
        demand_id: int,
        comments: Optional[str] = None,
    ) -> Demand:
        demand = await DemandService.get_demand_by_id(db, demand_id, user.organization_id)
        if not demand:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demand ticket not found")

        if demand.status != DemandStatus.PENDING_APPROVAL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot approve demand in state {demand.status.value}")

        demand.status = DemandStatus.APPROVED

        # Update pending approval entry or add new
        stmt = select(Approval).where(Approval.demand_id == demand.id, Approval.status == ApprovalStatus.PENDING)
        res = await db.execute(stmt)
        pending_approval = res.scalar_one_or_none()
        
        if pending_approval:
            pending_approval.status = ApprovalStatus.APPROVED
            pending_approval.approver_id = user.id
            pending_approval.comments = comments or "Approved by manager"
        else:
            approval = Approval(
                demand_id=demand.id,
                approver_id=user.id,
                status=ApprovalStatus.APPROVED,
                comments=comments or "Approved by manager"
            )
            db.add(approval)

        await db.commit()
        await db.refresh(demand)

        await AuditService.log_action(
            db=db,
            user=user,
            action="purchase:approve",
            resource_type="demand",
            resource_id=str(demand.id),
            new_values={
                "status": demand.status.value,
                "approver_id": user.id,
                "comments": comments,
            }
        )

        return await DemandService.get_demand_by_id(db, demand.id, user.organization_id)

    @staticmethod
    async def reject_demand(
        db: AsyncSession,
        user: User,
        demand_id: int,
        comments: Optional[str] = None,
    ) -> Demand:
        demand = await DemandService.get_demand_by_id(db, demand_id, user.organization_id)
        if not demand:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demand ticket not found")

        if demand.status != DemandStatus.PENDING_APPROVAL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot reject demand in state {demand.status.value}")

        demand.status = DemandStatus.REJECTED

        stmt = select(Approval).where(Approval.demand_id == demand.id, Approval.status == ApprovalStatus.PENDING)
        res = await db.execute(stmt)
        pending_approval = res.scalar_one_or_none()
        
        if pending_approval:
            pending_approval.status = ApprovalStatus.REJECTED
            pending_approval.approver_id = user.id
            pending_approval.comments = comments or "Rejected by manager"
        else:
            approval = Approval(
                demand_id=demand.id,
                approver_id=user.id,
                status=ApprovalStatus.REJECTED,
                comments=comments or "Rejected by manager"
            )
            db.add(approval)

        await db.commit()
        await db.refresh(demand)

        await AuditService.log_action(
            db=db,
            user=user,
            action="purchase:reject",
            resource_type="demand",
            resource_id=str(demand.id),
            new_values={
                "status": demand.status.value,
                "approver_id": user.id,
                "comments": comments,
            }
        )

        return await DemandService.get_demand_by_id(db, demand.id, user.organization_id)
