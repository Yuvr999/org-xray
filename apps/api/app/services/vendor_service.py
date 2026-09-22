from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.demand import Vendor
from app.schemas.vendor import VendorCreate


class VendorService:
    @staticmethod
    async def get_vendor_by_id(db: AsyncSession, vendor_id: int, organization_id: int) -> Optional[Vendor]:
        stmt = select(Vendor).where(
            Vendor.id == vendor_id,
            Vendor.organization_id == organization_id
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_vendors(
        db: AsyncSession,
        organization_id: int,
        category: Optional[str] = None,
        region: Optional[str] = None,
        status: str = "ACTIVE",
    ) -> List[Vendor]:
        stmt = select(Vendor).where(
            Vendor.organization_id == organization_id,
            Vendor.status == status
        )
        if category:
            stmt = stmt.where(Vendor.category.ilike(f"%{category}%"))
        if region:
            stmt = stmt.where(Vendor.region.ilike(f"%{region}%"))
            
        stmt = stmt.order_by(Vendor.rating.desc(), Vendor.name.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_vendor(db: AsyncSession, organization_id: int, vendor_in: VendorCreate) -> Vendor:
        vendor = Vendor(
            organization_id=organization_id,
            name=vendor_in.name,
            category=vendor_in.category,
            region=vendor_in.region,
            contact_email=vendor_in.contact_email,
            rating=vendor_in.rating,
            status=vendor_in.status,
            gstin=vendor_in.gstin,
            metadata_json=vendor_in.metadata_json,
        )
        db.add(vendor)
        await db.commit()
        await db.refresh(vendor)
        return vendor
