import pytest
from app.services.tax_validation import validate_gst_arithmetic, validate_line_item_totals


def test_gst_arithmetic_valid_18_percent():
    # Subtotal 1000, 18% GST is 180, grand total 1180
    results = validate_gst_arithmetic(
        subtotal=1000.0,
        total_tax=180.0,
        grand_total=1180.0,
        tax_rate=18.0,
    )
    
    # Check that all validation checks passed
    for res in results:
        assert res.passed is True, f"Rule {res.rule_name} failed: {res.message}"


def test_gst_arithmetic_invalid_tax():
    # Subtotal 1000, expected 180 tax, but got 200
    results = validate_gst_arithmetic(
        subtotal=1000.0,
        total_tax=200.0,
        grand_total=1200.0,
        tax_rate=18.0,
    )
    
    tax_calc_res = next((r for r in results if r.rule_name == "gst_tax_calculation"), None)
    assert tax_calc_res is not None
    assert tax_calc_res.passed is False
    assert tax_calc_res.severity == "error"
    assert "₹200.00 does not match expected ₹180.00" in tax_calc_res.message


def test_gst_arithmetic_invalid_grand_total():
    # Subtotal 1000, tax 180, but grand total 1500 (wrong sum)
    results = validate_gst_arithmetic(
        subtotal=1000.0,
        total_tax=180.0,
        grand_total=1500.0,
        tax_rate=18.0,
    )
    
    total_res = next((r for r in results if r.rule_name == "gst_total_validation"), None)
    assert total_res is not None
    assert total_res.passed is False
    assert total_res.severity == "error"


def test_gst_arithmetic_missing_amounts():
    results = validate_gst_arithmetic(
        subtotal=None,
        total_tax=180.0,
        grand_total=None,
    )
    assert len(results) == 1
    assert results[0].passed is False
    assert results[0].rule_name == "gst_amounts_present"


def test_line_item_totals_validation():
    items = [
        {"description": "Item A", "taxable_amount": 500.0},
        {"description": "Item B", "taxable_amount": 500.0},
    ]
    results = validate_line_item_totals(items=items, subtotal=1000.0)
    assert len(results) == 1
    assert results[0].passed is True

    # Mismatching subtotal
    bad_results = validate_line_item_totals(items=items, subtotal=1200.0)
    assert len(bad_results) == 1
    assert bad_results[0].passed is False
