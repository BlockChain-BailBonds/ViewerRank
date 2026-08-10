from datetime import datetime, timezone

import pytest

from viewerrank.causal import (
    DoublyRobustObservation,
    curator_alpha_dr,
    doubly_robust_value,
    inverse_propensity_weight,
)
from viewerrank.evaluation import TimedExample, evaluate_ablation, temporal_split
from viewerrank.forecast import HorizonForecast, quality_velocity, upper_confidence_bound
from viewerrank.metrics import (
    Prediction,
    expected_calibration_error,
    future_quality_lift,
    hidden_gem_recall_at_k,
    ndcg_at_k,
)
from viewerrank.temporal import CuratorEmbedding, TemporalSignal, temporal_mean


def test_inverse_propensity_weight_is_capped() -> None:
    assert inverse_propensity_weight(0.001, max_weight=10.0) == 10.0


def test_doubly_robust_value_matches_formula() -> None:
    item = DoublyRobustObservation(outcome=0.9, propensity=0.5, expected_outcome=0.6)
    assert doubly_robust_value(item) == pytest.approx(1.2)


def test_curator_alpha_dr_positive_when_selection_beats_baseline() -> None:
    alpha = curator_alpha_dr([0.9, 0.8], [0.5, 0.5], [0.5, 0.5])
    assert alpha > 0


def test_temporal_mean_prefers_recent_signal() -> None:
    value = temporal_mean(
        [TemporalSignal(1.0, 1.0), TemporalSignal(0.0, 180.0)], half_life_days=30.0
    )
    assert value > 0.9


def test_curator_embedding_vector_is_stable() -> None:
    embedding = CuratorEmbedding(1, 2, 3, 4, 5, 6)
    assert embedding.as_vector() == (1, 2, 3, 4, 5, 6)


def test_quality_velocity_and_ucb() -> None:
    forecasts = [HorizonForecast(24, 0.4, 0.2), HorizonForecast(72, 0.8, 0.1)]
    assert quality_velocity(forecasts) == pytest.approx(0.2)
    assert upper_confidence_bound(forecasts[0], beta=0.5) == pytest.approx(0.5)


def test_calibration_error_zero_for_perfect_predictions() -> None:
    predictions = [Prediction(1.0, 1.0), Prediction(0.0, 0.0)]
    assert expected_calibration_error(predictions) == pytest.approx(0.0)


def test_hidden_gem_recall_and_quality_lift() -> None:
    recall = hidden_gem_recall_at_k(
        ["a", "b", "c"], {"a", "x"}, {"a", "x", "z"}, 2
    )
    assert recall == pytest.approx(0.5)
    assert future_quality_lift(0.75, 0.60) == pytest.approx(0.25)


def test_ndcg_at_k_is_bounded() -> None:
    score = ndcg_at_k([3.0, 2.0, 1.0], 3)
    assert score == pytest.approx(1.0)


def test_temporal_split_is_leakage_safe() -> None:
    examples = [
        TimedExample(datetime(2026, 1, 1, tzinfo=timezone.utc), 1.0),
        TimedExample(datetime(2026, 2, 1, tzinfo=timezone.utc), 2.0),
        TimedExample(datetime(2026, 3, 1, tzinfo=timezone.utc), 3.0),
    ]
    split = temporal_split(
        examples,
        datetime(2026, 1, 15, tzinfo=timezone.utc),
        datetime(2026, 2, 15, tzinfo=timezone.utc),
    )
    assert len(split.train) == len(split.validation) == len(split.test) == 1


def test_ablation_delta() -> None:
    result = evaluate_ablation(lambda: 0.8, lambda: 0.6)
    assert result.delta == pytest.approx(0.2)
    assert result.relative_lift == pytest.approx(1 / 3)
