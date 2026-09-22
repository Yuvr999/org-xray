"""
GSTIN Verification Service

Implements:
1. Regex format validation (15 chars)
2. MOD-36 checksum algorithm (India GSTIN specification)
3. Provider Adapter interface (Mock & REST)
4. Database persistence of verification provenance
"""

import abc
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.models.identity import User
from app.models.gstin import GSTINStatus, GSTINVerificationRecord
from app.services.audit_service import log_audit_event

# 15-character official GSTIN regex pattern
GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

# MOD-36 alphabet
MOD36_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def validate_gstin_format(gstin: str) -> bool:
    """Validate standard 15-character GSTIN regex format."""
    if not gstin or not isinstance(gstin, str):
        return False
    clean_gstin = gstin.strip().upper()
    return bool(GSTIN_REGEX.match(clean_gstin))


def calculate_mod36_checksum(gstin: str) -> Tuple[bool, Optional[str]]:
    """
    Calculate GSTIN MOD-36 checksum according to Indian GST specification.
    Returns (is_valid, expected_check_digit).
    """
    if not gstin or len(gstin.strip()) != 15:
        return False, None

    clean_gstin = gstin.strip().upper()
    
    # Pre-check basic characters exist in MOD36_ALPHABET
    for char in clean_gstin:
        if char not in MOD36_ALPHABET:
            return False, None

    weights = [1, 2] * 7  # Alternating multipliers 1, 2 for first 14 chars
    total_sum = 0

    for i in range(14):
        char_val = MOD36_ALPHABET.index(clean_gstin[i])
        product = char_val * weights[i]
        # Sum quotient and remainder when divided by 36
        quotient, remainder = divmod(product, 36)
        total_sum += quotient + remainder

    remainder = total_sum % 36
    check_digit_index = (36 - remainder) % 36
    expected_check_digit = MOD36_ALPHABET[check_digit_index]

    actual_check_digit = clean_gstin[14]
    is_valid = actual_check_digit == expected_check_digit

    return is_valid, expected_check_digit


# --- Provider Adapter Pattern ---

class GSTINProviderResult:
    def __init__(
        self,
        success: bool,
        status: str,
        legal_name: Optional[str] = None,
        trade_name: Optional[str] = None,
        state_code: Optional[str] = None,
        taxpayer_type: Optional[str] = None,
        raw_response: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ):
        self.success = success
        self.status = status
        self.legal_name = legal_name
        self.trade_name = trade_name
        self.state_code = state_code
        self.taxpayer_type = taxpayer_type
        self.raw_response = raw_response or {}
        self.error_message = error_message


class GSTINAdapter(abc.ABC):
    @abc.abstractmethod
    async def verify_live(self, gstin: str) -> GSTINProviderResult:
        """Perform live verification against GSTIN REST provider."""
        pass


class MockGSTINAdapter(GSTINAdapter):
    """Development / Offline Mock GSTIN provider."""

    async def verify_live(self, gstin: str) -> GSTINProviderResult:
        clean = gstin.strip().upper()

        # Simulated mock responses
        if clean.startswith("99"):
            return GSTINProviderResult(
                success=False,
                status="INACTIVE",
                error_message="GSTIN registration cancelled or inactive",
                raw_response={"message": "Taxpayer cancelled"},
            )

        state_code = clean[:2]
        return GSTINProviderResult(
            success=True,
            status="ACTIVE",
            legal_name=f"ENTERPRISE VENDOR {clean[2:7]} LTD",
            trade_name=f"VENDOR {clean[2:7]} TRADERS",
            state_code=state_code,
            taxpayer_type="Regular",
            raw_response={
                "gstin": clean,
                "sts": "Active",
                "lgnm": f"ENTERPRISE VENDOR {clean[2:7]} LTD",
                "stj": f"State Jurisdiction {state_code}",
            },
        )


