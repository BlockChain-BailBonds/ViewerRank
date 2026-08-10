from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import exp, log

DEFAULT_WEIGHTS: dict[str, float] = {
    "taste": 0.35,
    "discovery": 0.25,
    "depth": 0.15,
    "reliability": 0.10,
    "breadth": 0.05,
    "influence": 0.10,
}


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def validate_weights(weights: Mapping[str, float]) -> None:
    required = set(DEFAULT_WEIGHTS)
    if set(weights) != required:
        missing = required - set(weights)
        extra = set(weights) - required
        raise ValueError(f"invalid weight keys; missing={sorted(missing)} extra={sorted(extra)}")
    if any(value < 0 for value in weights.values()):
        raise ValueError("weights must be non-negative")
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"weights must sum to 1.0; got {total}")


def bayesian_shrink(observed: float, sample_count: int, prior_mean: float, prior_strength: float) -> float:
    if sample_count < 0:
        raise ValueError("sample_count must be non-negative")
    if prior_strength < 0:
        raise ValueError("prior_strength must be non-negative")
    if sample_count == 0 and prior_strength == 0:
        return clamp01(prior_mean)
    numerator = sample_count * clamp01(observed) + prior_strength * clamp01(prior_mean)
    denominator = sample_count + prior_strength
    return clamp01(numerator / denominator)


def confidence_from_samples(sample_count: int, prior_strength: float) -> float:
    if sample_count < 0:
        raise ValueError("sample_count must be non-negative")
    if prior_strength < 0:
        raise ValueError("prior_strength must be non-negative")
    if sample_count == 0:
        return 0.0
    if prior_strength == 0:
        return 1.0
    return clamp01(sample_count / (sample_count + prior_strength))


def time_decay(age_days: float, half_life_days: float) -> float:
    if age_days < 0:
        raise ValueError("age_days must be non-negative")
    if half_life_days <= 0:
        raise ValueError("half_life_days must be positive")
    return exp(-(log(2.0) / half_life_days) * age_days)


def early_factor(popularity_percentile_at_selection: float, exponent: float = 1.5) -> float:
    if exponent <= 0:
        raise ValueError("exponent must be positive")
    popularity = clamp01(popularity_percentile_at_selection)
    return clamp01((1.0 - popularity) ** exponent)


def discovery_credit(
    matured_quality: float,
    popularity_percentile_at_selection: float,
    watch_depth: float,
    quality_confidence: float = 1.0,
    exponent: float = 1.5,
) -> float:
    return clamp01(
        clamp01(matured_quality)
        * early_factor(popularity_percentile_at_selection, exponent)
        * clamp01(watch_depth)
        * clamp01(quality_confidence)
    )


def selection_alpha(matured_quality: float, expected_quality_at_exposure: float) -> float:
    return max(-1.0, min(1.0, clamp01(matured_quality) - clamp01(expected_quality_at_exposure)))


@dataclass(frozen=True)
class ViewerComponents:
    taste: float
    discovery: float
    depth: float
    reliability: float
    breadth: float
    influence: float
    confidence: float
    fraud_penalty: float = 0.0

    def normalized(self) -> ViewerComponents:
        return ViewerComponents(
            taste=clamp01(self.taste),
            discovery=clamp01(self.discovery),
            depth=clamp01(self.depth),
            reliability=clamp01(self.reliability),
            breadth=clamp01(self.breadth),
            influence=clamp01(self.influence),
            confidence=clamp01(self.confidence),
            fraud_penalty=max(0.0, float(self.fraud_penalty)),
        )


def calculate_viewer_rank(
    components: ViewerComponents,
    weights: Mapping[str, float] | None = None,
) -> float:
    effective_weights = dict(DEFAULT_WEIGHTS if weights is None else weights)
    validate_weights(effective_weights)
    c = components.normalized()
    weighted = (
        effective_weights["taste"] * c.taste
        + effective_weights["discovery"] * c.discovery
        + effective_weights["depth"] * c.depth
        + effective_weights["reliability"] * c.reliability
        + effective_weights["breadth"] * c.breadth
        + effective_weights["influence"] * c.influence
    )
    trusted = weighted * c.confidence
    penalized = trusted - c.fraud_penalty
    return round(100.0 * clamp01(penalized), 6)
