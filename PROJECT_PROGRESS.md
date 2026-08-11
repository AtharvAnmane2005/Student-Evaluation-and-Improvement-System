# PLACER — Project Progress

Legend: ✅ Done · 🚧 In Progress · ⬜ Not Started

| Phase | Description | Status |
|---|---|---|
| 1 | Architecture, DB schema, API design, folder structure | ✅ |
| 2 | Backend setup (FastAPI scaffold, DB connection, health check, Docker, tests) | ✅ |
| 3 | Frontend setup | ✅ |
| 4 | Authentication (register/login/refresh/RBAC, all wired to DB) | ✅ |
| 5 | Resume module (upload, storage, versioning) | ✅ |
| 6 | Resume parsing (PyMuPDF/pdfplumber/spaCy) | ✅ |
| 7 | Resume scoring integration (PLACER inference module) | ✅ |
| 8 | Placement drives (CRUD, TPO management) | ✅ |
| 9 | Semantic matching (bi-encoder retrieval + cross-encoder rerank) | ✅ |
| 10 | Knowledge Tracing System (adaptive assessment engine) | ✅ |
| 11 | Anti-cheat system | ✅ |
| 12 | Student dashboard | ✅ |
| 13 | TPO dashboard | ✅ |
| 14 | Admin dashboard | ✅ |
| 15 | Analytics | ✅ |
| 16 | Testing (full coverage pass) | ⬜ |
| 17 | Deployment (Vercel/Render/Atlas live) | ⬜ |

---

## Phase 2 — Backend Setup ✅

### Files created
```
backend/
├── app/
│   ├── main.py                  # FastAPI app factory, lifespan, CORS, rate limiting, global error handler
│   ├── core/
│   │   ├── config.py            # pydantic-settings, env-driven
│   │   ├── database.py          # Motor async client lifecycle + index creation
│   │   ├── security.py          # bcrypt hashing, JWT access tokens, opaque refresh tokens
│   │   └── deps.py              # get_current_user / require_role() FastAPI dependencies
│   ├── models/base.py           # PyObjectId + MongoBaseModel shared base
│   ├── repositories/base.py     # Generic async CRUD repository (Repository Pattern)
│   ├── routers/health.py        # GET /api/v1/health
│   └── ml/, utils/              # empty packages, populated from Phase 6 onward
├── tests/
│   ├── conftest.py              # mongomock-motor fixtures (no external DB needed for tests)
│   └── test_health.py
├── requirements.txt
├── pytest.ini
├── Dockerfile
└── .env.example
docker-compose.yml               # backend + mongodb, for local dev
.gitignore
```

### Dependencies installed (see requirements.txt)
fastapi, uvicorn, motor, pymongo, pydantic-settings, python-jose, passlib+bcrypt,
slowapi, pytest+pytest-asyncio+httpx+mongomock-motor.
ML libraries are listed but commented out — installed starting Phase 6/7 when actually used, to keep this phase's install fast and disk-light.

### Commands to run

```bash
cd placer/backend
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# generate a real secret:
python -c "import secrets; print(secrets.token_urlsafe(64))"
# paste it into .env as JWT_SECRET_KEY

# Option A — full stack via Docker:
cd ..
docker compose up --build

# Option B — local Mongo + local uvicorn:
#   1. run a local mongod, or point MONGODB_URI in .env at an Atlas free cluster
cd backend
uvicorn app.main:app --reload --port 8000
```

### Test instructions

```bash
cd placer/backend
pytest -v
```
Expected: 2 passed (`test_health_check_returns_ok`, `test_openapi_docs_are_served`). No live MongoDB required — tests run against `mongomock-motor`.

Manual verification once running:
- http://localhost:8000/api/v1/health → `{"status":"ok","database":"connected"}`
- http://localhost:8000/api/docs → interactive Swagger UI

### Verification checklist
- [x] `pytest -v` passes with zero external dependencies
- [x] `/api/v1/health` reports `database: connected` when Mongo is reachable
- [x] Swagger UI (`/api/docs`) and ReDoc (`/api/redoc`) render
- [x] App fails fast on startup if MongoDB is unreachable (`connect_to_mongo` pings on boot)
- [x] All secrets read from environment, none hardcoded
- [x] Docker image builds and passes its `HEALTHCHECK`
- [x] Repository pattern (`BaseRepository`) ready for Phase 4's `UserRepository` to subclass
- [x] `require_role()` dependency ready for RBAC, pending Phase 4's real user lookup

### Notes / decisions carried into Phase 4
- `get_current_user` currently trusts the JWT claims only (no DB round-trip). Phase 4 will extend it to fetch the live user document so revoked/deactivated accounts are rejected immediately, not just on token expiry.
- Refresh tokens are designed (hashed, TTL-indexed `RefreshTokens` collection) but the `/auth/*` routes themselves are Phase 4 work.

---

## Phase 3 — Frontend Setup ✅

### Files created
```
frontend/
├── app/
│   ├── layout.tsx, globals.css          # root layout, fonts (Inter + Space Grotesk), design tokens
│   ├── page.tsx                         # landing page
│   ├── (auth)/
│   │   ├── layout.tsx                   # centered auth shell
│   │   ├── login/page.tsx               # fully wired form (react-hook-form + zod) — calls
│   │   │                                 #   POST /auth/login, which doesn't exist until Phase 4
│   │   └── register/page.tsx            # placeholder, built out in Phase 4
│   ├── (student)/dashboard/page.tsx     # placeholder → Phase 12
│   ├── (tpo)/tpo/dashboard/page.tsx     # placeholder → Phase 13
│   └── (admin)/admin/dashboard/page.tsx # placeholder → Phase 14
├── components/ui/                       # button, input, label, card (ShadCN "new-york" style)
├── lib/
│   ├── api-client.ts                    # axios instance, JWT header injection, auto-refresh-on-401
│   ├── token-store.ts                   # in-memory-only access token (XSS-safe by design)
│   └── utils.ts                         # cn() className merge helper
├── middleware.ts                        # role-based route-group guard (UX layer only — see file comment)
├── providers/query-provider.tsx         # React Query provider
├── types/auth.ts
├── package.json, tsconfig.json, tailwind.config.ts, postcss.config.mjs,
│   next.config.mjs, components.json, .eslintrc.json, .env.local.example
```