class RESTGSTINAdapter(GSTINAdapter):
    """External Live REST GSTIN API provider client."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    async def verify_live(self, gstin: str) -> GSTINProviderResult:
        if not self.api_url:
            return GSTINProviderResult(
                success=False,
                status="UNAVAILABLE",
                error_message="GSTIN Provider REST API URL not configured",
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(f"{self.api_url}/verify/{gstin}", headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return GSTINProviderResult(
                        success=True,
                        status=data.get("status", "ACTIVE"),
                        legal_name=data.get("legal_name"),
                        trade_name=data.get("trade_name"),
                        state_code=data.get("state_code", gstin[:2]),
                        taxpayer_type=data.get("taxpayer_type"),
                        raw_response=data,
                    )
                else:
                    return GSTINProviderResult(
                        success=False,
                        status="PROVIDER_NEGATIVE",
                        error_message=f"HTTP {res.status_code}: {res.text}",
                        raw_response={"status_code": res.status_code, "body": res.text},
                    )
        except Exception as e:
            logger.error(f"GSTIN REST API call failed for {gstin}: {str(e)}")
            return GSTINProviderResult(
                success=False,
                status="PROVIDER_UNAVAILABLE",
                error_message=str(e),
            )


def get_gstin_adapter() -> GSTINAdapter:
    """Factory to return configured GSTIN provider adapter."""
    provider_type = getattr(settings, "GSTIN_PROVIDER_TYPE", "mock").lower()
    if provider_type == "rest":
        return RESTGSTINAdapter(
            api_url=getattr(settings, "GSTIN_API_URL", ""),
            api_key=getattr(settings, "GSTIN_API_KEY", ""),
        )
    return MockGSTINAdapter()


# --- Main Service Verification Flow ---

async def verify_gstin(
    db: AsyncSession,
    gstin: str,
    user: User,
    skip_live_check: bool = False,
) -> GSTINVerificationRecord:
    """
    Perform full GSTIN verification flow:
    1. Normalize string
    2. Format regex check
    3. MOD-36 checksum calculation
    4. Optional live provider check
    5. Save verification record & log audit event
    """
    clean_gstin = gstin.strip().upper() if gstin else ""

    # 1. Format check
    format_valid = validate_gstin_format(clean_gstin)
    if not format_valid:
        record = GSTINVerificationRecord(
            organization_id=user.organization_id,
            requested_by_id=user.id,
            gstin=clean_gstin,
            is_format_valid=False,
            is_checksum_valid=False,
            is_live_verified=False,
            status=GSTINStatus.INVALID_FORMAT.value,
            evidence={
                "error": "Invalid format. Expected 15-character GSTIN pattern e.g. 27AAPCU6142R1ZA."
            },
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    # 2. Checksum check
    checksum_valid, expected_digit = calculate_mod36_checksum(clean_gstin)
    if not checksum_valid:
        record = GSTINVerificationRecord(
            organization_id=user.organization_id,
            requested_by_id=user.id,
            gstin=clean_gstin,
            is_format_valid=True,
            is_checksum_valid=False,
            is_live_verified=False,
            status=GSTINStatus.INVALID_CHECKSUM.value,
            evidence={
                "error": f"MOD-36 checksum mismatch. Received '{clean_gstin[-1]}', expected '{expected_digit}'."
            },
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    # 3. Live verification (if requested and format/checksum pass)
    live_verified = False
    status_str = GSTINStatus.VALID.value
    legal_name = None
    trade_name = None
    state_code = clean_gstin[:2]
    taxpayer_type = None
    provider_name = "local_mod36"
    raw_response = None
    evidence = {
        "format_check": "PASSED",
        "checksum_check": "PASSED",
        "expected_check_digit": expected_digit,
    }

    if not skip_live_check:
        adapter = get_gstin_adapter()
        provider_name = adapter.__class__.__name__
        prov_res = await adapter.verify_live(clean_gstin)

        raw_response = prov_res.raw_response
        evidence["provider_status"] = prov_res.status

        if prov_res.success:
            live_verified = True
            status_str = GSTINStatus.PROVIDER_VERIFIED.value
            legal_name = prov_res.legal_name
            trade_name = prov_res.trade_name
            state_code = prov_res.state_code or state_code
            taxpayer_type = prov_res.taxpayer_type
        else:
            if prov_res.status == "UNAVAILABLE":
                status_str = GSTINStatus.PROVIDER_UNAVAILABLE.value
            else:
                status_str = GSTINStatus.PROVIDER_NEGATIVE.value
            evidence["provider_error"] = prov_res.error_message

    record = GSTINVerificationRecord(
        organization_id=user.organization_id,
        requested_by_id=user.id,
        gstin=clean_gstin,
        is_format_valid=True,
        is_checksum_valid=True,
        is_live_verified=live_verified,
        status=status_str,
        legal_name=legal_name,
        trade_name=trade_name,
        state_code=state_code,
        taxpayer_type=taxpayer_type,
        provider_name=provider_name,
        raw_response=raw_response,
        evidence=evidence,
    )
    db.add(record)

    await log_audit_event(
        db=db,
        action="gstin.verify",
        resource_type="gstin",
        resource_id=clean_gstin,
        new_values={
            "status": status_str,
            "format_valid": True,
            "checksum_valid": True,
            "live_verified": live_verified,
        },
        user=user,
        organization_id=user.organization_id,
    )

    await db.commit()
    await db.refresh(record)

    return record


async def get_gstin_verification_history(
    db: AsyncSession,
    organization_id: int,
    gstin: str,
) -> Optional[GSTINVerificationRecord]:
    """Retrieve most recent verification record for a GSTIN in organization."""
    clean_gstin = gstin.strip().upper()
    stmt = (
        select(GSTINVerificationRecord)
        .where(
            GSTINVerificationRecord.organization_id == organization_id,
            GSTINVerificationRecord.gstin == clean_gstin,
        )
        .order_by(GSTINVerificationRecord.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
