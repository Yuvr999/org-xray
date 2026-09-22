"""
Invoice Tax Validation Service

Implements the documented 18% GST arithmetic validation rule.
Tax rate is configurable per-organization but defaults to 18%.
"""

from dataclasses import dataclass
from typing import List, Optional

# Rounding tolerance for floating point comparisons
DEFAULT_TOLERANCE = 0.50  # ₹0.50 tolerance for rounding


@dataclass
class ValidationResult:
    rule_name: str
    severity: str  # "error", "warning", "info"
    passed: bool
    message: str
    details: Optional[dict] = None


def validate_gst_arithmetic(
    subtotal: Optional[float],
    total_tax: Optional[float],
    grand_total: Optional[float],
    tax_rate: float = 18.0,
    tolerance: float = DEFAULT_TOLERANCE,
) -> List[ValidationResult]:
    """
    Validate GST arithmetic: total_tax should be (tax_rate/100) * subtotal,
    and grand_total should equal subtotal + total_tax.

    Preserves the documented 18% default while allowing configurable rates.
    """
    results: List[ValidationResult] = []

    # 1. Check if required amounts are present
    if subtotal is None or grand_total is None:
        results.append(ValidationResult(
            rule_name="gst_amounts_present",
            severity="warning",
            passed=False,
            message="Subtotal and/or grand total are missing — cannot validate tax arithmetic",
            details={"subtotal": subtotal, "grand_total": grand_total},
        ))
        return results

    results.append(ValidationResult(
        rule_name="gst_amounts_present",
        severity="info",
        passed=True,
        message="Required amount fields are present",
    ))

    # 2. Validate tax amount calculation
    expected_tax = round(subtotal * (tax_rate / 100.0), 2)

    if total_tax is not None:
        tax_diff = abs(total_tax - expected_tax)
        tax_ok = tax_diff <= tolerance

        results.append(ValidationResult(
            rule_name="gst_tax_calculation",
            severity="error" if not tax_ok else "info",
            passed=tax_ok,
            message=(
                f"Tax amount ₹{total_tax:.2f} matches expected ₹{expected_tax:.2f} "
                f"({tax_rate}% of ₹{subtotal:.2f})"
            ) if tax_ok else (
                f"Tax amount ₹{total_tax:.2f} does not match expected ₹{expected_tax:.2f} "
                f"({tax_rate}% of ₹{subtotal:.2f}). Difference: ₹{tax_diff:.2f}"
            ),
            details={
                "subtotal": subtotal,
                "tax_rate_percent": tax_rate,
                "expected_tax": expected_tax,
                "actual_tax": total_tax,
                "difference": round(tax_diff, 2),
                "tolerance": tolerance,
            },
        ))
    else:
        results.append(ValidationResult(
            rule_name="gst_tax_calculation",
            severity="warning",
            passed=False,
            message="Total tax amount is missing — cannot validate tax calculation",
            details={"expected_tax": expected_tax},
        ))

    # 3. Validate grand total = subtotal + tax
    tax_for_total = total_tax if total_tax is not None else expected_tax
    expected_total = round(subtotal + tax_for_total, 2)
    total_diff = abs(grand_total - expected_total)
    total_ok = total_diff <= tolerance

    results.append(ValidationResult(
        rule_name="gst_total_validation",
        severity="error" if not total_ok else "info",
        passed=total_ok,
        message=(
            f"Grand total ₹{grand_total:.2f} matches expected ₹{expected_total:.2f} "
            f"(₹{subtotal:.2f} + ₹{tax_for_total:.2f})"
        ) if total_ok else (
            f"Grand total ₹{grand_total:.2f} does not match expected ₹{expected_total:.2f} "
            f"(₹{subtotal:.2f} + ₹{tax_for_total:.2f}). Difference: ₹{total_diff:.2f}"
        ),
        details={
            "subtotal": subtotal,
            "tax_used": tax_for_total,
            "expected_total": expected_total,
            "actual_total": grand_total,
            "difference": round(total_diff, 2),
            "tolerance": tolerance,
        },
    ))

    return results


def validate_line_item_totals(
    items: list,
    subtotal: Optional[float],
    tolerance: float = DEFAULT_TOLERANCE,
) -> List[ValidationResult]:
    """
    Validate that line item amounts sum to the invoice subtotal.
    Each item dict is expected to have 'taxable_amount' or 'total_amount'.
    """
    results: List[ValidationResult] = []

    if not items:
        results.append(ValidationResult(
            rule_name="line_item_sum",
            severity="info",
            passed=True,
            message="No line items to validate",
        ))
        return results

    item_sum = 0.0
    for item in items:
        amt = item.get("taxable_amount") or item.get("total_amount") or 0.0
        item_sum += float(amt)

    item_sum = round(item_sum, 2)

    if subtotal is not None:
        diff = abs(item_sum - subtotal)
        ok = diff <= tolerance
        results.append(ValidationResult(
            rule_name="line_item_sum",
            severity="error" if not ok else "info",
            passed=ok,
            message=(
                f"Line item sum ₹{item_sum:.2f} matches subtotal ₹{subtotal:.2f}"
            ) if ok else (
                f"Line item sum ₹{item_sum:.2f} does not match subtotal ₹{subtotal:.2f}. "
                f"Difference: ₹{diff:.2f}"
            ),
            details={
                "line_item_sum": item_sum,
                "subtotal": subtotal,
                "difference": round(diff, 2),
                "item_count": len(items),
            },
        ))

    return results
