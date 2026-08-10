# ViewerRank

ViewerRank is a production-oriented human curator ranking system for measuring which viewers consistently identify high-quality videos, consume them meaningfully, discover them early, and do so with statistically credible behavior.

## Core idea

ViewerRank separates popularity from quality and treats meaningful video selection as an implicit prediction. It records immutable exposure-time snapshots, waits for future quality to mature, and then scores whether a viewer repeatedly selected content that later proved unusually valuable relative to what their feed already exposed them to.

The primary score is:

`ViewerRank = confidence * weighted(taste, discovery, depth, reliability, breadth, influence) - fraud_penalty`

## v0.2 research core

The research core adds the pieces required to benchmark ViewerRank as a causal, temporal discovery system rather than a static engagement score:

- inverse-propensity weighting and doubly robust outcome estimation
- doubly robust curator alpha against expected exposure quality
- time-decayed curator state and stable curator embedding primitives
- multi-horizon future-quality forecasts with uncertainty and quality velocity
- uncertainty-aware upper-confidence exploration scores
- calibration error, NDCG, Future Quality Lift, and Hidden Gem Recall metrics
- leakage-safe temporal train/validation/test splitting
- first-class ablation evaluation for proving incremental curator value

The intended research question is:

> Given only information available at selection time, how much causal information does a viewer's behavior add about future content quality beyond the platform's existing exposure model?

## Repository layout

```text
src/viewerrank/          scoring, causal, temporal, forecast and evaluation code
config/                  versioned scoring/research configuration
db/                      PostgreSQL schema
tests/                   unit and research-core tests
.github/workflows/       CI
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn viewerrank.api:app --host 0.0.0.0 --port 8080
```

Then:

```bash
curl http://localhost:8080/healthz
```

Run the complete verification suite with:

```bash
ruff check src tests
pytest
docker build -t viewerrank:local .
```

## Benchmark targets

ViewerRank should be evaluated on temporal holdouts with no future leakage. Primary targets are Future Quality NDCG@K, Hidden Gem Recall@K, Future Quality Lift@K, calibration error, curator-alpha stability, and ablations that remove causal correction, curator signal, temporal state, or uncertainty exploration one component at a time.

## Production invariants

- Inputs are clamped and validated before scoring.
- Quality-at-selection and popularity-at-selection must be stored separately from matured future quality.
- Discovery credit cannot be earned solely by watching obscure content; future quality must validate the choice.
- Causal estimators must use exposure-time propensities and cap extreme inverse-propensity weights.
- Temporal evaluation must split by event time; random future-leaking splits are not acceptable for headline metrics.
- Ranking weights are versioned configuration, not hidden constants.
- Public rank should be opt-in; raw watch history should remain private.
- Recursive curator influence must be capped to prevent runaway feedback loops.

## Intellectual property

ViewerRank is claimed as intellectual property of **Mathew Blake Ward**. Copyright © 2026 Mathew Blake Ward. All rights reserved. See [NOTICE.md](NOTICE.md) for the repository notice.

## License

No open-source license has been granted. Public availability of the repository does not by itself grant permission to copy, modify, redistribute, sublicense, commercialize, or create derivative works except where applicable law provides otherwise.
