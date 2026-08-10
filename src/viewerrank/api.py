from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .scoring import ViewerComponents, calculate_viewer_rank, discovery_credit, selection_alpha

app = FastAPI(title="ViewerRank API", version="0.1.0")


class ComponentsIn(BaseModel):
    taste: float = Field(ge=0.0, le=1.0)
    discovery: float = Field(ge=0.0, le=1.0)
    depth: float = Field(ge=0.0, le=1.0)
    reliability: float = Field(ge=0.0, le=1.0)
    breadth: float = Field(ge=0.0, le=1.0)
    influence: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    fraud_penalty: float = Field(default=0.0, ge=0.0)


class RankOut(BaseModel):
    score: float


class DiscoveryIn(BaseModel):
    matured_quality: float = Field(ge=0.0, le=1.0)
    popularity_percentile_at_selection: float = Field(ge=0.0, le=1.0)
    watch_depth: float = Field(ge=0.0, le=1.0)
    quality_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    expected_quality_at_exposure: float = Field(ge=0.0, le=1.0)


class DiscoveryOut(BaseModel):
    discovery_credit: float
    selection_alpha: float


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/rank/calculate", response_model=RankOut)
def rank_calculate(payload: ComponentsIn) -> RankOut:
    components = ViewerComponents(**payload.model_dump())
    return RankOut(score=calculate_viewer_rank(components))


@app.post("/v1/discovery/calculate", response_model=DiscoveryOut)
def discovery_calculate(payload: DiscoveryIn) -> DiscoveryOut:
    return DiscoveryOut(
        discovery_credit=discovery_credit(
            matured_quality=payload.matured_quality,
            popularity_percentile_at_selection=payload.popularity_percentile_at_selection,
            watch_depth=payload.watch_depth,
            quality_confidence=payload.quality_confidence,
        ),
        selection_alpha=selection_alpha(
            payload.matured_quality,
            payload.expected_quality_at_exposure,
        ),
    )
