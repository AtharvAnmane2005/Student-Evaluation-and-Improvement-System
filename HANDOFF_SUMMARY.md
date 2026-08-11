# PLACER — Project Handoff Summary
*Generated to continue this build in a new conversation without losing context.*

---

## 0. How to use this document

Paste this whole file as your first message in a new chat, along with the latest project zip (`placer_phase11.zip` as of this writing). That gives Claude everything needed to keep building without re-deriving decisions already made.

---

## 1. What this project is

**AI-Powered Intelligent Campus Recruitment & Placement Assistance System** ("PLACER") — a final-year engineering project. Full-stack platform for Students, TPOs (Training & Placement Officers), and Admins, covering resume evaluation, semantic job matching, adaptive skill assessment, and placement analytics. Must run entirely on free-tier infrastructure (Vercel, Render, MongoDB Atlas free tier, no paid APIs).

**Tech stack:** FastAPI (Python) backend, Next.js 15 + React 19 + TypeScript + Tailwind + ShadCN frontend, MongoDB (Motor async driver), JWT auth with rotating refresh tokens.

**Location on disk:** `D:\Student Eval Sys\placer\` (Windows machine). `backend/` and `frontend/` are siblings under `placer/`.

---

## 2. Critical context: the PLACER ML model

The user has a **pre-trained resume-scoring/matching model** from a Jupyter notebook (`PLACER_RoBERTa_Training_NEW.ipynb`, already analyzed by Claude). It is a **two-stage retrieve-and-rerank semantic matcher**:

1. **Bi-encoder** (`all-MiniLM-L6-v2`, fine-tuned with `MultipleNegativesRankingLoss`) — fast retrieval via cosine similarity
2. **Cross-encoder** (`cross-encoder/stsb-roberta-base`, fine-tuned) — precise pairwise reranking
3. **Platt calibration** (`LogisticRegression`) — raw score → true match probability
4. **Hybrid formula**: `0.50 × calibrated_semantic + 0.35 × skill_coverage + 0.15 × experience_fit`, with explainability (matched/missing skills)

**Architectural decision already made:** this model becomes the engine for Module 5 (Semantic Job Matching) and Module 6 (Explainable AI) almost as-is. It does NOT do resume "quality" grading (grammar/formatting/ATS) — that's handled separately by Phase 6's rule-based parser.

**BLOCKER:** The actual trained model artifacts (bi-encoder weights, cross-encoder weights, fitted calibrator `.pkl`) are with a colleague of the user, not yet received. **Phase 7 (wrapping this model in an inference API) and Phase 9 (Semantic Matching, which depends on Phase 7) are both blocked** until those files arrive. When they do: the user needs to provide the saved model folders (sentence-transformers format for both encoders, plus the calibrator pickle) so Claude can build `app/ml/matching/inference.py` around the *exact* trained weights, per the original requirement to preserve prediction logic exactly.

**To unblock:** ask the user if the artifacts have arrived yet. If yes, request the files be uploaded, then resume Phase 7.

---

## 3. Development approach established

- **Strictly phased, incremental delivery.** Each phase: implement → py_compile syntax-check (no network access in Claude's sandbox to actually pip install/run) → user installs/runs on their real Windows machine → user reports pytest results back → fix any real bugs found → move on.
- **No placeholders, but honest about scope boundaries.** Where something is genuinely out of scope (e.g., real code execution for grading coding questions, real BKT knowledge tracing, webcam proctoring), it's explicitly flagged in `PROJECT_PROGRESS.md` as a documented decision, not silently faked or left as a TODO.
- **Out-of-order execution when blocked.** Phases 7 and 9 are skipped for now (blocked on external files); Phases 8, 10, 11 were built out of order since they don't depend on the ML model. Phase tracker in `PROJECT_PROGRESS.md` reflects this honestly (marked ⏸ Blocked, not ⬜ Not Started).
- **Every phase's completion includes:** files created, key architectural decisions (with reasoning), setup/install commands, test instructions, a verification checklist, and "notes carried forward" (known limitations, follow-ups).
- **Full project re-zipped and delivered after every phase** (old zip deleted, new one includes everything cumulative). `PROJECT_PROGRESS.md` at the repo root is the living source of truth — **read it in full before continuing**, it has far more detail than this summary.

---

## 4. Phase status

| Phase | Status |
|---|---|
| 1. Architecture, DB schema, API design | ✅ Done |
| 2. Backend setup (FastAPI, Docker, health check) | ✅ Done |
| 3. Frontend setup (Next.js scaffold, routing, login UI) | ✅ Done |
| 4. Authentication (JWT, refresh rotation, RBAC, **Google Sign-In**) | ✅ Done |
| 5. Resume module (upload, validation, versioning, storage) | ✅ Done |
| 6. Resume parsing (PyMuPDF/pdfplumber/spaCy) | ✅ Done |
| **7. Resume scoring integration (PLACER model)** | **⏸ BLOCKED — waiting on trained model artifacts** |
| 8. Placement drives (CRUD, eligibility, applications) | ✅ Done |
| **9. Semantic matching** | **⏸ BLOCKED — depends on Phase 7** |
| 10. Knowledge Tracing System (adaptive assessments) | ✅ Done |
| 11. Anti-cheat system (backend enforcement) | ✅ Done |
| 12. Student dashboard | ⬜ Not started |
| 13. TPO dashboard | ⬜ Not started |
| 14. Admin dashboard | ⬜ Not started |
| 15. Analytics | ⬜ Not started |
| 16. Testing (full pass) | ⬜ Not started (though every phase has been tested incrementally) |
| 17. Deployment | ⬜ Not started |

**Current test count: 82 passing** (`pytest -v` in `backend/`, with `.venv` activated).

---

## 5. Key architectural decisions to remember

1. **Student profile ID vs. User account ID are DIFFERENT IDs.** Every collection that references "which student" (`Resumes.student_id`, `Applications.student_id`, `AssessmentAttempts.student_id`, `KnowledgeStates.student_id`) stores the **Student profile document's own `_id`** (from the `students` collection), resolved via `StudentRepository.get_by_user_id(user_id)` — **never** the raw User account `_id` from the JWT. This was violated once during Phase 10 development and caught/fixed before shipping. **If extending this schema, always resolve through `get_by_user_id()` first.**
2. **Never concatenate pydantic model instances with raw dicts and write straight to Mongo.** Pymongo can't BSON-encode pydantic objects. When appending to a list field that was fetched (and thus contains model instances), convert with `.model_dump(mode="json")` first. Caught once in Phase 10 (`AssessmentAttempt.answers`), fixed. Fields typed as plain `list[dict]` (like `violations`, `history`) don't have this issue since they never get converted to model instances on read.
3. **Repository Pattern throughout** — `app/repositories/base.py`'s `BaseRepository[ModelT]` generic class gives every collection consistent CRUD; services never touch Motor/PyMongo directly.
4. **Auth:** access JWT (15min) in memory only on frontend (never localStorage), httpOnly refresh cookie (7d) that **rotates on every use** (old token revoked, new one issued — replay of an old token fails). Google Sign-In uses client-side ID-token verification (no client secret needed), creates accounts with `password_hash: null`.
5. **Storage:** local disk (dev) or Cloudinary (prod), selected via `STORAGE_BACKEND` env var, abstracted in `app/services/storage_service.py`. Local storage uses `local://` pseudo-URLs, never absolute filesystem paths, in the DB.
6. **Resume parsing:** PyMuPDF primary/pdfplumber fallback for text; regex for contact info; spaCy NER with heuristic fallback for name (spaCy model is optional at runtime — app doesn't crash if `en_core_web_sm` isn't downloaded, just logs a warning and degrades gracefully).
7. **Knowledge tracing:** deliberately a simple exponential-moving-average heuristic, NOT real Bayesian Knowledge Tracing — documented as a conscious choice (BKT needs calibrated params from real usage data that doesn't exist yet for a brand-new system).
8. **Adaptive assessment:** starts at Medium difficulty, correct → harder, wrong → easier, clamped at Easy/Hard, with graceful fallback to other difficulties if the ideal tier's question pool is exhausted.
9. **Grading:** MCQ fully automatic (exact-match). Coding is exact-output-match, NOT real code execution (sandboxed execution deliberately out of scope — security-sensitive, substantial feature). Descriptive is stored ungraded for manual review (no review UI built yet).
10. **Anti-cheat (backend only so far):** generic violation-type strings (not a hardcoded enum) reported to `POST /assessments/attempts/{id}/violation`, auto-submit at a configurable threshold; session-token binding as defense-in-depth beyond JWT; server-side timer enforcement; MCQ options shuffled per-delivery (safe because grading matches option text, not position); IP captured server-side; fingerprint captured once at start (not continuously re-validated, to avoid false positives from legitimate network changes).
11. **Question sourcing:** user explicitly declined web scraping (copyright/ToS risk was flagged and they agreed) and declined Open Trivia DB integration — **staying with manual bulk JSON import** (`POST /questions/import`), already built. No further work needed here.
12. **Question types:** MCQ, Coding, Descriptive confirmed sufficient by user — no true/false, fill-in-blank, or keyword-auto-grading needed.

---

## 6. Known environment quirks (Windows-specific, already solved)

- User's Python is the **Windows Store version**, which has venv/PATH quirks. Bare `python`/`pytest` commands sometimes resolve to the wrong install. **Solution in use:** always invoke via the venv's explicit path: `.venv\Scripts\python.exe -m pytest -v`, `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
- **Docker Desktop's WSL2 virtual disk defaults to C: drive** and can silently eat disk space (holds all Docker images/data, not just this project's). User has limited C: space. Two fixes applied: (a) `docker-compose.yml` now bind-mounts MongoDB data to a project-local `mongodb-data/` folder on D: instead of an opaque Docker volume; (b) user was advised to move Docker Desktop's entire disk image location to D: via Settings → Resources → Advanced (this is the more complete fix, affects all Docker data including future ML library images in Phase 7).
- **npm peer-dependency conflicts** are common with this Next.js 15 + React 19 combo (the React 19 ecosystem is still catching up on peer-dep metadata in many packages, e.g., `recharts`). **Standing fix:** `frontend/.npmrc` sets `legacy-peer-deps=true` so `npm install` doesn't need the flag manually every time.
- **Google OAuth clock-skew errors** ("Token used too early") are a Windows clock sync issue, not a code bug — fixed via `w32tm /resync /force` (admin PowerShell).
- No network access in Claude's own sandbox — all backend code is verified via `py_compile` (syntax only) and manual reasoning, never actually run with real dependencies installed. **The user's `pytest -v` run on their real machine is the actual verification step** every phase.

---

## 7. Environment setup (for a fresh continuation)

```powershell
# Backend
cd "D:\Student Eval Sys\placer\backend"
.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m spacy download en_core_web_sm   # if not already done
copy .env.example .env   # then set a real JWT_SECRET_KEY (see .env.example for how to generate)
.venv\Scripts\python.exe -m pytest -v   # should show 82 passed

# Run it
uvicorn app.main:app --reload --port 8000
# Swagger UI at http://localhost:8000/api/docs

# Frontend (separate terminal)
cd "D:\Student Eval Sys\placer\frontend"
npm install
copy .env.local.example .env.local
npm run dev
# http://localhost:3000
```

MongoDB: either `docker compose up --build` from the `placer/` root (starts Mongo + backend together), or a MongoDB Atlas free-tier connection string in `.env`.

Google Sign-In needs a free OAuth Client ID from [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) — set as `GOOGLE_CLIENT_ID` (backend `.env`) and `NEXT_PUBLIC_GOOGLE_CLIENT_ID` (frontend `.env.local`), same value in both. Without it, the Google button just doesn't render — nothing breaks.

---

## 8. Immediate next steps (pick up here)

1. **Ask the user: have the model artifacts arrived from their colleague yet?**
   - If yes → resume **Phase 7**: request the bi-encoder folder, cross-encoder folder, and calibrator `.pkl` be uploaded; build `app/ml/matching/inference.py` wrapping them exactly as trained; wire into a resume-scoring endpoint.
   - If no → continue with **Phase 12: Student Dashboard** (frontend) — the next unblocked phase in sequence. This will need to build: resume upload UI, resume score/parsed-data display, drive browsing/application UI, adaptive assessment-taking UI (which is also where Phase 11's anti-cheat client-side pieces — fullscreen API, tab-switch detection, copy/paste blocking — finally get wired in), and knowledge-state visualization.
2. Whichever path: read `PROJECT_PROGRESS.md` in full first (it's the authoritative, detailed record — this summary is a compressed pointer to it, not a replacement).
3. Continue the same phase-by-phase discipline: implement, compile-check, package as a zip, user tests on their machine, report back, fix real bugs, proceed.

---

## 9. Files to bring into the new chat

- **This summary** (paste as first message)
- **`placer_phase11.zip`** (or whatever the latest phase zip is) — extract to `D:\Student Eval Sys\placer\`, replace all
- The original **`PLACER_RoBERTa_Training_NEW.ipynb`** notebook, if starting a fresh chat that hasn't seen it — needed context for Phase 7 whenever it unblocks
- Model artifacts from the colleague, whenever they arrive
