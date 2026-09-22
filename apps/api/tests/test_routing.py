import pytest
from app.services.routing_service import DemandRoutingPipeline, routing_pipeline
from app.models.demand import RoutingMethod


def test_rule_classifier_technical():
    dept, conf = routing_pipeline.classify_rule("Request for GPU servers and high-speed network router")
    assert dept == "Technical"
    assert conf > 0.60


def test_rule_classifier_finance():
    dept, conf = routing_pipeline.classify_rule("Audit and tax advisory consultation services")
    assert dept == "Finance"
    assert conf > 0.60


def test_rule_classifier_pr():
    dept, conf = routing_pipeline.classify_rule("Press release distribution and marketing campaign banner")
    assert dept == "PR"
    assert conf > 0.60


def test_ml_classifier_high_confidence():
    res = routing_pipeline.route_demand(
        title="Purchase Macbook Pro laptops for developers",
        description="Engineering department requires 5 M3 Macbook Pros for software development"
    )
    assert res["routed_department"] == "Technical"
    assert res["confidence"] >= 0.50
    assert res["method"] in [RoutingMethod.ML, RoutingMethod.RULE]


def test_route_demand_fallback():
    # Test ambiguous input triggers fallback or human review
    res = routing_pipeline.route_demand(
        title="Miscellaneous request item",
        description="Unrelated random text for office supplies"
    )
    assert "routed_department" in res
    assert "confidence" in res
    assert "method" in res
