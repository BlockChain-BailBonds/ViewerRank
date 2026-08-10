from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable


@dataclass(frozen=True)
class TimedExample:
    occurred_at: datetime
    value: float


@dataclass(frozen=True)
class TemporalSplit:
    train: tuple[TimedExample, ...]
    validation: tuple[TimedExample, ...]
    test: tuple[TimedExample, ...]


def temporal_split(
    examples: Iterable[TimedExample],
    train_end: datetime,
    validation_end: datetime,
) -> TemporalSplit:
    if validation_end <= train_end:
        raise ValueError("validation_end must be after train_end")
    ordered = sorted(examples, key=lambda item: item.occurred_at)
    train = tuple(item for item in ordered if item.occurred_at <= train_end)
    validation = tuple(item for item in ordered if train_end < item.occurred_at <= validation_end)
    test = tuple(item for item in ordered if item.occurred_at > validation_end)
    return TemporalSplit(train=train, validation=validation, test=test)


@dataclass(frozen=True)
class AblationResult:
    baseline: float
    ablated: float

    @property
    def delta(self) -> float:
        return self.baseline - self.ablated

    @property
    def relative_lift(self) -> float:
        if self.ablated == 0:
            return 0.0
        return self.baseline / self.ablated - 1.0


def evaluate_ablation(
    full_model: Callable[[], float],
    ablated_model: Callable[[], float],
) -> AblationResult:
    return AblationResult(baseline=float(full_model()), ablated=float(ablated_model()))
