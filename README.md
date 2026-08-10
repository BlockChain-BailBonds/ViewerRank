# ViewerRank

ViewerRank is a production-oriented human curator ranking system for measuring which viewers consistently identify high-quality videos, consume them meaningfully, discover them early, and do so with statistically credible behavior.

## Live dashboard

GitHub Pages dashboard: **https://blockchain-bailbonds.github.io/ViewerRank/**

The dashboard redeploys automatically when the site changes on `main` and refreshes public repository, pull-request, commit, and GitHub Actions data in the browser every 10 minutes.

## Core idea

ViewerRank separates popularity from quality and treats meaningful video selection as an implicit prediction. It records immutable exposure-time snapshots, waits for future quality to mature, and then scores whether a viewer repeatedly selected content that later proved unusually valuable relative to what their feed already exposed them to.

The primary score is:

`ViewerRank = confidence * weighted(taste, discovery, depth, reliability, breadth, influence) - fraud_penalty`

The starter implementation includes deterministic scoring, Bayesian confidence shrinkage, early-discovery credit, time decay, a FastAPI service, PostgreSQL schema, configuration, tests, Docker packaging, and CI.

## Repository layout

```text
src/viewerrank/          scoring and API implementation
config/                  versioned scoring configuration
db/                      PostgreSQL schema
site/                    live GitHub Pages dashboard
tests/                   unit tests
.github/workflows/       CI and Pages deployment
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

## Production invariants

- Inputs are clamped and validated before scoring.
- Quality-at-selection and popularity-at-selection must be stored separately from matured future quality.
- Discovery credit cannot be earned solely by watching obscure content; future quality must validate the choice.
- Ranking weights are versioned configuration, not hidden constants.
- Public rank should be opt-in; raw watch history should remain private.
- Recursive curator influence must be capped to prevent runaway feedback loops.

## Intellectual property

ViewerRank is claimed as intellectual property of **Mathew Blake Ward**. Copyright © 2026 Mathew Blake Ward. All rights reserved. See [NOTICE.md](NOTICE.md) for the repository notice.

## License

No open-source license has been granted. Public availability of the repository does not by itself grant permission to copy, modify, redistribute, sublicense, commercialize, or create derivative works except where applicable law provides otherwise.