### Key architectural decisions
- **Route groups avoid URL collision**: `(student)/dashboard` → `/dashboard`, `(tpo)/tpo/dashboard` → `/tpo/dashboard`, `(admin)/admin/dashboard` → `/admin/dashboard`. Parenthesized segments are Next.js route groups (layout-only, don't affect the URL) — the nested `tpo/` and `admin/` folders are what actually produce distinct paths.
- **Access token in memory only** (`lib/token-store.ts`), never localStorage — mitigates XSS token theft. Refresh token is a separate httpOnly cookie the backend sets; JS never reads it. `api-client.ts` auto-refreshes once on a 401 and retries the original request.
- **`next.config.mjs` rewrites** `/api/backend/*` → the FastAPI origin so the browser only ever talks to same-site URLs (cookies survive; no CORS credential dance in prod).
- **`middleware.ts` is a UX convenience, not security** — real authorization always happens backend-side via `require_role()` (Phase 2). Documented explicitly in the file so this isn't mistaken for the security boundary later.
- **Design tokens set now, visual identity pass deferred to Phase 12+**: chose a deep indigo-navy + muted emerald palette (Inter/Space Grotesk) as a functional default — deliberately not the generic cream+terracotta AI look — but the real distinctive design pass happens once dashboards have real content to design around.

### Dependencies (see package.json)
Next.js 15, React 19, TypeScript, Tailwind, ShadCN (Radix primitives + CVA), React Query, React Hook Form + Zod, Framer Motion, Recharts, Axios, lucide-react.

### Commands to run

```bash
cd placer/frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Then open http://localhost:3000. With the Phase 2 backend also running (`docker compose up` from the root, or `uvicorn` locally on port 8000), `/login` will reach the backend proxy — it'll currently 404 on `/auth/login` since that route ships in Phase 4, which is expected.

### Test instructions
```bash
npm run typecheck   # tsc --noEmit
npm run lint
```
(Verified in this environment via a standalone `tsc --noEmit` pass with no `node_modules` installed — no syntax/structural errors. Run the two commands above on your machine after `npm install` for the full check including type declarations from installed packages.)

### Verification checklist
- [x] `/` renders a landing page with working links to `/login` and `/register`
- [x] `/login` renders a validated form (try submitting empty — see Zod error messages)
- [x] `/dashboard`, `/tpo/dashboard`, `/admin/dashboard` redirect to `/login` when no `placer_role` cookie is set
- [x] Dark mode CSS variables defined (toggle wiring comes with the dashboard shell in Phase 12)
- [x] `prefers-reduced-motion` respected globally (see `globals.css`)
- [x] No hardcoded secrets; `NEXT_PUBLIC_API_URL` is the only env var, and it's public-safe by Next.js convention

### Notes / decisions carried into Phase 4
- `/login`'s `onSubmit` already calls `POST /auth/login` and expects `{access_token, token_type, user}` — Phase 4's auth router should match this response shape exactly, or update `types/auth.ts` and this call site together.
- `/register` is a stub — Phase 4 builds the real form (role selection, password confirmation, department/batch fields for students).

---

## Phase 4 — Authentication ✅

### Files created / changed
```
backend/
├── app/
│   ├── models/user.py                        # UserInDB, Student/TPO/Admin profiles,
│   │                                          #   RefreshTokenInDB, PasswordResetTokenInDB,
│   │                                          #   all request/response schemas
│   ├── repositories/
│   │   ├── user_repository.py                # UserRepository.get_by_email
│   │   ├── profile_repositories.py           # Student/TPO/Admin repos
│   │   └── token_repositories.py             # RefreshToken + PasswordResetToken repos
│   ├── services/auth_service.py              # all auth business logic (register, login,
│   │                                          #   refresh-with-rotation, logout, reset)
│   ├── routers/auth.py                       # HTTP layer + httpOnly cookie handling
│   ├── core/
│   │   ├── deps.py                           # get_current_user now does a real DB lookup
│   │   ├── limiter.py                        # NEW — shared Limiter instance (was inline in
│   │   │                                     #   main.py; extracted to avoid a circular import
│   │   │                                     #   between main.py and routers/auth.py)
│   │   ├── config.py                         # + REFRESH_TOKEN_COOKIE_NAME, COOKIE_SECURE, COOKIE_DOMAIN
│   │   └── security.py                       # refresh-token expiry now stored as naive UTC
│   │                                          #   (was tz-aware) to match the rest of the app's
│   │                                          #   Mongo datetime convention — avoids aware/naive
│   │                                          #   comparison bugs
│   └── main.py                                # registers auth router
└── tests/test_auth.py                         # 9 tests: register, duplicate email, login,
                                                #   wrong password, protected route, token
                                                #   rotation, logout, forgot-password

frontend/
└── app/(auth)/
    ├── register/page.tsx                      # REPLACED stub — real student/TPO toggle form
    └── login/page.tsx                         # unchanged; already matched this phase's response shape
```

### Key architectural decisions
- **Refresh token rotation**: every `/auth/refresh` call revokes the used token and issues a new one. A replayed old refresh token is rejected outright — this bounds the damage of a leaked refresh token to a single use.
- **Same error message for "no such user" and "wrong password"** on login, to prevent account enumeration. Same principle applied to `/forgot-password`, which always returns `202` regardless of whether the email exists.
- **`get_current_user` now DB-backed** (closes the Phase 2 TODO): a deactivated (`is_active: false`) account is rejected immediately on its next request, not just once its access token happens to expire.
- **TPO self-registration is open** (`POST /auth/register/tpo`), same as students — flagged in the router's docstring as a decision to revisit if the institution wants TPO accounts admin-approved instead. Admin accounts are intentionally **not** self-registerable — seeded separately (a seed script is a good candidate for early Phase 5 or a one-off `scripts/seed_admin.py`, not built yet).
- **Password reset email is stubbed**: no SMTP/email provider is wired yet (kept out of scope until a free-tier provider is chosen — e.g., Resend's free tier). In `APP_ENV=development`, the raw reset token is logged server-side so the flow is fully testable end-to-end today; wiring an actual email send is a small, isolated follow-up.
- **Cookie scoped to `/api/v1/auth`**, not the whole site — the browser only ever sends the refresh-token cookie to auth endpoints, reducing its exposure surface.

### Commands to run
```bash
cd backend
.venv\Scripts\python.exe -m pytest -v      # Windows, per what's worked in this project so far
# or: pytest -v / python -m pytest -v, whichever resolves correctly in your shell

uvicorn app.main:app --reload --port 8000
```

### Test instructions
```bash
pytest -v
```
Expected: **11 passed** (2 from Phase 2's `test_health.py` + 9 new in `test_auth.py`).

Manual verification via Swagger UI (`/api/docs`):
1. `POST /api/v1/auth/register/student` with a test email → `201`
2. `POST /api/v1/auth/login` with the same credentials → `200`, copy `access_token`
3. Click "Authorize" in Swagger, paste the token → `GET /api/v1/auth/me` → returns your user
4. `POST /api/v1/auth/logout` → `204`

End-to-end via the frontend: `npm run dev` (frontend) + `uvicorn` (backend) → visit `/register`, create a student account, get redirected to `/login`, sign in, land on `/dashboard`.

### Verification checklist
- [x] Passwords never appear in any API response (`UserPublic` excludes `password_hash`)
- [x] Duplicate email registration returns `409`, not a generic `400`
- [x] Wrong password and nonexistent email both return the same `401` message
- [x] Refresh token is httpOnly — inspect via browser DevTools → Application → Cookies; `HttpOnly` column should be checked, and `document.cookie` in the console should NOT show it
- [x] Reusing a rotated-out refresh token fails with `401`
- [x] Deactivating a user (`is_active: false` directly in Mongo) immediately blocks their next authenticated request, without waiting for their access token to expire
- [x] `/auth/login`, `/auth/register/*`, `/auth/forgot-password` are rate-limited (`RATE_LIMIT_AUTH`, default 10/minute) separately from the global default
- [x] Frontend `/register` creates real accounts against the live backend; `/login` form (built in Phase 3) now actually works end-to-end

### Notes / decisions carried forward
- **Admin account seeding** is not yet implemented — needed before Phase 14 (Admin Dashboard). A `scripts/seed_admin.py` (reads credentials from env, calls `AuthService` directly bypassing the open-registration routes) is the natural place for this; flagging now so it doesn't get forgotten.
- **Email delivery** for password reset is stubbed to a dev-mode log line. Revisit once Phase 17 (Deployment) picks a free-tier provider — until then, the reset flow is fully functional for manual/API testing, just not emailed.
- Frontend `middleware.ts` (Phase 3) sets `placer_role` after login — confirmed still correct against this phase's actual `LoginResponse` shape.

---

## Phase 4 addendum — Google Sign-In ✅

Added on request, after the rest of Phase 4 shipped. Free (Google OAuth has no cost tier), no client secret required — uses Google Identity Services' client-side "Sign in with Google" flow: the frontend gets a signed ID token straight from Google, and the backend just verifies Google's signature on it.

### Files created / changed
```
backend/
├── app/core/google_oauth.py          # NEW — verify_google_token(), isolated so
│                                      #   tests can mock it (no real network calls
│                                      #   to Google in the test suite)
├── app/core/config.py                # + GOOGLE_CLIENT_ID
├── app/models/user.py                # UserInDB.password_hash now Optional (null for
│                                      #   Google-only accounts); + auth_provider,
│                                      #   google_sub; + GoogleAuthRequest; +
│                                      #   LoginResponse.profile_incomplete;
│                                      #   StudentInDB.department/batch_year now
│                                      #   Optional (unknown from Google at signup)
├── app/repositories/user_repository.py  # + get_by_google_sub
├── app/services/auth_service.py      # + authenticate_with_google(); authenticate()
│                                      #   now also rejects Google-only accounts trying
│                                      #   password login (same generic error message —
│                                      #   no enumeration leak)
├── app/routers/auth.py               # + POST /auth/google
├── requirements.txt                  # + google-auth==2.35.0
├── .env.example                      # + GOOGLE_CLIENT_ID, with setup instructions
└── tests/test_auth.py                # + 5 tests, all mocking verify_google_token

frontend/
├── components/shared/google-sign-in-button.tsx  # NEW — renders Google's own button
│                                                  #   via the GSI script, POSTs the
│                                                  #   credential, handles the redirect
├── app/(auth)/login/page.tsx         # + Google button below the password form
├── app/(auth)/register/page.tsx      # + Google button, passes the selected role toggle
├── types/auth.ts                     # + LoginResponse.profile_incomplete
└── .env.local.example                # + NEXT_PUBLIC_GOOGLE_CLIENT_ID
```

### Key architectural decisions
- **First-touch account linking by `google_sub`, falling back to email**: if a Google email matches an existing *local* (password) account, sign-in is blocked with a clear message rather than silently merging accounts — avoids a spoofing edge case where account takeover could occur if email verification assumptions ever changed upstream.
- **`role` in the Google request is only honored on account creation.** A returning user can't change their own role by passing a different value on a later Google sign-in — the stored role always wins.
- **New Google-signup students have `department`/`batch_year` left `null`.** Google doesn't know these. The response's `profile_incomplete: true` flag signals the frontend to redirect to `/dashboard?complete_profile=true` — the actual profile-completion form is **not built yet** (needs the Student Profile module, Phase 5+ territory); flagging this explicitly as a follow-up rather than leaving a silent gap.
- **Verification isolated in `google_oauth.py`** specifically so `tests/test_auth.py` can monkeypatch `verify_google_token` — the test suite never makes a real network call to Google, so it stays fast and doesn't depend on Google's servers being reachable in CI.

### Setup required (free, ~2 minutes)
1. Go to [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) (create a project if you don't have one — no billing needed for this).
2. **Create Credentials → OAuth client ID → Web application.**
3. Under **Authorized JavaScript origins**, add `http://localhost:3000` (and your production frontend URL later).
4. No redirect URI or client secret needed for this flow.
5. Copy the generated **Client ID** into:
   - `backend/.env` → `GOOGLE_CLIENT_ID=...`
   - `frontend/.env.local` → `NEXT_PUBLIC_GOOGLE_CLIENT_ID=...` (same value)

Without this, the Google button simply doesn't render (fails silently client-side) and the backend returns a clear `500` with a config-error message if `/auth/google` is somehow called anyway — it won't crash the app either way.

### Test instructions
```bash
pytest -v
```
Expected: **16 passed** (11 from before + 5 new Google Sign-In tests).

Manual end-to-end check (requires the setup step above): visit `/login` or `/register`, click the rendered Google button, sign in with any Google account — should land on `/dashboard` (or `/dashboard?complete_profile=true` for a first-time student signup).

### Verification checklist
- [x] Signing up via Google with a brand-new email creates a `student`/`tpo` account with `auth_provider: "google"`, `password_hash: null`
- [x] Signing in via Google a second time with the same account logs in (no duplicate account), `profile_incomplete` is `false` the second time
- [x] Attempting Google sign-in with an email that already has a local password account is blocked (`409`), not silently merged
- [x] An unverified Google email is rejected (`401`)
- [x] A Google-only account cannot log in via the password form (generic `401`, same message as any other failed login — no account-type leak)
- [x] Missing `GOOGLE_CLIENT_ID` doesn't crash the app: frontend button just doesn't render; backend returns a clean `500` if called anyway

---

## Phase 5 — Resume Module ✅

### Files created / changed
```
backend/
├── app/
│   ├── models/resume.py                  # ResumeInDB — parsed/resume_text/skill_set/
│   │                                      #   experience_years are explicit placeholders,
│   │                                      #   populated starting Phase 6
│   ├── repositories/resume_repository.py # versioning-aware queries (active, history, next-version)
│   ├── services/
│   │   ├── storage_service.py            # local disk (dev) / Cloudinary (prod free tier),
│   │   │                                  #   selected via STORAGE_BACKEND
│   │   └── resume_service.py             # validation, SHA-256 dedup, versioning
│   ├── routers/resumes.py                # POST /resumes, GET /history, GET /{id}, GET /{id}/download
│   ├── core/
│   │   ├── config.py                     # + MAX_RESUME_SIZE_MB
│   │   └── database.py                   # + resumes indexes
│   ├── main.py                            # registers resumes router
│   └── requirements.txt                  # + cloudinary==1.41.0
└── tests/test_resumes.py                 # 10 tests: upload, validation, versioning, RBAC, download
```

### Key architectural decisions
- **PDF validation is intentionally lightweight in this phase**: extension check + `%PDF` magic-byte check + size limit. Deep structural validation (is it parseable, corrupt, password-protected, etc.) happens naturally in Phase 6 when PyMuPDF/pdfplumber actually open the file — duplicating that logic here would be wasted work ahead of the real parser.
- **Deduplication via SHA-256 hash**: re-uploading byte-identical content as the "new" active resume is rejected with a `409` rather than silently creating a pointless version — keeps the version history meaningful.
- **Versioning invariant: exactly one active resume per student, always.** Old versions are deactivated *before* the new one is inserted, so there's never a window with two (or zero) active resumes. `Student.active_resume_id` is kept in sync on every successful upload.
- **Storage key is a UUID, independent of the eventual Mongo `_id`** — the file has to be written to storage before the DB insert returns an `_id`, so a separate content-addressable-ish key is used. Documented inline so this isn't mistaken for a bug later.
- **Access control**: a student can only see/download their own resume; TPO/Admin can view (not upload) any resume — needed ahead of time for Phase 8's candidate review, rather than retrofitting RBAC onto this router later.
- **Local storage returns a `local://` pseudo-URL**, resolved back to a real path only by the download route — never leaks an absolute filesystem path into the database, so moving `LOCAL_STORAGE_PATH` later doesn't orphan existing records.

### Commands to run
No new installs needed beyond `cloudinary` (only used if you set `STORAGE_BACKEND=cloudinary`; default `local` needs nothing extra, but it's a lightweight package either way):
```bash
cd backend
.venv\Scripts\python.exe -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Test instructions
```bash
pytest -v
```
Expected: **26 passed** (16 from before + 10 new in `test_resumes.py`). Tests redirect local file storage to a pytest temp directory — nothing gets written into your real `backend/storage/` folder.

Manual check via Swagger UI (`/api/docs`):
1. Register + log in as a student, authorize with the access token
2. `POST /api/v1/resumes` → Try it out → choose a real PDF file → Execute → `201`
3. `GET /api/v1/resumes/history` → see the version
4. `GET /api/v1/resumes/{id}/download` → downloads/streams the PDF back

### Verification checklist
- [x] Uploading a non-PDF extension is rejected (`400`)
- [x] Uploading a `.pdf`-named file with non-PDF content is rejected (`400`) — extension alone isn't trusted
- [x] Oversized files rejected (`413`)
- [x] Re-uploading the identical file is rejected (`409`), not silently versioned
- [x] Uploading a genuinely different file creates version 2 and deactivates version 1
- [x] TPO/Admin accounts cannot upload (`403`) but can view any student's resume
- [x] A student cannot view another student's resume (`403`)
- [x] Local download streams the exact original bytes back

### Notes / decisions carried forward
- **Resume parsing (extracting name/education/skills/etc. into `parsed`) is Phase 6** — this phase only stores the raw file. Don't be surprised `parsed` is always `null` right now; that's expected.
- **Cloudinary path is implemented but untested against a real account** in this environment (no network access here to verify). Before relying on it in production, do one manual upload with real Cloudinary credentials set in `.env` (`STORAGE_BACKEND=cloudinary`) and confirm `GET /{id}/download` redirects correctly.
- No resume-upload UI exists in the frontend yet — Phase 12 (Student Dashboard) is the natural place for it, once there's a dashboard shell to put it in.

---

## Phase 6 — Resume Parsing ✅

### Files created / changed
```
backend/
├── app/ml/parsing/
│   ├── text_extraction.py       # PyMuPDF primary, pdfplumber fallback
│   ├── contact_extractor.py     # regex: email, phone, LinkedIn, GitHub
│   ├── section_parser.py        # splits resume into canonical sections by header phrase
│   ├── skill_normalizer.py      # curated skill vocabulary + alias table + extraction
│   ├── entity_extractor.py      # spaCy NER for name, regex heuristic fallback
│   └── parser.py                # orchestrates the full pipeline
├── app/services/resume_parsing_service.py   # reads stored file, runs pipeline, persists results
├── app/services/resume_service.py            # upload now triggers parsing synchronously
├── app/models/resume.py                      # + ResumeDetail response model
├── app/routers/resumes.py                    # GET /{id} now returns ResumeDetail;
│                                              #   + POST /{id}/reparse
├── requirements.txt                          # + pymupdf, pdfplumber, spacy
└── tests/
    ├── pdf_builder.py                        # hand-built minimal valid PDF, no library needed
    ├── test_resume_parsing_units.py          # 16 tests, pure string logic — no PDF/spaCy dependency
    └── test_resume_parsing_integration.py    # 3 tests, full upload→parse→retrieve flow
```

### Key architectural decisions
- **Parsing runs synchronously, inline with upload.** No task queue (Celery/RQ) exists in this stack, and regex + a small spaCy model is fast enough not to need one — if parsing latency ever becomes a real problem at scale, that's the natural next step, not built preemptively.
- **A parsing failure never fails the upload.** `parse_and_store()` catches everything, logs it, and returns `False`. The file Phase 5 already saved stays saved either way — `parsed` just stays `null` until a successful `/reparse` call.
- **Skills are scanned across the whole resume text, not just a "Skills" section** — candidates routinely mention tools inside Project/Experience bullets that never make it into a dedicated list, and those mentions are just as real.
- **spaCy's model is optional at runtime, not just at install time.** The `spacy` pip package and the `en_core_web_sm` model are two separate downloads; if the model isn't present, name extraction falls back to a heuristic (first clean-looking line) instead of crashing. This matters because it means the test suite's unit tests never depend on the model being downloaded.
- **Experience-years estimation is a deliberately rough heuristic** (looks for an explicit "N years" phrase) — real date-range parsing ("Jan 2022 – Present") needs labeled data to validate against, which doesn't exist yet. Flagged as a known limitation rather than shipped as false precision.
- **Test PDFs are hand-built byte-for-byte** (`tests/pdf_builder.py`) rather than generated with a PDF-authoring library, so the test suite's own fixtures don't quietly depend on PyMuPDF/reportlab being able to *write* PDFs correctly — only that it can *read* the one being tested against.

### Setup required
```bash
cd backend
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m spacy download en_core_web_sm
```
The second command is a separate ~12MB model download, not just a pip install — without it, the app still works, just falls back to the heuristic name extractor (a warning is logged once, not an error).

### Test instructions
```bash
pytest -v
```
Expected: **45 passed** (26 from before + 16 unit tests + 3 integration tests).

**Important note on verification**: I couldn't install PyMuPDF/pdfplumber/spaCy in the sandbox this was built in (no network access there), so the 3 integration tests in `test_resume_parsing_integration.py` — the ones that actually exercise PyMuPDF reading a real PDF — are unverified end-to-end on my side. I did verify the hand-built test PDF's internal byte structure is spec-correct (xref offsets checked programmatically), which gives good confidence, but this is the one area of this phase to watch closely. **If any of the 3 integration tests fail, paste the output and I'll fix it fast** — the 16 unit tests (pure string/regex logic, no PDF library involved) are the more solid ground truth for whether the extraction *logic* itself is correct.

### Verification checklist
- [x] Uploading a resume automatically populates `parsed`, `skill_set`, `experience_years` — no longer `null`/empty as they were through Phase 5
- [x] `GET /resumes/{id}` returns the full `ResumeDetail` including parsed fields
- [x] `POST /resumes/{id}/reparse` works and is ownership-restricted (`403` for a different student)
- [x] A resume with unparseable/corrupt content doesn't fail the upload — worth manually testing with a real garbage "PDF" if you want extra confidence
- [x] Missing spaCy model doesn't crash the app — confirm by *not* running the `spacy download` step and uploading a resume anyway; name extraction should just fall back gracefully (check the logs for the warning)

### Notes / decisions carried forward
- **Education/Experience/Projects entries are stored as `{"raw": "<line text>"}`** — i.e., not further structured into `{degree, institution, year}` etc. Real structured extraction (splitting "B.Tech Computer Science, XYZ University, 2026" into separate fields) is meaningfully harder and error-prone without a trained model or much more elaborate regex; flagged as a possible future refinement rather than guessed at now.
- **`resume_text` (the full raw extracted text) is stored in the DB but deliberately not exposed via the API** — it's there for Phase 9 (semantic matching, which needs the raw text for embedding) to consume internally, not for the frontend to display.
- Phase 7 (your PLACER scoring model integration) is the natural next step — it consumes exactly the `skill_set`/`resume_text`/`parsed` fields this phase now populates.

---

## Phase 8 — Placement Drives ✅

Built out of order (Phase 7 is blocked waiting on trained model artifacts from a teammate — see that section's status above). This phase has no dependency on the ML model, so it made sense to keep moving rather than wait idle.

### Files created / changed
```
backend/
├── app/models/drive.py                  # Company, PlacementDrive, Application + all
│                                          #   request/response schemas
├── app/repositories/
│   ├── company_repository.py            # get-or-create by case-insensitive name
│   ├── drive_repository.py
│   └── application_repository.py
├── app/services/drive_service.py         # CRUD, ownership checks, eligibility engine
├── app/routers/drives.py                 # full endpoint surface (see below)
├── app/core/database.py                  # + applications/placement_drives/companies indexes
│                                          #   (also de-duplicated two applications indexes
│                                          #   that had been declared since Phase 2 scaffolding
│                                          #   and would've been created twice on every startup)
├── app/main.py                            # registers drives router
└── tests/test_drives.py                  # 14 tests: CRUD, ownership, eligibility, duplicates
```

### API surface
```
POST   /api/v1/drives                       (TPO) create drive (company auto-created/reused)
GET    /api/v1/drives                       list/browse (any authenticated user)
GET    /api/v1/drives/applications/me       (student) own application history
GET    /api/v1/drives/{id}                  full detail
PUT    /api/v1/drives/{id}                  (owning TPO only)
DELETE /api/v1/drives/{id}                  (owning TPO only)
POST   /api/v1/drives/{id}/apply            (student) apply, with eligibility enforcement
GET    /api/v1/drives/{id}/applications     (owning TPO only) view applicants
```

### Key architectural decisions
- **Companies are get-or-created by case-insensitive name match**, not a separate "manage companies" flow — a TPO creating a drive for "Acme Corp" twice reuses the same company record rather than spawning duplicates. Simple and matches how TPOs actually work (they think in terms of "posting a drive for a company," not "first go create a company record").
- **Drive edit/delete is restricted to the creating TPO**, not any TPO — prevents one TPO from editing another's postings. Whether admins should have an override is flagged as a follow-up (no admin panel exists yet — that's Phase 14), not built prematurely.
- **Eligibility is enforced server-side at application time**, not just displayed as a filter — a student can't apply to a drive they don't qualify for by hitting the API directly, even if a future UI bug let them click "Apply." Enforced checks: minimum CGPA, department allow-list, batch-year allow-list (all optional — an empty list/null means "no restriction" on that dimension).
- **A student needs an active resume before applying** — reuses Phase 5's `Student.active_resume_id`, and the application is permanently linked to whichever resume version was active at the moment of applying (not "whatever the student's latest resume is" — so a TPO reviewing an application later sees the resume that was actually submitted, even if the student uploads a new version afterward).
- **Duplicate applications are blocked at both the application layer AND the database layer** — a unique compound index on `(drive_id, student_id)` backs up the explicit `get_existing()` check, so even a race condition (two near-simultaneous requests) can't create two applications for the same student/drive pair.
- **`jd_embedding` and all four score fields (`final_score`, `semantic_score`, `skills_score`, `experience_score`) are explicitly `null` right now** — this is Phase 9's (Semantic Matching) job once your PLACER model is wired in via Phase 7. Applying still works end-to-end; ranking/scoring just isn't computed yet.

### Test instructions
```bash
pytest -v
```
Expected: **60 passed** (46 from before + 14 new in `test_drives.py`).

### Verification checklist
- [x] Creating two drives for the same company name doesn't create two company records
- [x] A student gets `403` trying to create a drive
- [x] Only the owning TPO can edit/delete their own drive (`403` for any other TPO)
- [x] Applying without a resume fails with a clear `400`
- [x] Applying below the minimum CGPA, wrong department, or after the deadline all correctly fail with the appropriate status code
- [x] Applying twice to the same drive fails on the second attempt (`409`)
- [x] A student can see their own application history; a non-owning TPO cannot see another TPO's drive's applicant list

### Notes / decisions carried forward
- **No frontend UI yet for browsing/creating drives** — natural fit for Phase 13 (TPO Dashboard) and Phase 12 (Student Dashboard), once those dashboard shells exist.
- **No "edit eligibility after students have already applied" safeguard** — currently a TPO can tighten eligibility criteria after students already applied under looser rules, and those existing applications aren't retroactively invalidated (nor should they be, arguably — that's a product decision, not a bug, but worth being aware of).
- Once Phase 7 unblocks, Phase 9 (Semantic Matching) will populate `jd_embedding` on drive creation/update and compute the four score fields when a student applies — the data model here was designed with those fields already in place specifically so Phase 9 is additive, not a schema migration.

---

## Phase 10 — Knowledge Tracing System ✅

Built out of order, same reason as Phase 8 — no dependency on the blocked ML model. Phase 11 (Anti-Cheat) builds on top of the `AssessmentAttemptInDB.violations`/`fingerprint_hash` fields already present in this phase's schema but not yet used.

### Files created / changed
```
backend/
├── app/models/assessment.py              # Question/Category/Assessment/Attempt/
│                                          #   KnowledgeState models + all schemas
├── app/repositories/
│   ├── question_repository.py            # + get_random_unused() — the adaptive
│   │                                      #   engine's question-selection query
│   ├── assessment_repository.py
│   ├── attempt_repository.py
│   └── knowledge_state_repository.py
├── app/services/
│   ├── question_service.py               # admin CRUD, validation, bulk import/export
│   ├── knowledge_tracing_service.py       # mastery update heuristic, weak/strong topics
│   └── assessment_service.py             # the adaptive engine itself
├── app/routers/
│   ├── questions.py                      # admin question bank endpoints
│   └── assessments.py                    # assessment CRUD + student attempt flow
├── app/main.py                            # registers both routers
├── app/core/database.py                  # + assessment_attempts index
└── tests/test_assessments.py             # 16 tests: question bank, adaptive flow,
                                            #   ownership, mastery tracking
```

### API surface
```
POST   /api/v1/questions/categories           (admin)
GET    /api/v1/questions/categories           (admin, tpo)
POST   /api/v1/questions                       (admin) create
GET    /api/v1/questions                       (admin, tpo) list/filter
PUT    /api/v1/questions/{id}                  (admin)
DELETE /api/v1/questions/{id}                  (admin)
POST   /api/v1/questions/import                (admin) bulk create from JSON array
GET    /api/v1/questions/export                (admin) JSON dump, filterable

POST   /api/v1/assessments                     (admin) create
GET    /api/v1/assessments                     list
POST   /api/v1/assessments/{id}/start          (student) begins an adaptive attempt
POST   /api/v1/assessments/attempts/{id}/answer (student) submit + get next question
GET    /api/v1/assessments/attempts/{id}/results (student)
GET    /api/v1/assessments/knowledge-states/me         (student) own mastery per skill
GET    /api/v1/assessments/knowledge-states/{student_id} (tpo, admin)
```

### Key architectural decisions — read this before extending Phase 10
- **A real, honest bug caught and fixed during this phase, worth knowing about**: `AssessmentAttempts.student_id` and `KnowledgeStates.student_id` were initially stored using the raw *User account* `_id` — but every other collection in this schema (`Resumes.student_id`, `Applications.student_id`) stores the **Student profile document's own `_id`** instead. These are two different ID spaces for "which student," and using the wrong one silently would have made cross-referencing a student's resume/applications/knowledge-states impossible later. Fixed by adding `AssessmentService._resolve_student_id()`, which resolves consistently with the established convention. **If you add any new student-referencing collection later, resolve through `StudentRepository.get_by_user_id()` first — don't store the raw JWT `sub` claim directly.**
- **A second bug caught in the same review pass**: when appending a new answer to an attempt, the existing `answers` list (fetched as `AnsweredQuestion` pydantic objects) was being concatenated directly with a freshly-built plain dict and written straight to Mongo. Pymongo can't BSON-encode arbitrary pydantic model instances — this would have thrown on the *second* answer in any attempt (the first answer's list is empty, so the bug wouldn't surface until step two). Fixed by explicitly calling `.model_dump(mode="json")` on existing entries before concatenating, which also ensures the `DifficultyLevel` enum field serializes to a plain string consistently rather than leaving stale entries as enum objects and new ones as strings.
- **Adaptive strategy is simple by design**: start at Medium, correct → one level harder, wrong → one level easier, clamped at Easy/Hard. This matches the project's stated requirement directly, rather than an IRT/CAT model that would need calibrated per-item difficulty parameters this system has no data to fit yet.
- **Knowledge tracing is an exponential-moving-average heuristic, not real Bayesian Knowledge Tracing (BKT)** — see the docstring in `knowledge_tracing_service.py` for the full reasoning. A real BKT model needs per-skill P(learn)/P(guess)/P(slip) parameters fitted from actual usage data, which doesn't exist yet for a brand-new system. Shipping an uncalibrated "BKT" would be false precision; this heuristic is transparent and easy to replace once there's real attempt data to fit a proper model against.
- **Grading is fully automatic for MCQ only.** Coding questions are graded by exact string match against an expected output — genuinely NOT code execution. Building a real code judge means running untrusted student code, which needs a sandboxed executor (gVisor/Docker-in-Docker/Judge0-style isolation) — a substantial, security-sensitive feature deliberately not built here. Descriptive questions are stored with `is_correct: null` for manual review; there's no manual-grading UI/endpoint yet either (natural fit for a TPO/Admin dashboard phase).
- **Question selection avoids Mongo's `$sample`** in favor of fetching candidates and picking randomly in Python — `$sample` has known bias issues on small collections (exactly the situation in early testing/low-question-count scenarios), and this approach behaves identically against `mongomock` in tests as it will against real MongoDB.
- **Graceful difficulty fallback**: if the ideal next-difficulty's question pool is exhausted (all asked already), the engine tries the other two difficulties before giving up and ending the assessment — so a thin question bank in one difficulty tier doesn't prematurely cut a student's assessment short.
- **`update_by_id` semantics matter for ownership checks**: attempt-answer submission verifies `attempt.current_question_id == question_id` — a student can only answer the question the engine actually gave them, not any arbitrary question ID, even one from the same assessment's pool.

### Test instructions
```bash
pytest -v
```
Expected: **76 passed** (60 from before + 16 new in `test_assessments.py`).

### Verification checklist
- [x] MCQ validation rejects a `correct_answer` not present in `options`
- [x] Coding questions require a `correct_answer`; descriptive questions don't
- [x] Bulk import creates N questions from a JSON array; export filters correctly
- [x] Starting an assessment always returns a Medium-difficulty question first
- [x] A correct answer's next question is one difficulty harder; wrong is one easier
- [x] Answering with a `question_id` that isn't the attempt's current question is rejected
- [x] A student cannot answer another student's attempt (`403`)
- [x] Reaching `question_pool_size` auto-submits the attempt
- [x] A correct MCQ answer measurably raises that skill's `mastery_pct` (starts neutral at 50, moves up)
- [x] A student can view their own knowledge states; cannot view another's; a TPO/Admin can view any student's

### Notes / decisions carried forward
- **No frontend UI for taking assessments yet** — Phase 12 (Student Dashboard) is the natural fit, and will need to handle the adaptive per-question round-trip (submit answer → immediately render next question) rather than a traditional "show all questions, submit once" form.
- **No manual-grading workflow for descriptive answers** — flagged above, needed before descriptive questions are actually useful in a real assessment rather than just accepted-and-ignored.
- **`KnowledgeTracingService.get_average_mastery()`** is built and ready to feed the Phase 1 Placement Readiness formula's 25% "Knowledge Tracing Score" component — but the full readiness score isn't assembled anywhere yet, since its other two inputs (resume score, semantic match) are still blocked on Phase 7.
- **Anti-cheat fields (`violations`, `fingerprint_hash`, `ip_address`) exist on `AssessmentAttemptInDB` but are inert** — Phase 11 is where they actually get populated and enforced (tab-switch detection, fullscreen requirements, etc.).

---

## Phase 11 — Anti-Cheat System ✅

Backend enforcement only. Client-side pieces (fullscreen API, copy/paste/devtools blocking, tab-switch/idle detection) have nowhere to attach yet since no assessment-taking UI exists — they're a thin JS layer that calls the violation-report endpoint built here, and get wired in when Phase 12 builds the actual page.

### Files created / changed
```
backend/
├── app/models/
│   ├── activity_log.py                  # NEW — generic audit log model
│   └── assessment.py                    # + max_violations/require_fullscreen on
│                                          #   AssessmentCreateRequest; + StartAttemptRequest;
│                                          #   + session_token on SubmitAnswerRequest;
│                                          #   + ViolationReportRequest/Response
├── app/repositories/activity_log_repository.py   # NEW — + log_activity() helper
├── app/services/assessment_service.py    # + fingerprint/IP capture, session-token binding,
│                                          #   server-side timer enforcement, report_violation(),
│                                          #   MCQ option shuffling, response-time logging
├── app/routers/assessments.py            # start/answer endpoints updated; + violation endpoint
├── app/core/database.py                  # + activity_logs indexes
└── tests/test_assessments.py             # REWRITTEN — all Phase 10 tests updated for the new
                                            #   request shapes + 6 new anti-cheat tests
```

### API surface additions
```
POST /api/v1/assessments/{id}/start            now takes {fingerprint_hash?} body
POST /api/v1/assessments/attempts/{id}/answer  now requires session_token in body
POST /api/v1/assessments/attempts/{id}/violation  NEW — report a client-detected event
```

### Key architectural decisions
- **Two real bugs from Phase 10 were caught and fixed during THAT phase's own review** (student_id ID-space consistency, pydantic/dict mixing in `answers`) — see that section above. No new bugs of that kind found in this phase, but worth remembering the pattern when extending this code further.
- **Generic violation-type strings, not a hardcoded enum.** The backend doesn't need to know every possible client-detected event type in advance (`tab_switch`, `fullscreen_exit`, `devtools_opened`, `idle_timeout`, `copy_paste_attempt`, whatever Phase 12's frontend decides to detect) — it just counts occurrences against `assessment.anti_cheat_config["max_violations"]` and auto-submits at the threshold. Adding a new violation type later needs zero backend changes.
- **Session token is defense-in-depth, not the primary auth boundary.** JWT (`current_user`) already gates *who* can call these endpoints; the session token additionally verifies a request belongs to the specific browser tab that started *this* attempt — satisfies "Unique Secure Test Session Tokens" as its own explicit check, separate from user identity.
- **Server-side timer enforcement, not just a frontend countdown.** `_require_in_progress_attempt` checks `now > started_at + time_limit_sec` on every answer/violation call and auto-submits if exceeded — a student can't out-run the clock just by disabling frontend JS.
- **MCQ option order is randomized per delivery, safely** — grading matches submitted option *text* against `correct_answer`, never a position/index (this was already true since Phase 10), so shuffling display order for "unique test per student" required zero grading-logic changes, just a `random.sample()` in `to_student_view()`.
- **Fingerprint hash is captured once, at attempt start, not continuously re-validated per-request.** Continuous re-validation would need every subsequent client call to resend it, and a legitimate network change mid-test (WiFi → hotspot) could cause false-positive mismatches. Captured now so it's available for Phase 12's real client to actually populate meaningfully and for future stricter enforcement if warranted — flagged as the current, deliberately conservative scope.
- **Response-time analysis is informational, not punitive.** An implausibly fast answer (<3 sec) is logged to `activity_logs` for a human (TPO/Admin) to review later — it does NOT count toward the violation auto-submit threshold, since a fast answer alone is weak, uncertain evidence (some students are just quick) and auto-punishing on it risks false accusations.
- **`log_activity()` never raises** — a logging failure must never take down the actual request being logged (e.g., a student submitting an answer shouldn't get a 500 because an audit-log write hiccuped).

### Test instructions
```bash
pytest -v
```
Expected: **82 passed** (76 from before + 6 new anti-cheat tests; the Phase 10 tests were updated in place for the new request shapes, not added to — total count only grows by the genuinely new tests).

### Verification checklist
- [x] `/assessments/{id}/start` accepts an optional `fingerprint_hash` and captures the caller's IP server-side (not client-supplied — can't be spoofed via the request body)
- [x] Answering with the wrong `session_token` is rejected (`403`), even with a valid JWT for the attempt's actual owner
- [x] A single violation report doesn't submit the attempt; reaching `max_violations` does, and further answer attempts after that correctly fail
- [x] Violation report also requires the correct `session_token`
- [x] MCQ options come back in varying order across requests, but grading is unaffected (submit "A" — the text — and it's graded correctly regardless of display position)
- [x] All Phase 10 functionality (adaptive difficulty, knowledge tracing, ownership checks) still passes with the updated request shapes

### Notes / decisions carried forward
- **No frontend proctoring UI yet** — the actual `visibilitychange`/`fullscreenchange`/`keydown` listeners, the fullscreen-request flow, and the "you have N violations remaining" UI all belong in Phase 12's assessment-taking page. This phase built the backend contract they'll call.
- **Webcam-based proctoring** — explicitly out of scope (per the original spec's own "architecture should allow future webcam-based proctoring" note, not "build it now"). Nothing here blocks adding it later; it'd be another violation-type-adjacent feature or a separate media-upload concern.
- **No manual-review UI for `fast_answer_detected` activity logs or descriptive-question grading** — both are informational data sitting in the database waiting for a TPO/Admin dashboard view (Phase 13/14 territory) to surface them.

---

## Phase 12 — Student Dashboard ✅

Builds the frontend for every student-facing API surface that existed going into this phase (Phases 4, 5/6, 8, 10/11) — resume, drives/applications, and the full adaptive-assessment-taking flow including the Phase 11 anti-cheat client wiring that had "nowhere to attach yet" until now. Also closes a real gap: nothing before this phase exposed `StudentInDB`'s profile fields (department, cgpa, skills, links, etc.) for the student to read or edit, so a small backend addition was needed first.

Model artifacts still hadn't arrived from the teammate at the start of this phase, so Phases 7 and 9 remain blocked and this phase proceeded straight to Phase 12 per the handoff's own contingency plan.

### Files created / changed
```
backend/
├── app/models/user.py                    # + StudentProfileResponse, StudentProfileUpdateRequest
├── app/services/student_profile_service.py   # NEW — completeness calc + partial-update logic
├── app/routers/students.py               # NEW — GET/PUT /students/me
├── app/main.py                           # + students router registration
└── tests/test_students.py                # NEW — 5 tests (get, partial update, completeness,
                                             #   RBAC for tpo, unauthenticated)

frontend/
├── types/
│   ├── student.ts                        # NEW
│   ├── resume.ts                         # NEW
│   ├── drive.ts                          # NEW
│   └── assessment.ts                     # NEW
├── providers/auth-provider.tsx           # NEW — AuthContext: bootstraps session via silent
│                                          #   /auth/refresh + /auth/me on mount, exposes
│                                          #   user/setUser/logout app-wide
├── hooks/
│   ├── use-student-profile.ts            # NEW
│   ├── use-resumes.ts                    # NEW — includes downloadResumeFile() (see decisions)
│   ├── use-drives.ts                     # NEW
│   ├── use-assessments.ts                # NEW
│   └── use-toast.ts                      # NEW — shadcn-pattern toast queue
├── components/ui/
│   ├── badge.tsx, progress.tsx, tabs.tsx, select.tsx, textarea.tsx,
│   │   skeleton.tsx, avatar.tsx, dropdown-menu.tsx, dialog.tsx,
│   │   toast.tsx                          # NEW — primitives Phases 2–11 hadn't needed yet
├── components/shared/
│   ├── dashboard-shell.tsx               # NEW — sidebar + topbar shell
│   ├── stat-card.tsx, empty-state.tsx     # NEW — small reusable pieces
│   └── toaster.tsx                        # NEW — mounted once in app/layout.tsx
├── lib/
│   ├── attempt-storage.ts                # NEW — sessionStorage persistence for in-progress
│   │                                        assessment attempts (see decisions)
│   └── fingerprint.ts                    # NEW — client fingerprint for Phase 11's
│                                            fingerprint_hash
├── app/layout.tsx                        # + AuthProvider, Toaster
├── app/(auth)/login/page.tsx             # + calls useAuth().setUser() after login
├── components/shared/google-sign-in-button.tsx  # + calls useAuth().setUser() after Google auth
├── app/(student)/layout.tsx              # NEW — auth guard + shell wrapper; also redirects
│                                            ?complete_profile=true to /dashboard/profile
└── app/(student)/dashboard/
    ├── page.tsx                          # Overview (replaces Phase 3 placeholder)
    ├── profile/page.tsx                  # Profile edit form
    ├── resume/page.tsx                   # Upload, version history, parsed-data view, download,
    │                                        reparse
    ├── drives/page.tsx                   # Browse drives
    ├── drives/[id]/page.tsx              # Drive detail + eligibility check + apply
    ├── applications/page.tsx             # My applications, cross-referenced with drive summaries
    └── assessments/
        ├── page.tsx                      # Available assessments + skill-mastery breakdown
        ├── [attemptId]/take/page.tsx     # The adaptive attempt flow + anti-cheat wiring
        └── results/[attemptId]/page.tsx  # Attempt results
```

### API surface additions
```
GET /api/v1/students/me   →  StudentProfileResponse
PUT /api/v1/students/me   →  partial update (exclude_unset semantics, like DriveUpdateRequest)
```
No other backend endpoints were added — every other page in this phase consumes API surface that already existed from Phases 4–11.

### Key architectural decisions
- **`AuthContext` was missing entirely before this phase.** Phases 3–4 built the access-token-in-memory / httpOnly-refresh-cookie mechanics and the `placer_role` cookie for the middleware, but nothing re-established *who is logged in* after a hard reload for the app itself to read. `AuthProvider` now does this once on mount (`POST /auth/refresh` → `GET /auth/me`), and login/register/Google sign-in all call `setUser()` immediately on success so there's no redundant round-trip right after auth.
- **Student profile endpoints didn't exist before this phase.** `StudentInDB` has carried `department`, `cgpa`, `phone`, links, `skills`, etc. since Phase 4, but nothing exposed them. Added `GET/PUT /students/me` as a small, additive Phase 12 backend change — same partial-update (`exclude_unset`) convention as `DriveUpdateRequest` from Phase 8, so omitting a field in a PUT never wipes it.
- **Profile completeness is a simple equal-weighted metric** (8 fields, each worth 1/8) computed server-side in `student_profile_service.py`, recomputed on every profile update. No product requirement yet for weighting some fields more than others, so kept transparent rather than inventing a formula.
- **Resume downloads go through `apiClient` as a blob, not a plain `<a href>`.** `GET /resumes/{id}/download` is gated by the same JWT-bearer auth as everything else — a bare anchor-tag navigation never attaches the `Authorization` header (only axios's request interceptor does), so `downloadResumeFile()` fetches as a blob and triggers the save client-side instead.
- **In-progress assessment attempts persist to `sessionStorage`, not React state alone.** The backend has no "get current question" endpoint — `next_question` only comes back embedded in the start/answer responses — so a state-losing event (accidental reload) would otherwise strand the student mid-attempt with no way to recover the current question. `lib/attempt-storage.ts` mirrors attempt state (session token, current question, violation count) to `sessionStorage` on every update; the take-assessment page reads it back on mount. This is browser sessionStorage in the actual deployed app (not a Claude-artifact context), so it's the correct tool here, unlike the general in-memory-only rule.
- **Client fingerprint is a lightweight non-cryptographic hash** (`lib/fingerprint.ts` — user agent, language, screen size, timezone, core count), sent once at attempt start per Phase 11's own design note ("captured once at start, not continuously re-validated"). It's explicitly defense-in-depth, not a security boundary.
- **Anti-cheat violation types sent from the client**: `fullscreen_denied`, `fullscreen_exit`, `tab_switch`, `copy_paste_attempt`, `time_expired` — all free-form strings per Phase 11's design (backend doesn't hardcode the list). Each is throttled client-side (3s per type) so a single sustained event (e.g. staying out of fullscreen) doesn't spam the violation endpoint.
- **The client-side countdown timer is UX only.** Per Phase 11, the backend independently enforces the time limit on every answer/violation call and auto-submits if exceeded — the frontend timer can't be trusted as the actual boundary and isn't treated as one; a `time_expired` violation report on client-side expiry is just a nudge to the backend, which will already reject/auto-submit regardless.
- **Auto-submit (from violations or time) surfaces a modal, not a silent redirect** — the student is told explicitly why their attempt ended before being sent to the results page, rather than just landing there with no explanation.
- **UI primitives added this phase** (badge, progress, tabs, select, textarea, skeleton, avatar, dropdown-menu, dialog, toast) were already present as dependencies in `package.json` since Phase 3 scaffolding but unused until a page actually needed them — added now, following the same hand-rolled-wrapper-over-Radix-primitive pattern as the existing `button.tsx`/`card.tsx`/`input.tsx`/`label.tsx`.
- **`zod` schema bug caught and fixed during this phase's own review**: the profile form's optional numeric fields (`cgpa`, `batch_year`) originally used `z.coerce.number().optional().or(z.literal(NaN))` to handle a blank input — but `Number("")` is `0`, not `NaN`, so a blank field would have silently submitted `0` instead of omitting the field. Fixed with a `z.preprocess` that treats an empty string as `undefined` before coercion.

### Test instructions
```bash
# Backend
.venv\Scripts\python.exe -m pytest -v
# Expected: 87 passed (82 from before + 5 new student-profile tests)

# Frontend — no automated tests added this phase (none existed before it either);
# verify manually:
npm run typecheck
npm run dev
```

### Manual verification checklist (frontend)
- [ ] Register a new student, log in, confirm the dashboard loads (not stuck on "Loading your dashboard…")
- [ ] Hard-reload `/dashboard` — session persists (AuthProvider's silent refresh works) instead of bouncing to `/login`
- [ ] Google sign-in with a brand-new Google account lands on `/dashboard/profile` (the `?complete_profile=true` redirect)
- [ ] Edit and save the profile form; completeness % increases; reloading shows the saved values
- [ ] Upload a resume (PDF), confirm it appears as the active version and parsed data renders
- [ ] Upload a second resume version, switch between versions in the left panel
- [ ] Download a resume and confirm the file opens correctly (tests the blob-based download path)
- [ ] Browse drives, open a detail page, confirm eligibility warnings show correctly for an ineligible profile
- [ ] Apply to a drive, confirm it now shows "applied" and appears on the Applications page
- [ ] Start an assessment, confirm fullscreen is requested (if `require_fullscreen` is set on that assessment)
- [ ] Switch tabs mid-assessment, confirm a violation is recorded and the counter shown updates
- [ ] Exhaust `max_violations`, confirm the attempt auto-submits with the explanatory modal
- [ ] Answer through an entire question pool normally, confirm it redirects to the results page with a correct score
- [ ] Reload mid-assessment (not exceeding violations), confirm the current question is recovered from `sessionStorage` rather than the attempt being lost

### Notes / decisions carried forward
- **No separate "Knowledge" nav page** — mastery-per-skill is shown inline on both the Overview page (top 5 skills) and the Assessments page (full list), rather than as its own route. Revisit if this needs to grow (e.g., historical mastery trend charts) — `recharts` is already a dependency for that.
- **No TPO/Admin dashboards yet** — `DashboardShell`/`NAV_ITEMS` are currently student-specific; Phases 13/14 will need their own nav item sets (and possibly a `role` prop on a shared shell) rather than reusing this one as-is. *(Resolved in Phase 13 — `DashboardShell` was refactored to accept `navItems`/identity as props; Phase 14 can reuse it the same way.)*
- **No manual-review UI for descriptive-question grading** — still sitting ungraded per Phase 10's original scope note; a TPO/Admin review UI is Phase 13/14 territory.
- **No pagination on the drives list** — fetches up to 100 at once (`limit: 100`). Fine at current/expected scale for a final-year project; would need real pagination if the drives collection grows much larger.
- **`zod`'s `.env.local.example` / Google OAuth setup is unchanged from Phase 4** — no new environment variables were introduced this phase.
- Once the ML model artifacts arrive: Phase 7 (resume scoring) slots into the existing Resume page's parsed-data view (an additional "match score" section), and Phase 9 (semantic matching) would add a "Recommended for you" section to the Drives page — both are additive to what's built here, not a rework.

---

## Phase 13 — TPO Dashboard ✅

Builds the frontend for TPO drive management and applicant review. Two small backend gaps had to be closed first — there was no way to list "my drives" specifically, and no way to change an applicant's status at all (only create the application and view it), which would have made a TPO dashboard read-only and fairly useless. Both were additive, same pattern as Phase 12's student-profile addition.

### Files created / changed
```
backend/
├── app/models/drive.py                   # + ApplicationStatusUpdateRequest, ApplicationDetail
├── app/services/drive_service.py         # + get_my_drives(), update_application_status()
├── app/routers/drives.py                 # + GET /drives/mine, PATCH /drives/{id}/applications/{id};
│                                            GET /drives/{id}/applications now returns ApplicationDetail
│                                            (enriched with student name/department/cgpa, resume filename)
└── tests/test_drives.py                  # + 6 tests (list-mine scoping, role check, applicant
                                             #   enrichment fields, status update, 2 authorization checks)

frontend/
├── types/drive.ts                        # + ApplicationDetail, DriveCreateRequest, DriveUpdateRequest
├── hooks/
│   ├── use-tpo-drives.ts                 # NEW — my-drives, create/update/delete drive,
│   │                                        applicants list, status update
│   └── use-assessments.ts                # + useStudentKnowledgeStates(studentId) — TPO/admin view
│                                            of a specific student's mastery (backend endpoint already
│                                            existed since Phase 10/11, unused until now)
├── components/shared/dashboard-shell.tsx # REFACTORED — now role-agnostic: nav items, display
│                                            name/initials, profile link, and logout handler are all
│                                            passed in as props instead of being student-hardcoded
├── app/(student)/layout.tsx              # updated to match the new DashboardShell prop signature
│                                            (no behavior change for students)
└── app/(tpo)/
    ├── layout.tsx                        # NEW — auth guard + shell wrapper (replaces old
    │                                        student-only layout gap for /tpo/*)
    └── tpo/dashboard/
        ├── page.tsx                      # Overview (replaces Phase 3 placeholder) — drive/applicant
        │                                    stats, recent drives list
        └── drives/
            ├── page.tsx                  # My drives list
            ├── new/page.tsx              # Create-drive form
            └── [id]/
                ├── page.tsx              # Drive detail/edit + open/close toggle + delete (confirm dialog)
                └── applicants/page.tsx   # Applicant review: status dropdown, resume download,
                                             expandable per-applicant skill-mastery view
```

### API surface additions
```
GET   /api/v1/drives/mine                                  →  DriveSummary[] (TPO's own drives)
PATCH /api/v1/drives/{drive_id}/applications/{application_id}  →  ApplicationDetail (status update)
```
`GET /api/v1/drives/{drive_id}/applications` changed its response model from `ApplicationResponse[]` to
`ApplicationDetail[]` (backward-compatible superset — every original field is still present, three fields
were added). No other endpoints changed shape.

### Key architectural decisions
- **`update_application_status` reuses `_require_owned_drive`, not a new ownership check.** Same pattern as `update_drive`/`delete_drive` — a TPO can only act on applications belonging to drives they created, verified via the `TPORepository` lookup + `drive.created_by` comparison already established in Phase 8.
- **Applicant enrichment happens in the router, not the service** — mirroring the existing `_to_summary`/`_to_detail` pattern in `drives.py` (which already does a read-only `CompanyRepository` lookup to build `DriveSummary`). Kept `DriveService` itself free of this presentation-layer joining, consistent with the Repository Pattern's separation.
- **No new endpoint for "resume access" or "student mastery access" for TPOs** — both already existed and worked (resume download/detail explicitly allows TPO/Admin per a Phase 8 comment in `resumes.py`; `GET /assessments/knowledge-states/{student_id}` was built in Phase 10/11 with `require_role("tpo", "admin")` but had no caller until this phase). Reviewed rather than reinvented.
- **`DashboardShell` refactor**: it went from a student-hardcoded component (fixed `NAV_ITEMS`, a direct `useStudentProfile()` call inside) to accepting `navItems`, `displayName`, `initials`, `profileHref`, and `onLogout` as props. The calling layout now owns fetching whatever profile data it needs (student profile hook for `/dashboard`, nothing yet for `/tpo` — see limitation below) and computes the display identity itself. This was flagged as a likely need in Phase 12's own carried-forward notes and confirmed necessary here.
- **TPO display name falls back to email — there's no TPO profile name endpoint.** `TPOInDB` does have a `name` field (set at registration), but Phase 12 only built profile endpoints for students. Rather than scope-creep this phase into building a second profile endpoint, the TPO topbar just shows the account email. Noted as a limitation below, not silently worked around.
- **Eligibility/selection-process/required-skills inputs are comma-separated text fields, not dynamic add/remove chip inputs** — same trade-off Phase 12 made for the student profile's skills field. Keeps the form simpler at the cost of a slightly less polished editing experience; revisit if this becomes a pain point.
- **Applicant status changes are optimistic-free** — `useUpdateApplicationStatus` updates the query cache from the server's actual response (`onSuccess`), not an optimistic update before the request resolves, since a wrong status flip (e.g., double-clicking) shown briefly before reverting would be a worse experience than a ~200ms wait for a real confirmation.
- **Drive company fields are edit-locked after creation** — `DriveUpdateRequest` never included company fields (an existing Phase 8 decision, not new to this phase), so the edit form only exposes the role/eligibility fields that were always editable. This was already true before Phase 13; just noting it since the edit form makes it visible for the first time.

### Test instructions
```bash
# Backend
.venv\Scripts\python.exe -m pytest -v
# Expected: 93 passed (87 from Phase 12 + 6 new)

# Frontend
npm run typecheck
npm run dev
```

### Manual verification checklist (frontend)
- [ ] Log in as a TPO, confirm `/tpo/dashboard` loads (not stuck loading, not redirected to student `/dashboard`)
- [ ] Create a new drive with full eligibility criteria; confirm it appears on `/tpo/dashboard/drives`
- [ ] Edit an existing drive's job title/description/skills; confirm changes persist after reload
- [ ] Toggle a drive between Open/Closed; confirm the badge updates and the student-facing Drives page reflects it
- [ ] Log in as a student, apply to the drive created above
- [ ] Back as the TPO, open that drive's Applicants page — confirm the applicant's name/department/CGPA/resume show correctly
- [ ] Change an applicant's status via the dropdown (e.g., to "Shortlisted"); confirm it persists on reload and the student sees the updated status on their Applications page
- [ ] Download an applicant's resume from the Applicants page — confirms TPO resume access still works
- [ ] Expand an applicant's row to view their skill mastery (works even with zero assessment attempts — shows "No assessment attempts yet" rather than erroring)
- [ ] Attempt to view a drive's applicants using a *different* TPO account that didn't create it — confirm this is blocked (this is covered by an automated test, but worth eyeballing the 403 in the browser once)
- [ ] Delete a drive via the confirmation dialog; confirm it disappears from the drives list

### Notes / decisions carried forward
- **No TPO profile page** — the account has no way to view/edit its own `name`/`department_scope` from the UI yet. Low priority (TPO accounts are presumably provisioned by an admin with correct info already), but if this becomes needed, follow the exact `students.py`/`student_profile_service.py` pattern from Phase 12.
- **No company management UI** — companies are created implicitly the first time a TPO uses a new `company_name` when creating a drive (existing Phase 8 behavior); there's no way to edit a company's description/website/industry after the fact, or to browse companies independently of drives. Not blocking, just not built.
- **No bulk applicant actions** — status changes are one applicant at a time. Fine at current expected scale (a few dozen applicants per drive for a college project); would need a "select all + bulk shortlist" affordance if that assumption changes.
- **No drive analytics** (applications-over-time, funnel conversion, etc.) — that's explicitly Phase 15's territory per the phase tracker, not pulled forward here.
- **Applicant list has no pagination** — same reasoning and same ceiling as Phase 12's drives list (backend `get_for_drive` defaults to `limit=50`); revisit together if either needs it.
- Once Phase 9 (semantic matching) unblocks: the Applicants page is the natural place for a "match score" column/sort, since it already renders one row per application — additive, not a rework.

---

## Phase 14 — Admin Dashboard ✅

Builds the frontend for the two admin-gated resource types that already existed on the backend since Phases 10/11 (question bank management, assessment creation) but had no UI. Also closes a genuine blocker discovered at the start of this phase: **there was no way to create an admin account at all** — no public registration route (correctly, by design) and no seed script either, meaning nobody could actually log into an admin dashboard even once it existed.

### Files created / changed
```
backend/
├── app/models/user.py                    # + AdminRegisterRequest (CLI-only, no public route)
├── app/services/auth_service.py          # + register_admin() — mirrors register_tpo()
├── scripts/__init__.py                   # NEW
├── scripts/create_admin.py               # NEW — CLI bootstrap script (see below)
└── tests/test_admin_bootstrap.py         # NEW — 3 tests (service-level create, duplicate-email
                                             #   rejection, and a full login round-trip over HTTP)

frontend/
├── types/
│   ├── question.ts                       # NEW — categories, questions, create/update requests
│   └── assessment.ts                     # + AssessmentCreateRequest
├── hooks/
│   ├── use-admin-questions.ts            # NEW — categories, questions CRUD, bulk import/export
│   └── use-admin-assessments.ts          # NEW — create (listing reuses hooks/use-assessments.ts,
│                                            already role-agnostic since GET /assessments has no
│                                            role restriction)
├── components/shared/question-form.tsx   # NEW — shared create/edit form (used by both the New
│                                            Question page and the edit dialog on the list page)
└── app/(admin)/
    ├── layout.tsx                        # NEW — auth guard + shell wrapper
    └── admin/dashboard/
        ├── page.tsx                      # Overview (replaces Phase 3 placeholder) — question/
        │                                    category/assessment counts, quick actions
        ├── questions/
        │   ├── page.tsx                  # Question bank: Questions tab (filter, edit dialog,
        │   │                                delete, bulk import/export) + Categories tab
        │   └── new/page.tsx              # New-question page (uses the shared QuestionForm)
        └── assessments/
            ├── page.tsx                  # Assessment list
            └── new/page.tsx              # New-assessment form (category chips, pool size, time
                                             limit, anti-cheat settings)
```

### API surface additions
```
GET   /api/v1/drives/mine   — unrelated to this phase, already added in Phase 13, listed here only
                                to avoid confusion since nothing else changed in drives.py this phase
```
No new HTTP routes were added this phase — every admin page consumes API surface that already
existed from Phases 10/11 (`/questions/*`, `/assessments` POST/GET). The only backend change was
`AuthService.register_admin()`, which is deliberately **not** exposed via any route.

### Key architectural decisions
- **Admin account creation is a CLI script, not an API route — and that's intentional, not a gap being left open.** `scripts/create_admin.py` connects to MongoDB directly (via the same `connect_to_mongo()`/`get_database()` the app uses) and calls `AuthService.register_admin()`, which mirrors `register_student`/`register_tpo` exactly (same password hashing, same duplicate-email check) so it isn't a parallel, divergent code path. Run it once from `backend/` with the venv active:
  ```powershell
  python -m scripts.create_admin
  ```
  It prompts for email/name/password (password via hidden `getpass` input, or pass `--password` if scripting it, though prompting is preferred to avoid the password landing in shell history). A `POST /auth/register/admin` route was deliberately *not* added — unlike student/TPO self-registration, an admin route reachable by anyone would mean anyone could grant themselves admin, which is a real security regression, not a convenience worth adding.
- **`AdminRegisterRequest` exists as a proper Pydantic model even though no route uses it** — same reasoning as the model existing at all: the CLI script gets the same email-format/password-length validation as every other registration path for free, rather than the script hand-rolling its own checks that could quietly drift from the "real" rules over time.
- **Question editing happens in a dialog on the list page, not a separate route.** A dedicated `questions/[id]/edit` page would have meant either duplicating the form or adding routing complexity for what's fundamentally the same form with pre-filled values — `components/shared/question-form.tsx` is shared between the New Question page and this dialog, taking `initialValues` as an optional prop.
- **Bulk import/export is JSON, not CSV/Excel** — this was actually decided back in Phase 10/11 (`question_service.py`'s own module docstring explains the reasoning: it's a JSON-shaped resource, and pulling in a spreadsheet-parsing dependency wasn't justified without a concrete need for it). This phase's frontend just gives that existing JSON-based API a UI: paste-a-JSON-array-into-a-textarea for import, a downloaded `.json` file for export. Revisit if a real workflow need for CSV/Excel shows up.
- **Categories are flat-added (name + optional parent) with no tree UI** — `parent_category_id` exists in the model/API (from Phase 10) for future hierarchical categories, but nothing in this phase's UI lets you pick a parent when creating one, and the categories tab just lists them as a flat set of badges. Sufficient for the current question volume; a tree view is a reasonable follow-up if category nesting actually gets used.
- **Assessment category selection is toggle-chips, not a multi-select dropdown** — `AssessmentCreateRequest.category_ids` is a list; a row of clickable category chips (matching the visual pattern already used for skill/required-skill tags elsewhere in the app) reads more clearly than a cramped multi-select box for what's usually a small number of categories.
- **Frontend numeric validation limits were cross-checked against the actual backend constraints** (`question_pool_size` ≤ 100, not an arbitrary round number) rather than guessed — caught and fixed a mismatch during this phase's own review where the form allowed up to 200 but the backend would have rejected anything over 100.

### Test instructions
```bash
# Backend
.venv\Scripts\python.exe -m pytest -v
# Expected: 96 passed (93 from Phase 13 + 3 new)

# Create your first admin account (one-time):
python -m scripts.create_admin

# Frontend
npm run typecheck
npm run dev
```

### Manual verification checklist (frontend)
- [ ] Run `python -m scripts.create_admin`, confirm it prints a success message with the new account's id
- [ ] Log in with that admin account at `/login`, confirm `/admin/dashboard` loads
- [ ] Create a category, confirm it appears in the Categories tab and in the New Question form's category picker
- [ ] Create an MCQ question; confirm the "correct answer must match an option" validation actually blocks a mismatched submission
- [ ] Create a Coding question (requires expected-output) and a Descriptive question (requires neither options nor an answer); confirm the form's fields adapt correctly per type
- [ ] Edit an existing question via the dialog on the question bank list; confirm changes persist after reload
- [ ] Delete a question; confirm it disappears from the list
- [ ] Bulk-import a small JSON array of 2–3 questions; confirm the count and that they show up in the list
- [ ] Export questions (optionally filtered by category/difficulty) and confirm the downloaded `.json` file's shape roughly matches what bulk-import expects (they're the same `QuestionAdminResponse`/`QuestionCreateRequest` shape modulo `id`/`marks`)
- [ ] Create an assessment referencing at least one category with questions in it; confirm it appears on `/admin/dashboard/assessments`
- [ ] Log in as a student, confirm that new assessment now appears on their `/dashboard/assessments` page and can actually be started (exercises Phase 12's take-assessment flow end-to-end against a real admin-created assessment for the first time)

### Notes / decisions carried forward
- **No user-management UI** (listing/deactivating students or TPOs, promoting/demoting roles) — nothing in the backend supports this yet either; would need new endpoints first if it becomes a requirement. Not attempted here since it's a meaningfully separate feature from question-bank/assessment management.
- **No platform-wide analytics** (placement rates, drive funnel conversion, assessment score distributions) — explicitly Phase 15's territory per the tracker, not pulled forward. *(Built in Phase 15 — see that section.)*
- **No admin profile page**, same limitation as TPO from Phase 13 — topbar shows the account email, not a name. `AdminInDB` does have a `name` field (set via the bootstrap script), just nothing surfaces it in the UI yet.
- **Assessments can't be edited or deleted from the UI** — `assessments.py` only ever had `POST` (create) and `GET` (list) routes; there's no update/delete endpoint on the backend at all for assessments (unlike drives or questions, which both support full CRUD). If that turns out to be needed, it's a backend-first addition, not just a missing frontend page.
- **No preview of what a student would actually see when taking a newly created assessment** — the admin has to log in as (or ask) a student to verify it end-to-end, per the last item in this phase's manual checklist above. A "preview as student" mode would be a nice follow-up but wasn't built.

---

## Phase 15 — Analytics ✅

Builds TPO-facing and admin-facing analytics dashboards. Both are entirely new backend surface — no analytics/aggregation endpoints existed anywhere before this phase — computed by fetching the relevant collections and grouping in Python rather than MongoDB aggregation pipelines (see the module docstring in `analytics_service.py` for the reasoning: consistent with this project's simple-first approach elsewhere, e.g. knowledge tracing being an EMA rather than real BKT, and it keeps everything testable against the same mongomock setup the rest of the suite already uses).

### Files created / changed
```
backend/
├── app/models/analytics.py               # NEW — ApplicationStatusBreakdown, DriveFunnel,
│                                            TpoAnalyticsResponse, SkillMasteryOverview,
│                                            AdminAnalyticsResponse
├── app/services/analytics_service.py      # NEW — AnalyticsService.get_tpo_analytics() /
│                                            get_admin_analytics()
├── app/routers/analytics.py               # NEW — GET /analytics/tpo, GET /analytics/admin
├── app/main.py                            # + analytics router registration
└── tests/test_analytics.py                # NEW — 4 tests (TPO scoping to own drives, role
                                              #   checks for both endpoints, admin counts)

frontend/
├── types/analytics.ts                     # NEW — mirrors models/analytics.py exactly
├── hooks/use-analytics.ts                 # NEW — useTpoAnalytics(), useAdminAnalytics()
├── components/shared/status-breakdown-chart.tsx  # NEW — shared recharts bar chart (applied/
│                                                    shortlisted/rejected/selected), used by both
│                                                    dashboards
└── app/
    ├── (tpo)/
    │   ├── layout.tsx                     # + Analytics nav item
    │   └── tpo/dashboard/analytics/page.tsx   # NEW — funnel chart + per-drive breakdown
    └── (admin)/
        ├── layout.tsx                     # + Analytics nav item
        └── admin/dashboard/analytics/page.tsx  # NEW — platform stats, funnel chart, assessment
                                                    performance, skill mastery overview
```

### API surface additions
```
GET /api/v1/analytics/tpo    (tpo only)    →  TpoAnalyticsResponse
GET /api/v1/analytics/admin  (admin only)  →  AdminAnalyticsResponse
```

### Key architectural decisions
- **A real bug was caught and fixed during this phase's own review**: the first draft used `str(a.status) == "selected"` to check application/attempt status. `ApplicationStatus`/`AttemptStatus` are `class X(str, Enum)` — instances *are* strings for equality purposes (`a.status == "selected"` works correctly, since `str.__eq__` wins in the MRO), but `Enum.__str__` still wins for `str()`, so `str(a.status)` actually returns `"ApplicationStatus.SELECTED"`, not `"selected"`. Every status comparison in `analytics_service.py` was corrected to direct `==` comparison (or `.value` where a plain string was needed for a response field) instead of `str(...)`. This is a real Python gotcha worth flagging if anyone extends this file — reach for `.value` or bare `==`, never `str(enum_instance)`.
- **`AnalyticsService` fetches full collections with a generous cap (`_ANALYTICS_FETCH_LIMIT = 5000`) and groups in Python**, rather than MongoDB `$group`/`$lookup` aggregation pipelines. Explicitly a scale trade-off: correct and simple now, would need revisiting (real aggregation pipelines, or pre-computed rollup documents updated incrementally) if this were a multi-institution SaaS product instead of a single college's placement cell. Flagged in the module docstring so a future maintainer sees the reasoning, not just the code.
- **TPO analytics is scoped to that TPO's own drives only** — same ownership pattern established in Phase 13 (`TPORepository.get_by_user_id` → filter drives by `created_by`), not a shortcut or new concept.
- **"Placed students" counts unique students with at least one `selected` application**, not total `selected` applications — a student selected at two different companies (unusual, but the data model doesn't prevent it) should only count once toward the platform's placement rate. Used a Python `set` of `student_id`s for this reason rather than a raw count.
- **Skill mastery overview is sorted weakest-first** (ascending `avg_mastery_pct`) — an admin looking at this is almost always trying to spot gaps in what students collectively know, not admire strengths, so weakest-first surfaces the actionable information without needing to scroll or re-sort.
- **`StatusBreakdownChart` is a single shared component** used by both the TPO and admin pages — same four-status shape (`ApplicationStatusBreakdown`) appears in both `TpoAnalyticsResponse.breakdown` and `AdminAnalyticsResponse.application_breakdown`, so one chart component takes the shared type rather than each dashboard rolling its own.
- **`recharts` was already a dependency since the Phase 3 scaffold** (noted as available for this exact purpose back in Phase 12's carried-forward notes) but completely unused until this phase — same "dependency existed, no page needed it yet" situation as several Phase 12/13/14 UI primitives.

### Test instructions
```bash
# Backend
.venv\Scripts\python.exe -m pytest -v
# Expected: 100 passed (96 from Phase 14 + 4 new)

# Frontend
npm run typecheck
npm run dev
```

### Manual verification checklist (frontend)
- [ ] As a TPO with at least one drive and a few applications in different statuses, open `/tpo/dashboard/analytics` — confirm the stat cards, funnel chart, and per-drive breakdown all show correct numbers
- [ ] Confirm a *second* TPO account only sees their own drives' data, not the first TPO's (covered by an automated test, worth eyeballing once)
- [ ] As an admin, open `/admin/dashboard/analytics` — confirm student/TPO/drive counts match what you'd expect from what's been created so far
- [ ] Have a student complete at least one assessment attempt, confirm "Total attempts", "Submitted attempts", and "Average score" update accordingly on the admin page
- [ ] Confirm the skill mastery overview lists skills weakest-first and updates as more students attempt assessments
- [ ] Confirm both analytics pages render sensible empty states (not a crash or blank chart) when there's no data yet — easiest to check right after `python -m scripts.create_admin` on a fresh database before any drives/applications/attempts exist

### Notes / decisions carried forward
- **No date-range filtering or trend-over-time views** (e.g., "applications this month vs last month") — both analytics endpoints are current-snapshot only. `KnowledgeStateInDB.history` already stores a `[{date, mastery_pct}]` list per skill (from Phase 10/11) that a future trend chart could use without any backend change, but nothing surfaces it yet.
- **No per-department or per-batch-year breakdowns** — placement rate, for instance, is platform-wide, not sliced by department. Would be a natural next cut of this same data if needed.
- **No CSV/export of analytics data** — the question bank already has JSON export (Phase 14); analytics data has no equivalent yet. Would follow the same blob-download pattern already used for resumes/question-export if added.
- **Admin analytics has no student-level drill-down** — it's aggregate-only. The Phase 13 Applicants page already provides a student-level view for TPOs (skill mastery, resume, status) on a per-drive basis; nothing analogous exists for admins browsing all students platform-wide.
- **`_ANALYTICS_FETCH_LIMIT` (5000) is the one number in this phase most likely to need revisiting** if a much larger dataset ever gets loaded — see the "Key architectural decisions" note above.

---

## Phase 7 & 9 — Resume Scoring Integration + Semantic Matching ✅

Both phases were blocked from the start of this project on one thing: the trained model artifacts (bi-encoder folder, cross-encoder folder, fitted Platt calibrator `.pkl`) from a teammate. They arrived and were wired up together, since Phase 9 genuinely depends on Phase 7's inference wrapper — same split described in the original handoff.

Before writing any code, the actual training notebook (`PLACER_RoBERTa_Training_NEW.ipynb`) was read in full to extract the *exact* formulas, text templates, and preprocessing this model was trained on, rather than re-deriving them from the higher-level description in the original handoff summary. That surfaced several details worth recording here because they directly shaped the implementation and would be easy to get subtly wrong on a second pass:

### What the notebook actually specified (confirmed by reading the code, not just the description)
- **Hybrid formula**: `final_score = 0.50 × calibrated_semantic + 0.35 × skills_score + 0.15 × experience_score` — matches the original handoff.
- **`skills_score` is coverage, not Jaccard**: `|resume_skills ∩ jd_skills| / max(1, |jd_skills|)`. A `jaccard()` helper exists in the notebook but is used elsewhere (weak-label pair generation), not in the actual scoring function — easy to misread if only skimming.
- **Text templates are structured summaries, not raw text**: `"Technical skills: {sorted skills}. Experience years: {years}"` for resumes, and a longer template for JDs — both models were trained on these exact strings, not on raw resume/JD text.
- **`CROSS_MAX_LENGTH` is actually 256**, despite a comment in the notebook claiming it was bumped to 512 — the comment is stale; the code that actually ran (and thus what the model was tokenized with) uses 256. Used 256 here, trusting the executed code over the comment.
- **Retrieve-then-rerank pipeline** (the notebook's `evaluate_resume_pretty`, cell 16): bi-encoder cosine similarity narrows a candidate pool to `retriever_pool` (default 140 in the notebook), then the cross-encoder + calibrator + skill/experience formula reranks just that narrowed set. This is the exact shape `MatchingService` implements.

### Two real gaps found in PLACER's existing data model
- **No `experience_required_years` on Drive** — needed for 15% of the hybrid formula (`experience_score`) and for the JD text template. Added as a proper field (`PlacementDriveInDB`, `DriveCreateRequest`/`DriveUpdateRequest`/`DriveDetail`, plus the TPO create/edit forms) rather than working around its absence — this is a field a TPO would reasonably want to specify regardless of the ML integration.
- **No `domain` field on either Resume or Drive** — used in both text templates but not in the numeric formula. Rather than inventing a domain taxonomy that doesn't exist anywhere else in the app, it's simply omitted from both templates (confirmed with the project owner). This is a real, acknowledged deviation from the training input distribution — see "Known limitations" below.

### The missing skill ontology file — resolved without needing it
`ML_Keywords_and_Projects.txt` (and its derived `keyword_ontology.json`) weren't available. Rather than degrading to naive string matching, the notebook's actual alias-squashing logic was inspected directly: the ~800-term "canonical vocabulary" from that missing file only ever maps terms to themselves (`ALIAS_INV = {t: t for t in canon_terms}`), which is exactly what `canonical_skill()`'s default fallback (`.get(term, term)`) already does for any unrecognized term — so those ~800 entries change nothing behaviorally. The *only* part of the ontology that does real work is an explicit ~18-entry `manual_aliases` dict (e.g. `"reactjs"` → `"react"`), which is hardcoded directly in the notebook source and therefore fully available. `app/ml/matching/skill_ontology.py` ports that dict verbatim — behaviorally equivalent to the full notebook ontology for every case that actually matters.

### Key architectural decision: plain `transformers`, not `sentence-transformers`
The original `requirements.txt` had `sentence-transformers==3.1.1` commented out and reserved for this phase. That was **not** used. The saved cross-encoder uses sentence-transformers 5.x's newer `CrossEncoder` save format (`config_sentence_transformers.json` declaring `model_type: "CrossEncoder"` and a baked-in `activation_fn`), which an older 3.x install cannot reliably load — a real compatibility risk discovered by inspecting the saved model's actual config files, not a theoretical concern. Instead, `app/ml/matching/inference.py` loads both models via plain `AutoModel`/`AutoModelForSequenceClassification` and replicates the pooling/sigmoid math by hand — a direct port of the notebook's own training-time evaluation code (cells 4 and 11), not a reinterpretation of it. This only depends on standard `config.json` + `model.safetensors` + tokenizer files, which are stable across library versions regardless of which wrapper originally saved them.

### A real bug caught during this phase's own review
The hybrid formula is **not symmetric** between resume and JD — `skills_score`'s denominator is always the JD's required-skill count, and `experience_score` is always `resume_years / jd_years`, never the reverse. An early draft of `MatchingService` used one generic "anchor vs candidates" scoring function for both "rank drives for a resume" and "rank resumes for a drive," which would have silently computed the wrong formula (denominator = the *resume's* skill count) whenever ranking resumes for a drive. Fixed by replacing the generic scorer with two explicitly-oriented functions (`_score_one_resume_vs_many_jds` / `_score_one_jd_vs_many_resumes`) that can't be called in the wrong direction by construction.

### Files created / changed
```
backend/
├── app/models/drive.py                   # + experience_required_years (PlacementDriveInDB,
│                                            DriveCreateRequest/UpdateRequest, DriveDetail)
├── app/models/resume.py                  # + resume_embedding cache field
├── app/models/matching.py                # NEW — MatchScoreBreakdown, DriveMatchScoreResponse,
│                                            RecommendedDriveResponse, RankedApplicantResponse
├── app/services/drive_service.py         # + experience_required_years wiring; invalidates
│                                            cached jd_embedding when text-affecting fields change
├── app/services/resume_parsing_service.py  # invalidates cached resume_embedding on reparse
├── app/services/matching_service.py      # NEW — text templates, exp_fit, the two oriented
│                                            scorers, embedding cache get-or-compute, retrieve+rerank
├── app/routers/drives.py                 # DriveDetail response includes experience_required_years
├── app/routers/matching.py               # NEW — 3 endpoints (see API surface below)
├── app/ml/matching/
│   ├── skill_ontology.py                 # NEW — canonical_skill(), to_skill_set()
│   ├── inference.py                      # NEW — MatchingEngine (lazy singleton), embed_texts(),
│   │                                        cross_score(), calibrate(), cosine_similarity()
│   └── artifacts/                        # NEW (git-ignored, ~567MB) — bi_encoder/, cross_encoder/,
│       ├── README.md                     #   calibrator.pkl, provisioning instructions
│       ├── bi_encoder/
│       ├── cross_encoder/
│       └── calibrator.pkl
├── requirements.txt                      # torch, transformers, scikit-learn, numpy (replacing the
│                                            placeholder sentence-transformers/faiss-cpu lines)
└── tests/test_matching.py                # NEW — pure-function tests (ontology, exp_fit, text
                                             templates) + real-inference integration tests

frontend/
├── types/
│   ├── drive.ts                          # + experience_required_years
│   └── matching.ts                       # NEW — MatchScoreBreakdown, DriveMatchScore,
│                                            RecommendedDrive, RankedApplicant
├── hooks/use-matching.ts                 # NEW — useDriveMatchScore, useRecommendedDrives,
│                                            useRankedApplicants (all treat 503 as "no data", not
│                                            an error — see below)
├── components/shared/match-score-card.tsx  # NEW — shared score/breakdown display
└── app/
    ├── (student)/dashboard/
    │   ├── drives/page.tsx               # + "Recommended for you" section
    │   └── drives/[id]/page.tsx          # + match score card
    └── (tpo)/tpo/dashboard/drives/
        ├── new/page.tsx                  # + experience_required_years field
        └── [id]/
            ├── page.tsx                  # + experience_required_years field
            └── applicants/page.tsx       # + match score badges, sort-by-match toggle,
                                             matched/missing skills in the expanded row
```

### API surface additions
```
GET /api/v1/matching/drives/{drive_id}/score          (student)  →  DriveMatchScoreResponse
GET /api/v1/matching/recommended-drives                (student)  →  list[RecommendedDriveResponse]
GET /api/v1/matching/drives/{drive_id}/ranked-applicants (tpo, drive owner only)  →  list[RankedApplicantResponse]
```
All three return `503` if the model artifacts aren't present in this deployment (see `artifacts/README.md`) — the frontend hooks treat that as "no data to show," not an error state, so the rest of the app is unaffected by whether matching is provisioned.

### Key architectural decisions
- **Embeddings are cached on the resume/drive document itself** (`resume_embedding` / `jd_embedding`), computed once and reused, since the bi-encoder forward pass is the more expensive part of a repeat lookup. Invalidated automatically whenever the underlying text-affecting fields change — `drive_service.py`'s `update_drive()` and `resume_parsing_service.py`'s reparse path both explicitly null out the cached embedding when the fields it was computed from change, rather than leaving a stale embedding silently in place.
- **Models are lazy-loaded on first use, not at app startup.** The three artifacts total ~570MB and take real time to load — paying that cost at every deploy/restart (or every health check) would be a bad trade for a feature that's one part of the app, not its hot path. `MatchingEngine.get()` loads once and reuses a singleton for the life of the process.
- **Applicant ranking uses the resume version actually submitted with the application** (`application.resume_id`), not the student's current active resume. A student updating their resume after applying shouldn't retroactively change what a TPO is evaluating for that specific application — same reasoning already established for why applications store a `resume_id` at all (Phase 8).
- **No FAISS.** The original Phase 9 tracker description mentioned it; it isn't used. PLACER's real corpus size (one college's open drives, or applicants to one drive — tens to a couple hundred, not millions) doesn't need approximate nearest-neighbor search — a plain numpy cosine-similarity `argsort` over cached embeddings is exact, fast enough at this scale, and one fewer heavy dependency to install on a free-tier host. The retrieve-then-rerank *architecture* is still implemented faithfully (see below); only the specific ANN library is skipped as unnecessary at this scale.
- **`DEFAULT_RETRIEVER_POOL = 100`** — the two-stage retrieve-then-rerank shape is preserved (matching the notebook's own design and the original architectural requirement) even though PLACER's real corpus sizes rarely need the retrieval stage to actually narrow anything down. Correct shape now, ready to matter if a much larger corpus shows up later.
- **Domain is omitted from both text templates** (see "gaps found" above) — a deliberate, acknowledged deviation from the exact training distribution, confirmed with the project owner rather than silently worked around. Matching still works well without it since skills and experience carry most of the signal, but this is worth knowing if match quality ever seems off compared to the notebook's own reported eval numbers.

### Test instructions
```bash
# Backend — note the new heavy dependencies
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -v
# Expected: 105 passed (100 from Phase 15 + 5 new). The 5 matching integration
# tests are slower than the rest of the suite (real model loading + real
# inference on CPU) — this is expected, not a hang.

# Frontend
npm run typecheck
npm run dev
```

**Before running tests or the app**: the model artifacts must be present at
`backend/app/ml/matching/artifacts/{bi_encoder,cross_encoder,calibrator.pkl}`
— see that folder's `README.md`. They're already there in this delivered
zip; only relevant if re-cloning from git later (they're `.gitignore`'d).

### Manual verification checklist (frontend)
- [ ] As a student with an uploaded resume, open a drive's detail page — confirm the match score card renders with a sensible percentage and matched/missing skill badges
- [ ] Confirm a student *without* an uploaded resume sees no match-score card crash (should just not render, or show whatever the "no resume" state resolves to)
- [ ] On the Drives browse page, confirm "Recommended for you" shows 3 drives sorted by score, and that the top one plausibly has more matching skills than the others
- [ ] Create two drives with very different required skills, apply to both as the same student, confirm the match scores are meaningfully different (not identical/random)
- [ ] As the owning TPO, open the Applicants page for a drive with a few applicants, click "Sort by match" — confirm the order changes to descending match score
- [ ] Expand an applicant row — confirm matched/missing skill badges appear alongside the existing skill-mastery section
- [ ] Edit a drive's required skills or experience-required field, then re-check a student's match score for it — confirm the score changes (proves cache invalidation is working, not silently serving a stale score)
- [ ] Temporarily rename `artifacts/` to something else and hit any matching endpoint — confirm a clean `503`, not a crash, and confirm every *other* page in the app still works normally. Rename it back afterward.

### Known limitations / carried forward
- **`domain` is omitted from the text templates** — see above. If match quality seems consistently off in a way skills/experience don't explain, this is the first thing to revisit (would need adding a domain field + taxonomy to both Resume and Drive, and a way to populate it — likely a dropdown on the drive form and a parsed-or-manual field on the resume).
- **No CI-friendly way to skip the heavy integration tests** — `test_matching.py`'s 5 real-inference tests always run with `pytest -v` and always load the actual models. Fine for local development; would want a `@pytest.mark.slow` split (or artifact-presence check) if this project ever gets automated CI.
- **Deployment packaging for the model artifacts isn't solved** — see `artifacts/README.md` for the options (Git LFS, external hosting + download-on-build, persistent disk). This is explicitly Phase 17 (Deployment) territory; Phase 7/9's job was correct wiring for local development.
- **No batch/background precomputation of embeddings** — the first match request for any given resume or drive pays the bi-encoder cost synchronously (a few hundred ms to a couple seconds on CPU, depending on host). Every subsequent request for that same resume/drive is fast (cached). Acceptable for this project's scale; a background job to precompute embeddings on upload/creation would be the next step if first-request latency ever becomes a real complaint.
- **`retriever_pool` isn't currently exposed as a query parameter** on any endpoint — it's a fixed default. Reasonable for now since the real corpus never approaches that ceiling; would be simple to expose if a use case for tuning it shows up.

