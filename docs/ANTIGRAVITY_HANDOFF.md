# Antigravity Handoff
**State:** scaffolding only. Nothing trained, no datasets read, no fake outputs.
**Rules:** never invent columns/counts/results; resolve every `TO_BE_VERIFIED_DURING_IMPLEMENTATION` by inspecting data *at implementation time* and updating docs; keep ML/Rule/Scoring/Analytics labelled; time-based splits for forecasting; datasets never auto-merged.
**Start here:** docs/IMPLEMENTATION_ROADMAP.md step 1. Search the repo for `NOT_IMPLEMENTED_YET` to find work items.
**Open decisions:** classifier backbone; capacity data source; ARIMA viability; recovery rule sources and weights; TACO mapping; chart/map libraries; auth method.
**Run:** `pip install -r requirements.txt && python app.py && pytest`.
