from __future__ import annotations

from dataclasses import dataclass
from math import exp, log


@dataclass(frozen=True)
class TemporalSignal:
    value: float
    age_days: float
    confidence: float = 1.0


def decay_weight(age_days: float, half_life_days: float) -> float:
    if age_days < 0:
        raise ValueError("age_days must be non-negative")
    if half_life_days <= 0:
        raise ValueError("half_life_days must be positive")
    return exp(-(log(2.0) / half_life_days) * age_days)


def temporal_mean(signals: list[TemporalSignal], half_life_days: float = 90.0) -> float:
    if not signals:
        return 0.0
    numerator = 0.0
    denominator = 0.0
    for signal in signals:
        confidence = min(1.0, max(0.0, signal.confidence))
        weight = decay_weight(signal.age_days, half_life_days) * confidence
        numerator += signal.value * weight
        denominator += weight
    return numerator / denominator if denominator else 0.0


def blend_short_long_term(
    short_term: float,
    long_term: float,
    short_term_confidence: float,
    max_short_weight: float = 0.7,
) -> float:
    if not 0.0 <= max_short_weight <= 1.0:
        raise ValueError("max_short_weight must be within [0, 1]")
    short_weight = max_short_weight * min(1.0, max(0.0, short_term_confidence))
    return short_weight * short_term + (1.0 - short_weight) * long_term


@dataclass(frozen=True)
class CuratorEmbedding:
    topic_skill: float
    discovery_skill: float
    quality_discrimination: float
    novelty_affinity: float
    long_form_affinity: float
    trust: float

    def as_vector(self) -> tuple[float, ...]:
        return (
            self.topic_skill,
            self.discovery_skill,
            self.quality_discrimination,
            self.novelty_affinity,
            self.long_form_affinity,
            self.trust,
        )
