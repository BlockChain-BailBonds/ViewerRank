from __future__ import annotations

from dataclasses import dataclass


DEFAULT_HORIZONS_HOURS = (1, 24, 168, 720, 2160)


@dataclass(frozen=True)
class HorizonForecast:
    horizon_hours: int
    expected_quality: float
    uncertainty: float

    def validated(self) -> "HorizonForecast":
        if self.horizon_hours <= 0:
            raise ValueError("horizon_hours must be positive")
        return HorizonForecast(
            horizon_hours=self.horizon_hours,
            expected_quality=min(1.0, max(0.0, self.expected_quality)),
            uncertainty=max(0.0, self.uncertainty),
        )


def quality_velocity(forecasts: list[HorizonForecast]) -> float:
    if len(forecasts) < 2:
        return 0.0
    ordered = sorted((item.validated() for item in forecasts), key=lambda item: item.horizon_hours)
    first = ordered[0]
    last = ordered[-1]
    delta_days = (last.horizon_hours - first.horizon_hours) / 24.0
    if delta_days <= 0:
        return 0.0
    return (last.expected_quality - first.expected_quality) / delta_days


def upper_confidence_bound(forecast: HorizonForecast, beta: float = 0.25) -> float:
    if beta < 0:
        raise ValueError("beta must be non-negative")
    item = forecast.validated()
    return min(1.0, item.expected_quality + beta * item.uncertainty)


def curator_information_lift(with_curator: float, without_curator: float) -> float:
    return max(-1.0, min(1.0, float(with_curator) - float(without_curator)))
