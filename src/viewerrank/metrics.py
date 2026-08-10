from __future__ import annotations

from dataclasses import dataclass
from math import log2


@dataclass(frozen=True)
class Prediction:
    probability: float
    outcome: float


def expected_calibration_error(predictions: list[Prediction], bins: int = 10) -> float:
    if bins <= 0:
        raise ValueError("bins must be positive")
    if not predictions:
        return 0.0
    buckets: list[list[Prediction]] = [[] for _ in range(bins)]
    for item in predictions:
        probability = min(1.0, max(0.0, item.probability))
        index = min(bins - 1, int(probability * bins))
        buckets[index].append(Prediction(probability=probability, outcome=item.outcome))
    total = len(predictions)
    error = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        confidence = sum(item.probability for item in bucket) / len(bucket)
        accuracy = sum(float(item.outcome) for item in bucket) / len(bucket)
        error += (len(bucket) / total) * abs(confidence - accuracy)
    return error


def ndcg_at_k(relevances: list[float], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    observed = relevances[:k]
    ideal = sorted(relevances, reverse=True)[:k]

    def dcg(values: list[float]) -> float:
        return sum((2**value - 1.0) / log2(index + 2) for index, value in enumerate(values))

    ideal_score = dcg(ideal)
    return dcg(observed) / ideal_score if ideal_score else 0.0


def hidden_gem_recall_at_k(
    predicted_video_ids: list[str],
    future_top_quality_video_ids: set[str],
    obscure_at_prediction_video_ids: set[str],
    k: int,
) -> float:
    eligible = future_top_quality_video_ids & obscure_at_prediction_video_ids
    if not eligible:
        return 0.0
    hits = set(predicted_video_ids[:k]) & eligible
    return len(hits) / len(eligible)


def future_quality_lift(model_quality: float, baseline_quality: float) -> float:
    if baseline_quality <= 0:
        raise ValueError("baseline_quality must be positive")
    return model_quality / baseline_quality - 1.0
