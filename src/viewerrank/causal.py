from __future__ import annotations

from dataclasses import dataclass


EPS = 1e-6


def _clip_probability(value: float) -> float:
    return min(1.0 - EPS, max(EPS, float(value)))


def inverse_propensity_weight(propensity: float, max_weight: float = 20.0) -> float:
    if max_weight <= 0:
        raise ValueError("max_weight must be positive")
    return min(max_weight, 1.0 / _clip_probability(propensity))


def ips_mean(outcomes: list[float], propensities: list[float], max_weight: float = 20.0) -> float:
    if len(outcomes) != len(propensities) or not outcomes:
        raise ValueError("outcomes and propensities must be non-empty and equal length")
    weighted_sum = 0.0
    weight_sum = 0.0
    for outcome, propensity in zip(outcomes, propensities, strict=True):
        weight = inverse_propensity_weight(propensity, max_weight)
        weighted_sum += float(outcome) * weight
        weight_sum += weight
    return weighted_sum / weight_sum


@dataclass(frozen=True)
class DoublyRobustObservation:
    outcome: float
    propensity: float
    expected_outcome: float


def doubly_robust_value(observation: DoublyRobustObservation, max_weight: float = 20.0) -> float:
    weight = inverse_propensity_weight(observation.propensity, max_weight)
    return float(observation.expected_outcome) + weight * (
        float(observation.outcome) - float(observation.expected_outcome)
    )


def doubly_robust_mean(
    observations: list[DoublyRobustObservation], max_weight: float = 20.0
) -> float:
    if not observations:
        raise ValueError("observations must be non-empty")
    return sum(doubly_robust_value(item, max_weight) for item in observations) / len(observations)


def curator_alpha_dr(
    selected_quality: list[float],
    propensities: list[float],
    expected_quality: list[float],
    max_weight: float = 20.0,
) -> float:
    if not (len(selected_quality) == len(propensities) == len(expected_quality)):
        raise ValueError("all inputs must have equal length")
    observations = [
        DoublyRobustObservation(outcome=q, propensity=p, expected_outcome=e)
        for q, p, e in zip(selected_quality, propensities, expected_quality, strict=True)
    ]
    corrected_quality = doubly_robust_mean(observations, max_weight)
    baseline_quality = sum(expected_quality) / len(expected_quality)
    return corrected_quality - baseline_quality
