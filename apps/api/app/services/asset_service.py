from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.asset import (
    Asset,
    AssetAssignment,
    AssetCategory,
    AssetCondition,
    AssetReallocation,
    AssetReturn,
    AssetStatus,
    ReallocationStatus,
)
from app.models.demand import Demand, DemandStatus
from app.models.identity import User
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    ReuseRecommendationItem,
    ReuseRecommendationResponse,
)
from app.services.audit_service import create_audit_log


def utc_now():
    return datetime.now(timezone.utc)


class AssetService:
    @staticmethod
    async def create_asset(
        db: AsyncSession,
        org_id: int,
        asset_in: AssetCreate,
        creator: Optional[User] = None,
    ) -> Asset:
        asset = Asset(
            organization_id=org_id,
            asset_tag=asset_in.asset_tag,
            name=asset_in.name,
            category=asset_in.category.value if hasattr(asset_in.category, "value") else str(asset_in.category),
            model=asset_in.model,
            serial_number=asset_in.serial_number,
            specifications=asset_in.specifications or {},
            condition=asset_in.condition.value if hasattr(asset_in.condition, "value") else str(asset_in.condition),
            status=AssetStatus.AVAILABLE.value,
            purchase_date=asset_in.purchase_date,
            purchase_price=asset_in.purchase_price,
            warranty_expiry=asset_in.warranty_expiry,
            expected_life_months=asset_in.expected_life_months,
            department_id=asset_in.department_id,
            physical_area_id=asset_in.physical_area_id,
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        if creator:
            await create_audit_log(
                db=db,
                organization_id=org_id,
                user_id=creator.id,
                action="ASSET_CREATED",
                resource_type="asset",
                resource_id=str(asset.id),
                new_values={
                    "asset_tag": asset.asset_tag,
                    "name": asset.name,
                    "category": asset.category,
                    "condition": asset.condition,
                },
            )
        return asset

    @staticmethod
    async def get_asset_by_id(
        db: AsyncSession,
        asset_id: int,
        org_id: int,
        load_details: bool = False,
    ) -> Optional[Asset]:
        query = select(Asset).where(Asset.id == asset_id, Asset.organization_id == org_id)
        if load_details:
            query = query.options(
                selectinload(Asset.assignments),
                selectinload(Asset.returns),
                selectinload(Asset.reallocations),
            )
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_assets(
        db: AsyncSession,
        org_id: int,
        category: Optional[str] = None,
        status: Optional[str] = None,
        condition: Optional[str] = None,
        department_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Asset]:
        query = select(Asset).where(Asset.organization_id == org_id)
        if category:
            query = query.where(Asset.category == category)
        if status:
            query = query.where(Asset.status == status)
        if condition:
            query = query.where(Asset.condition == condition)
        if department_id:
            query = query.where(Asset.department_id == department_id)

        query = query.order_by(desc(Asset.created_at)).limit(limit).offset(offset)
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def update_asset(
        db: AsyncSession,
        asset: Asset,
        update_in: AssetUpdate,
        updater: Optional[User] = None,
    ) -> Asset:
        old_values = {
            "name": asset.name,
            "category": asset.category,
            "condition": asset.condition,
            "status": asset.status,
        }
        update_data = update_in.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            if hasattr(asset, key):
                if hasattr(val, "value"):
                    setattr(asset, key, val.value)
                else:
                    setattr(asset, key, val)
        asset.updated_at = utc_now()
        await db.commit()
        await db.refresh(asset)

        if updater:
            await create_audit_log(
                db=db,
                organization_id=asset.organization_id,
                user_id=updater.id,
                action="ASSET_UPDATED",
                resource_type="asset",
                resource_id=str(asset.id),
                old_values=old_values,
                new_values={k: getattr(asset, k) for k in old_values.keys()},
            )
        return asset

    @staticmethod
    async def assign_asset(
        db: AsyncSession,
        asset: Asset,
        user_id: int,
        assigned_by: User,
        department_id: Optional[int] = None,
        demand_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> AssetAssignment:
        old_status = asset.status
        old_assigned = asset.current_assigned_user_id

        # Update Asset state
        asset.status = AssetStatus.ASSIGNED.value
        asset.current_assigned_user_id = user_id
        if department_id:
            asset.department_id = department_id
        asset.updated_at = utc_now()

        # Create Assignment record
        assignment = AssetAssignment(
            organization_id=asset.organization_id,
            asset_id=asset.id,
            user_id=user_id,
            department_id=department_id or asset.department_id,
            demand_id=demand_id,
            assigned_by_id=assigned_by.id,
            assigned_at=utc_now(),
            notes=notes,
        )
        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        await create_audit_log(
            db=db,
            organization_id=asset.organization_id,
            user_id=assigned_by.id,
            action="ASSET_ASSIGNED",
            resource_type="asset",
            resource_id=str(asset.id),
            old_values={"status": old_status, "current_assigned_user_id": old_assigned},
            new_values={
                "status": asset.status,
                "current_assigned_user_id": user_id,
                "assignment_id": assignment.id,
                "demand_id": demand_id,
            },
        )
        return assignment

    @staticmethod
    async def return_asset(
        db: AsyncSession,
        asset: Asset,
        returned_by_id: int,
        received_by: User,
        condition: str = AssetCondition.GOOD.value,
        reason: Optional[str] = None,
        is_reusable: bool = True,
        notes: Optional[str] = None,
    ) -> AssetReturn:
        old_status = asset.status
        old_assigned = asset.current_assigned_user_id

        # Close open assignment records
        open_assignments_stmt = (
            select(AssetAssignment)
            .where(AssetAssignment.asset_id == asset.id, AssetAssignment.returned_at.is_(None))
        )
        open_res = await db.execute(open_assignments_stmt)
        for open_assign in open_res.scalars().all():
            open_assign.returned_at = utc_now()

        # Update Asset state based on condition & reusability
        asset.current_assigned_user_id = None
        asset.condition = condition
        if condition in [AssetCondition.DAMAGED.value, AssetCondition.POOR.value] or not is_reusable:
            asset.status = AssetStatus.UNDER_MAINTENANCE.value
        else:
            asset.status = AssetStatus.AVAILABLE.value
        asset.updated_at = utc_now()

        # Create AssetReturn record
        asset_return = AssetReturn(
            organization_id=asset.organization_id,
            asset_id=asset.id,
            returned_by_id=returned_by_id,
            received_by_id=received_by.id,
            return_date=utc_now(),
            condition_on_return=condition,
            reason=reason,
            is_reusable=is_reusable,
            notes=notes,
        )
        db.add(asset_return)
        await db.commit()
        await db.refresh(asset_return)

        await create_audit_log(
            db=db,
            organization_id=asset.organization_id,
            user_id=received_by.id,
            action="ASSET_RETURNED",
            resource_type="asset",
            resource_id=str(asset.id),
            old_values={"status": old_status, "current_assigned_user_id": old_assigned},
            new_values={
                "status": asset.status,
                "condition": condition,
                "return_id": asset_return.id,
                "is_reusable": is_reusable,
            },
        )
        return asset_return

    @staticmethod
    async def recommend_assets_for_demand(
        db: AsyncSession,
        org_id: int,
        demand_id: Optional[int] = None,
        category: Optional[str] = None,
        required_specs: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> ReuseRecommendationResponse:
        target_category = category
        target_demand: Optional[Demand] = None

        if demand_id:
            d_stmt = select(Demand).where(Demand.id == demand_id, Demand.organization_id == org_id)
            d_res = await db.execute(d_stmt)
            target_demand = d_res.scalar_one_or_none()
            if target_demand and not target_category:
                # Infer target category from demand title or category
                text = f"{target_demand.title} {target_demand.category}".upper()
                if "LAPTOP" in text or "MACBOOK" in text or "THINKPAD" in text or "DELL" in text:
                    target_category = AssetCategory.LAPTOP.value
                elif "MONITOR" in text or "DISPLAY" in text or "SCREEN" in text:
                    target_category = AssetCategory.MONITOR.value
                elif "SERVER" in text or "RACK" in text:
                    target_category = AssetCategory.SERVER.value
                elif "NETWORK" in text or "ROUTER" in text or "SWITCH" in text:
                    target_category = AssetCategory.NETWORK.value
                elif "CHAIR" in text:
                    target_category = AssetCategory.CHAIR.value
                elif "DESK" in text:
                    target_category = AssetCategory.DESK.value
                else:
                    target_category = AssetCategory.LAPTOP.value

        # Fetch candidate assets in AVAILABLE or RETURNED status, excluding POOR/DAMAGED/RETIRED
        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == org_id,
                Asset.status.in_([AssetStatus.AVAILABLE.value, AssetStatus.RETURNED.value]),
                Asset.condition.in_([
                    AssetCondition.EXCELLENT.value,
                    AssetCondition.GOOD.value,
                    AssetCondition.FAIR.value,
                ]),
            )
        )
        candidates_res = await db.execute(stmt)
        candidates = list(candidates_res.scalars().all())

        scored_recommendations: List[ReuseRecommendationItem] = []

        for candidate in candidates:
            score, breakdown, reasons = AssetService._calculate_reuse_score(
                candidate=candidate,
                target_category=target_category,
                target_demand=target_demand,
                required_specs=required_specs,
            )
            scored_recommendations.append(
                ReuseRecommendationItem(
                    asset_id=candidate.id,
                    asset_tag=candidate.asset_tag,
                    name=candidate.name,
                    category=candidate.category,
                    model=candidate.model,
                    condition=candidate.condition,
                    status=candidate.status,
                    specifications=candidate.specifications,
                    department_id=candidate.department_id,
                    score=round(score, 1),
                    score_breakdown=breakdown,
                    match_reasons=reasons,
                )
            )

        # Sort descending by score
        scored_recommendations.sort(key=lambda x: x.score, reverse=True)
        top_recommendations = scored_recommendations[:limit]

        return ReuseRecommendationResponse(
            demand_id=demand_id,
            target_category=target_category,
            candidates_evaluated=len(candidates),
            recommendations=top_recommendations,
        )

    @staticmethod
    def _calculate_reuse_score(
        candidate: Asset,
        target_category: Optional[str],
        target_demand: Optional[Demand],
        required_specs: Optional[Dict[str, Any]],
    ) -> Tuple[float, Dict[str, float], List[str]]:
        breakdown: Dict[str, float] = {}
        reasons: List[str] = []

        # 1. Category Compatibility (Max 40 pts)
        if target_category:
            if candidate.category.upper() == target_category.upper():
                cat_score = 40.0
                reasons.append(f"Direct category match for {candidate.category}")
            else:
                cat_score = 10.0
                reasons.append(f"Cross-category candidate ({candidate.category} vs requested {target_category})")
        else:
            cat_score = 30.0
            reasons.append("General available asset candidate")
        breakdown["category_compatibility"] = cat_score

        # 2. Asset Condition (Max 25 pts)
        cond_map = {
            AssetCondition.EXCELLENT.value: 25.0,
            AssetCondition.GOOD.value: 20.0,
            AssetCondition.FAIR.value: 12.0,
            AssetCondition.POOR.value: 0.0,
            AssetCondition.DAMAGED.value: 0.0,
        }
        cond_score = cond_map.get(candidate.condition, 15.0)
        reasons.append(f"Physical condition is {candidate.condition} (+{cond_score} pts)")
        breakdown["condition_rating"] = cond_score

        # 3. Technical Specifications Compatibility (Max 25 pts)
        spec_score = 20.0  # default baseline
        specs = candidate.specifications or {}
        if required_specs:
            matched_criteria = 0
            total_criteria = len(required_specs)
            for req_k, req_v in required_specs.items():
                cand_v = specs.get(req_k)
                if cand_v is not None:
                    if isinstance(req_v, (int, float)) and isinstance(cand_v, (int, float)):
                        if cand_v >= req_v:
                            matched_criteria += 1
                    elif str(req_v).lower() in str(cand_v).lower():
                        matched_criteria += 1
            if total_criteria > 0:
                spec_score = round(25.0 * (matched_criteria / total_criteria), 1)
                reasons.append(f"Matched {matched_criteria}/{total_criteria} required technical specifications")
        else:
            if specs:
                spec_score = 25.0
                reasons.append("Complete verified hardware specification on record")
            else:
                spec_score = 18.0
                reasons.append("Standard hardware profile")
        breakdown["specifications_match"] = spec_score

        # 4. Lifecycle & Proximity (Max 10 pts)
        lifecycle_score = 8.0
        if target_demand and target_demand.department_id and candidate.department_id == target_demand.department_id:
            lifecycle_score = 10.0
            reasons.append("Located within the same department — immediate zero-freight availability")
        else:
            reasons.append("Available in central organizational stock pool")
        breakdown["lifecycle_and_locality"] = lifecycle_score

        total_score = min(100.0, cat_score + cond_score + spec_score + lifecycle_score)
        return total_score, breakdown, reasons

    @staticmethod
    async def propose_reallocation(
        db: AsyncSession,
        org_id: int,
        asset_id: int,
        demand_id: int,
        requester: User,
        source_type: str = "AVAILABLE_STOCK",
        notes: Optional[str] = None,
    ) -> AssetReallocation:
        asset = await AssetService.get_asset_by_id(db, asset_id=asset_id, org_id=org_id)
        if not asset:
            raise ValueError("Asset not found")
        if asset.status not in [AssetStatus.AVAILABLE.value, AssetStatus.RETURNED.value]:
            raise ValueError(f"Asset is currently '{asset.status}' and cannot be reallocated")

        # Verify demand exists
        d_stmt = select(Demand).where(Demand.id == demand_id, Demand.organization_id == org_id)
        d_res = await db.execute(d_stmt)
        demand = d_res.scalar_one_or_none()
        if not demand:
            raise ValueError("Demand request not found")

        reallocation = AssetReallocation(
            organization_id=org_id,
            asset_id=asset_id,
            demand_id=demand_id,
            source_type=source_type,
            requested_by_id=requester.id,
            status=ReallocationStatus.PROPOSED.value,
            notes=notes,
        )
        db.add(reallocation)
        await db.commit()
        await db.refresh(reallocation)

        await create_audit_log(
            db=db,
            organization_id=org_id,
            user_id=requester.id,
            action="ASSET_REALLOCATION_PROPOSED",
            resource_type="asset_reallocation",
            resource_id=str(reallocation.id),
            new_values={
                "asset_id": asset_id,
                "demand_id": demand_id,
                "status": reallocation.status,
            },
        )
        return reallocation

    @staticmethod
    async def decide_reallocation(
        db: AsyncSession,
        org_id: int,
        reallocation_id: int,
        decider: User,
        decision: str,
        notes: Optional[str] = None,
    ) -> AssetReallocation:
        stmt = (
            select(AssetReallocation)
            .where(
                AssetReallocation.id == reallocation_id,
                AssetReallocation.organization_id == org_id,
            )
            .options(
                selectinload(AssetReallocation.asset),
                selectinload(AssetReallocation.demand),
            )
        )
        res = await db.execute(stmt)
        reallocation = res.scalar_one_or_none()
        if not reallocation:
            raise ValueError("Reallocation request not found")
        if reallocation.status != ReallocationStatus.PROPOSED.value:
            raise ValueError(f"Reallocation is already '{reallocation.status}' and cannot be decided")

        reallocation.approved_by_id = decider.id
        reallocation.reallocated_at = utc_now()
        if notes:
            reallocation.notes = (reallocation.notes or "") + f" | Decision notes: {notes}"

        asset = reallocation.asset
        demand = reallocation.demand

        if decision.upper() == "APPROVE":
            reallocation.status = ReallocationStatus.APPROVED.value
            
            # Execute transactional ownership assignment
            asset.status = AssetStatus.ASSIGNED.value
            demand_recipient = demand.requester_id if demand else decider.id
            asset.current_assigned_user_id = demand_recipient
            if demand and demand.department_id:
                asset.department_id = demand.department_id
            asset.updated_at = utc_now()

            # Create assignment entry
            assignment = AssetAssignment(
                organization_id=org_id,
                asset_id=asset.id,
                user_id=demand_recipient,
                department_id=demand.department_id if demand else None,
                demand_id=demand.id if demand else None,
                assigned_by_id=decider.id,
                assigned_at=utc_now(),
                notes=f"Reallocated via approved request #{reallocation.id}",
            )
            db.add(assignment)

            # Update demand status if applicable to avoid duplicate purchase order
            if demand:
                demand.status = DemandStatus.APPROVED.value
                demand.updated_at = utc_now()

            reallocation.status = ReallocationStatus.COMPLETED.value

            await create_audit_log(
                db=db,
                organization_id=org_id,
                user_id=decider.id,
                action="ASSET_REALLOCATION_APPROVED",
                resource_type="asset_reallocation",
                resource_id=str(reallocation.id),
                new_values={
                    "status": reallocation.status,
                    "asset_id": asset.id,
                    "new_assigned_user_id": asset.current_assigned_user_id,
                    "demand_id": demand.id if demand else None,
                },
            )
        else:
            reallocation.status = ReallocationStatus.REJECTED.value
            await create_audit_log(
                db=db,
                organization_id=org_id,
                user_id=decider.id,
                action="ASSET_REALLOCATION_REJECTED",
                resource_type="asset_reallocation",
                resource_id=str(reallocation.id),
                new_values={"status": reallocation.status, "reason": notes},
            )

        await db.commit()
        await db.refresh(reallocation)
        return reallocation
