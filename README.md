# PLACER — AI-Powered Campus Recruitment & Placement Assistance System

A full-stack placement platform for Students, TPOs (Training & Placement
Officers), and Admins — resume upload & parsing, AI-powered semantic
job matching, adaptive skill assessments with anti-cheat monitoring, and
placement analytics.

**Tech stack:** FastAPI (Python) + MongoDB backend, Next.js 15 + React 19 +
TypeScript + Tailwind frontend, JWT auth, and a fine-tuned bi-encoder /
cross-encoder pair for resume-to-job matching.

For the detailed build history, architectural decisions, and known
limitations, see [`PROJECT_PROGRESS.md`](./PROJECT_PROGRESS.md) — this
README only covers "how do I get this running."

---

## Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **MongoDB** — either Docker (`docker compose up`) or a free
  [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) cluster
- **~1GB free disk space** for the ML model weights (see below)

## 1. Clone and get the model weights

```bash
git clone <this-repo-url>
cd placer
```

The two largest model files (~560MB combined) aren't tracked in git —
they're too big for a normal git push. Everything *else* about the models
(config, tokenizer, folder structure) **is** already in the repo; you just
need to drop these two files into their already-existing folders:

1. Go to this repo's **Releases** page
2. Download `bi_encoder_model.safetensors` and `cross_encoder_model.safetensors`
3. Place them at:
   ```
   backend/app/ml/matching/artifacts/bi_encoder/model.safetensors
   backend/app/ml/matching/artifacts/cross_encoder/model.safetensors
   ```
   (exact filename `model.safetensors` in each folder — rename after downloading if needed)

If you skip this step, the app still runs completely normally — every
feature works except AI match scores, which return a `503` instead of a
crash. See `backend/app/ml/matching/artifacts/README.md` for details.

## 2. Backend setup

```bash
cd backend
python -m venv .venv

# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

.venv\Scripts\python.exe -m pip install -r requirements.txt   # Windows
# pip install -r requirements.txt                              # macOS/Linux

python -m spacy download en_core_web_sm

copy .env.example .env     # Windows
# cp .env.example .env      # macOS/Linux
```

Open `.env` and set a real `JWT_SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```
Paste the output in as `JWT_SECRET_KEY=...`. Everything else in `.env.example`
has sensible local defaults — leave as-is unless you know you need to change it
(e.g. pointing `MONGODB_URI` at an Atlas cluster instead of local Docker).

### Start MongoDB (pick one)
```bash
# Option A — Docker (from the repo root, not backend/)
docker compose up --build

# Option B — MongoDB Atlas: paste your connection string into
# backend/.env's MONGODB_URI instead, skip Docker entirely
```

### Create your first admin account (one-time)
```bash
python -m scripts.create_admin
```
Follow the prompts for email/name/password. This is the only way to get
an admin account — there's no public admin sign-up (by design).

### Run the tests
```bash
.venv\Scripts\python.exe -m pytest -v
```
Should show **109 passed**. If the 5 tests in `test_matching.py` fail or
error, double-check step 1 (the model weight files).

### Start the backend
```bash
uvicorn app.main:app --reload --port 8000
```
Swagger UI at http://localhost:8000/api/docs

## 3. Frontend setup (separate terminal)

```bash
cd frontend
npm install
copy .env.local.example .env.local   # Windows
# cp .env.local.example .env.local    # macOS/Linux
npm run dev
```
App runs at http://localhost:3000

Google Sign-In needs a free OAuth Client ID from
[console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
— set the same value as both `GOOGLE_CLIENT_ID` (backend `.env`) and
`NEXT_PUBLIC_GOOGLE_CLIENT_ID` (frontend `.env.local`). Without it, the
Google button just doesn't render — everything else works fine.

## 4. Try it out

1. Register a student account, complete your profile, upload a resume
2. Register a TPO account, create a placement drive
3. As the TPO, review applicants — ranked by AI match score
4. Log in as the admin account from step 2 above, create a question
   category, a few questions, and an assessment
5. As the student, take the assessment, then check your dashboard

## Common issues

- **"Invalid email or password" but you're sure it's right"** — usually
  means the backend process is stale (didn't pick up a recent change) or
  `python`/`uvicorn` resolved to the wrong Python install. Always invoke
  via the venv's explicit path (`.venv\Scripts\python.exe -m uvicorn ...`,
  not bare `uvicorn`), and do a full restart (close the terminal, open a
  new one) after any `pip install`.
- **`ECONNREFUSED` / "Failed to proxy" errors in the frontend terminal** —
  the backend isn't running, or isn't reachable at `localhost:8000`. Check
  the backend terminal for errors.
- **Google Sign-In errors** — see the Google OAuth setup note above; it's
  optional, everything else works without it.

For anything not covered here, `PROJECT_PROGRESS.md` has a phase-by-phase
history including known limitations and the exact test/verification
checklist used for every feature.
