"""
Phase 8 – Asset Lifecycle & Reuse Recommendation Tests

Tests:
  - Asset creation, retrieval, listing, update
  - Asset assignment transaction
  - Asset return + status transitions (AVAILABLE vs UNDER_MAINTENANCE)
  - Reuse recommendation scoring (category match, condition weight, spec matching, department locality)
  - Reallocation proposal and approval workflow (PROPOSED → COMPLETED, audited)
  - Reallocation rejection workflow
  - Reject reallocation of non-available asset
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

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
from app.models.demand import Demand, DemandStatus, RoutingMethod
from app.models.identity import User
from app.schemas.asset import AssetCreate, AssetUpdate, AssetReturnCreate
from app.services.asset_service import AssetService


def make_user(
    uid=1, org_id=1, email="admin@test.com", role="admin",
    dept_id=None, is_superuser=True
) -> User:
    u = MagicMock(spec=User)
    u.id = uid
    u.organization_id = org_id
    u.email = email
    u.primary_role = role
    u.department_id = dept_id
    u.is_superuser = is_superuser
    u.is_active = True
    return u


def make_asset(
    asset_id=1,
    org_id=1,
    tag="ASSET-001",
    name="Dell Laptop",
    category=AssetCategory.LAPTOP.value,
    condition=AssetCondition.EXCELLENT.value,
    status=AssetStatus.AVAILABLE.value,
    dept_id=None,
    specs=None,
    assigned_user_id=None,
) -> Asset:
    a = MagicMock(spec=Asset)
    a.id = asset_id
    a.organization_id = org_id
    a.asset_tag = tag
    a.name = name
    a.category = category
    a.condition = condition
    a.status = status
    a.department_id = dept_id
    a.specifications = specs or {}
    a.current_assigned_user_id = assigned_user_id
    a.model = None
    a.serial_number = None
    a.purchase_price = None
    a.warranty_expiry = None
    a.expected_life_months = 36
    a.physical_area_id = None
    a.assignments = []
    a.returns = []
    a.reallocations = []
    return a


def make_demand(
    demand_id=10, org_id=1, user_id=2, dept_id=5,
    title="Laptop request", status=DemandStatus.DRAFT.value
) -> Demand:
    d = MagicMock(spec=Demand)
    d.id = demand_id
    d.organization_id = org_id
    # Demand uses requester_id not user_id in the model but service uses demand.user_id as alias
    d.user_id = user_id
    d.requester_id = user_id
    d.department_id = dept_id
    d.title = title
    d.category = "Technical"
    d.status = status
    d.routing_method = RoutingMethod.RULE
    d.updated_at = datetime.now(timezone.utc)
    return d


# ── Asset Scoring ──────────────────────────────────────────────────────────────

class TestReuseRecommendationScoring:
    def _score(self, asset, category=None, demand=None, specs=None):
        score, breakdown, reasons = AssetService._calculate_reuse_score(
            candidate=asset,
            target_category=category,
            target_demand=demand,
            required_specs=specs,
        )
        return score, breakdown, reasons

    def test_perfect_match_same_category_excellent_condition(self):
        asset = make_asset(
            category=AssetCategory.LAPTOP.value,
            condition=AssetCondition.EXCELLENT.value,
            dept_id=5,
            specs={"ram_gb": 16, "storage_gb": 512},
        )
        demand = make_demand(dept_id=5)
        score, breakdown, reasons = self._score(asset, category="LAPTOP", demand=demand)

        assert score >= 90.0, f"Expected score >=90, got {score}"
        assert breakdown["category_compatibility"] == 40.0
        assert breakdown["condition_rating"] == 25.0
        # Same department → max lifecycle bonus
        assert breakdown["lifecycle_and_locality"] == 10.0

    def test_category_mismatch_reduces_score(self):
        asset = make_asset(
            category=AssetCategory.MONITOR.value,
            condition=AssetCondition.GOOD.value,
        )
        score, breakdown, _ = self._score(asset, category="LAPTOP")
        assert breakdown["category_compatibility"] == 10.0
        assert score < 70.0

    def test_good_condition_scores_less_than_excellent(self):
        excellent = make_asset(condition=AssetCondition.EXCELLENT.value)
        good = make_asset(condition=AssetCondition.GOOD.value)
        s_exc, _, _ = self._score(excellent, category="LAPTOP")
        s_good, _, _ = self._score(good, category="LAPTOP")
        assert s_exc > s_good

    def test_fair_condition_scores_less_than_good(self):
        good = make_asset(condition=AssetCondition.GOOD.value)
        fair = make_asset(condition=AssetCondition.FAIR.value)
        s_good, _, _ = self._score(good, category="LAPTOP")
        s_fair, _, _ = self._score(fair, category="LAPTOP")
        assert s_good > s_fair

    def test_spec_matching_full_match(self):
        asset = make_asset(
            category=AssetCategory.LAPTOP.value,
            condition=AssetCondition.EXCELLENT.value,
            specs={"ram_gb": 16, "storage_gb": 512, "cpu": "i7"},
        )
        required = {"ram_gb": 16, "storage_gb": 256, "cpu": "i7"}
        score, breakdown, reasons = self._score(asset, category="LAPTOP", specs=required)
        assert breakdown["specifications_match"] == 25.0
        assert "3/3" in " ".join(reasons)

    def test_spec_matching_partial_match(self):
        asset = make_asset(
            category=AssetCategory.LAPTOP.value,
            specs={"ram_gb": 8, "storage_gb": 512},
        )
        required = {"ram_gb": 16, "storage_gb": 256}
        _, breakdown, reasons = self._score(asset, category="LAPTOP", specs=required)
        # ram_gb 8 < 16 = no match; storage 512 >= 256 = match → 1/2
        assert breakdown["specifications_match"] == pytest.approx(12.5, abs=0.1)

    def test_no_spec_requirements_gets_baseline(self):
        asset = make_asset(specs={"ram_gb": 16})
        _, breakdown, _ = self._score(asset, category="LAPTOP")
        # Has specs but no requirement → baseline 25
        assert breakdown["specifications_match"] == 25.0

    def test_different_department_gets_lower_lifecycle_score(self):
        asset = make_asset(dept_id=99)
        demand = make_demand(dept_id=5)
        _, breakdown, _ = self._score(asset, category="LAPTOP", demand=demand)
        assert breakdown["lifecycle_and_locality"] == 8.0

    def test_score_capped_at_100(self):
        asset = make_asset(
            category=AssetCategory.LAPTOP.value,
            condition=AssetCondition.EXCELLENT.value,
            dept_id=5,
            specs={"ram_gb": 32},
        )
        demand = make_demand(dept_id=5)
        score, _, _ = self._score(
            asset,
            category="LAPTOP",
            demand=demand,
            specs={"ram_gb": 16},
        )
        assert score <= 100.0


# ── Asset Service (async mock) ─────────────────────────────────────────────────

class TestAssetServiceAsync:
    @pytest.mark.asyncio
    async def test_create_asset_returns_asset(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()

        asset_in = AssetCreate(
            asset_tag="ASSET-TEST-001",
            name="Test Laptop",
            category=AssetCategory.LAPTOP,
            condition=AssetCondition.EXCELLENT,
        )
        user = make_user()

        # db.refresh must set asset.id so audit log str() doesn't fail
        async def mock_refresh(obj):
            obj.id = 1
            obj.asset_tag = "ASSET-TEST-001"
            obj.name = "Test Laptop"
            obj.category = "LAPTOP"
            obj.condition = "EXCELLENT"

        db.refresh = mock_refresh

        with patch("app.services.asset_service.create_audit_log", new_callable=AsyncMock) as mock_audit:
            await AssetService.create_asset(db=db, org_id=1, asset_in=asset_in, creator=user)

            db.add.assert_called_once()
            db.commit.assert_called()
            mock_audit.assert_called_once()
            audit_kwargs = mock_audit.call_args.kwargs
            assert audit_kwargs["action"] == "ASSET_CREATED"
            assert audit_kwargs["resource_type"] == "asset"

    @pytest.mark.asyncio
    async def test_return_asset_sets_available_for_good_condition(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        asset = make_asset(
            status=AssetStatus.ASSIGNED.value,
            assigned_user_id=2,
            condition=AssetCondition.EXCELLENT.value,
        )

        # Mock open assignment query
        open_result = MagicMock()
        open_result.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=open_result)

        receiver = make_user(uid=3)

        with patch("app.services.asset_service.create_audit_log", new_callable=AsyncMock):
            await AssetService.return_asset(
                db=db,
                asset=asset,
                returned_by_id=2,
                received_by=receiver,
                condition=AssetCondition.GOOD.value,
                is_reusable=True,
            )

        assert asset.status == AssetStatus.AVAILABLE.value
        assert asset.current_assigned_user_id is None

    @pytest.mark.asyncio
    async def test_return_damaged_asset_sets_under_maintenance(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        asset = make_asset(
            status=AssetStatus.ASSIGNED.value,
            assigned_user_id=2,
        )

        open_result = MagicMock()
        open_result.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=open_result)

        receiver = make_user(uid=3)

        with patch("app.services.asset_service.create_audit_log", new_callable=AsyncMock):
            await AssetService.return_asset(
                db=db,
                asset=asset,
                returned_by_id=2,
                received_by=receiver,
                condition=AssetCondition.DAMAGED.value,
                is_reusable=False,
            )

        assert asset.status == AssetStatus.UNDER_MAINTENANCE.value

    @pytest.mark.asyncio
    async def test_propose_reallocation_rejects_assigned_asset(self):
        db = AsyncMock()

        asset = make_asset(status=AssetStatus.ASSIGNED.value)

        # get_asset_by_id mock
        get_result = MagicMock()
        get_result.scalar_one_or_none.return_value = asset
        db.execute = AsyncMock(return_value=get_result)

        requester = make_user()

        with pytest.raises(ValueError, match="cannot be reallocated"):
            await AssetService.propose_reallocation(
                db=db,
                org_id=1,
                asset_id=1,
                demand_id=10,
                requester=requester,
            )

    @pytest.mark.asyncio
    async def test_decide_reallocation_approve_completes(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        asset = make_asset(status=AssetStatus.AVAILABLE.value)
        demand = make_demand()

        reallocation = MagicMock(spec=AssetReallocation)
        reallocation.id = 1
        reallocation.organization_id = 1
        reallocation.asset_id = 1
        reallocation.demand_id = 10
        reallocation.status = ReallocationStatus.PROPOSED.value
        reallocation.asset = asset
        reallocation.demand = demand
        reallocation.notes = None

        get_result = MagicMock()
        get_result.scalar_one_or_none.return_value = reallocation
        db.execute = AsyncMock(return_value=get_result)

        decider = make_user(uid=3, role="manager")

        with patch("app.services.asset_service.create_audit_log", new_callable=AsyncMock):
            result = await AssetService.decide_reallocation(
                db=db,
                org_id=1,
                reallocation_id=1,
                decider=decider,
                decision="APPROVE",
            )

        assert result.status == ReallocationStatus.COMPLETED.value
        assert asset.status == AssetStatus.ASSIGNED.value
        # Asset should now be assigned to the demand's requester
        assert asset.current_assigned_user_id == demand.requester_id

    @pytest.mark.asyncio
    async def test_decide_reallocation_reject_sets_rejected(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        asset = make_asset(status=AssetStatus.AVAILABLE.value)
        demand = make_demand()

        reallocation = MagicMock(spec=AssetReallocation)
        reallocation.id = 2
        reallocation.organization_id = 1
        reallocation.asset_id = 1
        reallocation.demand_id = 10
        reallocation.status = ReallocationStatus.PROPOSED.value
        reallocation.asset = asset
        reallocation.demand = demand
        reallocation.notes = None

        get_result = MagicMock()
        get_result.scalar_one_or_none.return_value = reallocation
        db.execute = AsyncMock(return_value=get_result)

        decider = make_user(uid=3, role="manager")

        with patch("app.services.asset_service.create_audit_log", new_callable=AsyncMock):
            result = await AssetService.decide_reallocation(
                db=db,
                org_id=1,
                reallocation_id=2,
                decider=decider,
                decision="REJECT",
                notes="Insufficient justification",
            )

        assert result.status == ReallocationStatus.REJECTED.value
        # Asset should remain AVAILABLE — not changed on rejection
        assert asset.status == AssetStatus.AVAILABLE.value

    @pytest.mark.asyncio
    async def test_decide_reallocation_already_decided_raises(self):
        db = AsyncMock()

        reallocation = MagicMock(spec=AssetReallocation)
        reallocation.status = ReallocationStatus.COMPLETED.value

        get_result = MagicMock()
        get_result.scalar_one_or_none.return_value = reallocation
        db.execute = AsyncMock(return_value=get_result)

        decider = make_user()

        with pytest.raises(ValueError, match="cannot be decided"):
            await AssetService.decide_reallocation(
                db=db,
                org_id=1,
                reallocation_id=1,
                decider=decider,
                decision="APPROVE",
            )

    @pytest.mark.asyncio
    async def test_recommendations_sorted_by_score_descending(self):
        db = AsyncMock()

        assets_data = [
            make_asset(
                asset_id=1, category=AssetCategory.MONITOR.value, condition=AssetCondition.FAIR.value
            ),
            make_asset(
                asset_id=2, category=AssetCategory.LAPTOP.value, condition=AssetCondition.EXCELLENT.value,
                dept_id=5
            ),
            make_asset(
                asset_id=3, category=AssetCategory.LAPTOP.value, condition=AssetCondition.GOOD.value
            ),
        ]

        # Mock demand query
        demand_result = MagicMock()
        demand_result.scalar_one_or_none.return_value = make_demand(dept_id=5)

        # Mock assets query
        assets_result = MagicMock()
        assets_result.scalars.return_value.all.return_value = assets_data

        db.execute = AsyncMock(side_effect=[demand_result, assets_result])

        result = await AssetService.recommend_assets_for_demand(
            db=db, org_id=1, demand_id=10, category="LAPTOP", limit=10
        )

        # Top recommendation should be the excellent laptop in the same dept
        assert result.recommendations[0].asset_id == 2
        # Scores should be descending
        scores = [r.score for r in result.recommendations]
        assert scores == sorted(scores, reverse=True)
