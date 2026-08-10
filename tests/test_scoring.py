import math

import pytest

from viewerrank.scoring import (
    ViewerComponents,
    bayesian_shrink,
    calculate_viewer_rank,
    confidence_from_samples,
    discovery_credit,
    early_factor,
    selection_alpha,
    time_decay,
)


def test_rank_is_deterministic() -> None:
    components = ViewerComponents(
        taste=0.9,
        discovery=0.8,
        depth=0.7,
        reliability=0.95,
        breadth=0.6,
        influence=0.5,
        confidence=0.9,
        fraud_penalty=0.02,
    )
    assert calculate_viewer_rank(components) == calculate_viewer_rank(components)


def test_rank_respects_confidence_and_penalty() -> None:
    high = ViewerComponents(1, 1, 1, 1, 1, 1, 1, 0)
    low = ViewerComponents(1, 1, 1, 1, 1, 1, 0.5, 0.1)
    assert calculate_viewer_rank(high) == 100.0
    assert calculate_viewer_rank(low) == 40.0


def test_bayesian_shrink_uses_prior() -> None:
    assert bayesian_shrink(1.0, 0, 0.5, 100) == 0.5
    assert bayesian_shrink(1.0, 100, 0.5, 100) == 0.75


def test_confidence_from_samples() -> None:
    assert confidence_from_samples(0, 50) == 0.0
    assert confidence_from_samples(50, 50) == 0.5


def test_early_factor_rewards_earlier_selection() -> None:
    assert early_factor(0.01) > early_factor(0.50) > early_factor(0.99)


def test_discovery_credit_requires_quality() -> None:
    assert discovery_credit(0.0, 0.001, 1.0) == 0.0
    assert discovery_credit(1.0, 0.001, 1.0) > 0.99


def test_selection_alpha_is_counterfactual_delta() -> None:
    assert selection_alpha(0.9, 0.6) == pytest.approx(0.3)
    assert selection_alpha(0.2, 0.7) == pytest.approx(-0.5)


def test_time_decay_half_life() -> None:
    assert time_decay(180, 180) == pytest.approx(0.5)
    assert math.isclose(time_decay(0, 180), 1.0)


def test_invalid_half_life_fails() -> None:
    with pytest.raises(ValueError):
        time_decay(10, 0)
