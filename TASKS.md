# AUTO DZ ACT — Copilot Task Board (One Checkbox = One Commit)

Hard rules: additive-only; no renames/deletes/refactors; no DOI inference; provenance-first; deterministic paths/keys; do not merge logic across repositories.

## Phase 1 — Documentation and Provenance

- [ ] **[DOCS] Add ZENODO_INDEX.md and provenance map**  
  Create `ZENODO_INDEX.md` with the explicit DOI list only (no additions).

- [ ] **[DOCS] Document RAW ingest contract**  
  Create/update `DATA_CONTRACT.md` describing:
  `data/raw/<YYYY-MM-DD>/<DOI_OR_SOURCE_ID>/payload/` and `/records/` plus required metadata keys.

## Phase 2 — Minimal Utilities (Deterministic + Auditable)

- [ ] **[CORE] Add hashing and timestamps utilities**  
  Add:
  - `src/utils/timestamps.py` → `now_utc_iso()` returns timezone-aware UTC ISO string  
  - `src/utils/hashing.py` → `sha256_file(path)` and `size_bytes(path)`

## Phase 3 — Zenodo Ingest Layer (Append-only RAW)

- [ ] **[INGEST] Add Zenodo fetch module (offline-first)**  
  Add `src/ingest/zenodo_fetch.py`:
  - supports `--input` offline usage
  - minimal online fetch optional; graceful failures with `[ERROR]` and `[HINT]`

- [ ] **[INGEST] Add RAW Zenodo ingest entrypoint contract**  
  Add `src/ingest/ingest_entrypoint.py` implementing CLI:
  `python src/ingest/ingest_entrypoint.py --source zenodo --doi <DOI> --mode ingest [--input <path>] [--output-only]`
  Writes:
  `data/raw/<YYYY-MM-DD>/zenodo_<DOI_SUFFIX>/payload/<record_id>__payload.json`
  `data/raw/<YYYY-MM-DD>/zenodo_<DOI_SUFFIX>/records/<record_id>.json`
  Required metadata:
  `record_id`, `retrieved_utc`, `provenance{source,doi,version}`, `sha256`, `size_bytes`
  Never overwrite; collision => regenerate `record_id`.

- [ ] **[CHORE] Ignore generated raw ingest outputs**  
  Append `data/raw/` to `.gitignore` (additive only).

## Phase 4 — Logic Layer (Non-Interpretive)

- [ ] **[CORE] Add state engine and verification scaffold**  
  Add:
  - `src/logic/state_engine.py` (epistemic states + transition validation API; theory-neutral)
  - `src/logic/verification.py` (PASS/FAIL/UNRESOLVED referencing RAW record IDs only)

## Phase 5 — Status Tracking

- [ ] **[DOCS] Add PROJECT_STATUS.md scaffold**  
  Add `PROJECT_STATUS.md` with restricted statuses:
  COMPLETE / PARTIAL / MISSING  
  Evidence must reference DOIs or RAW paths only (no invented evidence).

## STOP RULE
After completing the checked tasks, stop. Do not refactor; do not expand scope; do not merge logic across repos.
