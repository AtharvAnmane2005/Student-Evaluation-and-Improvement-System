# Matching model artifacts

This folder holds the three trained artifacts the Phase 7/9 matching
pipeline loads at runtime:

```
artifacts/
├── bi_encoder/       (~88MB)  fine-tuned all-MiniLM-L6-v2, sentence-transformers format
├── cross_encoder/    (~479MB) fine-tuned cross-encoder/stsb-roberta-base
└── calibrator.pkl    (~4KB)   sklearn LogisticRegression (Platt scaling)
```

**None of these are tracked in git** — `.gitignore` already excludes
`*.safetensors`/`*.bin`/`*.pt` (this was anticipated back in the original
project scaffolding), and `cross_encoder/model.safetensors` alone
(~476MB) is well over GitHub's 100MB per-file hard limit anyway, so a
plain `git add` would fail outright even without the `.gitignore` rule.

## After a fresh clone

These folders won't exist. Copy them in from wherever you're keeping the
trained artifacts (the same `bi_encoder_model.zip` /
`cross_encoder_roberta_model.zip` / `platt_calibrator.pkl` files
originally received from the model training work), so the final layout
matches the tree above exactly — `bi_encoder/config.json`,
`cross_encoder/model.safetensors`, `calibrator.pkl`, etc. directly under
this `artifacts/` folder (not nested inside an extra subfolder).

If they're missing, the app **does not crash** — `MatchingEngine` raises
`MatchingModelsUnavailable` only when a matching endpoint is actually
called (models are lazy-loaded on first use, not at startup), and the
router layer turns that into a `503 Service Unavailable` with a clear
message. Every other feature in the app works completely normally without
these files present.

## For real deployment (Render, etc.)

Bundling ~570MB of model weights into a normal git-based deploy isn't
practical. Options, roughly in order of effort:

1. **Git LFS** — tracks the large files in git without bloating the repo
   history, most platforms (including Render) support LFS-backed repos.
2. **External hosting** — upload the two model folders to somewhere like
   the Hugging Face Hub (under your own account) or a cloud storage
   bucket, and add a small startup/build script that downloads them into
   this folder before the app starts.
3. **Persistent disk / manual upload** — if the hosting platform offers
   persistent storage, upload the files there once outside the normal
   git-push deploy flow.

None of this is built yet — it's genuinely Phase 17 (Deployment)
territory, not Phase 7/9's. This phase's job was correct model wiring for
local development; deployment packaging is a separate concern.
