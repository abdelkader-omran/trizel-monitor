# Handoff: trizel-monitor → AUTO-DZ-ACT-3I-ATLAS-DAILY

**Version:** 1.0.0  
**Status:** AUTHORITATIVE  
**Date:** 2026-03-26  
**Scope:** Retrieval-to-preservation handoff codification

---

## 1. Purpose

This document is the authoritative record of the governed handoff mechanism from
`trizel-monitor` (retrieval layer) to `AUTO-DZ-ACT-3I-ATLAS-DAILY` (authoritative
preservation layer).

It closes the structural gap identified in §8.4 of
`docs/TRIZEL_REPOSITORY_ROLE_MAP_CORRECTED_2026-03-26.md`.

---

## 2. Layer Boundary

| Repository | Role | Handoff direction |
|---|---|---|
| `trizel-monitor` | Retrieval / monitoring | **SOURCE** |
| `AUTO-DZ-ACT-3I-ATLAS-DAILY` | Authoritative preservation | **TARGET** |

`trizel-monitor` owns retrieval only. It does not own preservation.  
`AUTO-DZ-ACT-3I-ATLAS-DAILY` owns preservation only. It does not own retrieval.  
The handoff is unidirectional: monitor → DAILY.

---

## 3. Handoff Mechanism

The handoff is implemented as a GitHub `repository_dispatch` event sent from
`trizel-monitor`'s `daily.yml` workflow to `AUTO-DZ-ACT-3I-ATLAS-DAILY` after
each successful or diagnostically complete retrieval run.

### 3.1 Trigger step (in `.github/workflows/daily.yml`)

The step "Dispatch to DAILY preservation layer" fires when:
- `TRIZEL_EXIT_CODE` is `0` (successful retrieval) **or**
- `TRIZEL_EXIT_CODE` is `2` (API error — diagnostic snapshot written)

It does **not** fire on fatal errors (exit code 3 or higher), because no valid
snapshot exists in those cases.

### 3.2 Dispatch payload

```json
{
  "event_type": "trizel-monitor-snapshot",
  "client_payload": {
    "run_date":        "YYYY-MM-DD (UTC)",
    "retrieved_utc":   "ISO-8601 UTC timestamp",
    "exit_code":       "0 | 2",
    "source_repo":     "abdelkader-omran/trizel-monitor",
    "snapshot_latest": "data/snapshot_3I_ATLAS_latest.json"
  }
}
```

`snapshot_latest` is the stable path to the most recent snapshot committed to
`trizel-monitor`. DAILY uses this as a reference to check out or fetch the
authoritative snapshot for preservation.

---

## 4. Secret Configuration (REQUIRED)

The dispatch requires a Personal Access Token (PAT) stored as a repository secret
in `trizel-monitor`.

| Secret name | Required scope | Purpose |
|---|---|---|
| `DAILY_DISPATCH_TOKEN` | `repo` (for private) or `public_repo` (for public) | Authorize `repository_dispatch` to `AUTO-DZ-ACT-3I-ATLAS-DAILY` |

**If `DAILY_DISPATCH_TOKEN` is not set, the dispatch step fails with a clear error.**
The secret must be configured in `trizel-monitor` repository settings before
governed preservation can operate end-to-end.

---

## 5. DAILY Receiving Workflow (Required in AUTO-DZ-ACT-3I-ATLAS-DAILY)

`AUTO-DZ-ACT-3I-ATLAS-DAILY` must have a workflow that listens for the
`trizel-monitor-snapshot` dispatch event and handles preservation through a
PR-based path (branch-protection-compliant).

The receiving workflow must:

1. Trigger on `repository_dispatch` with `event_type == 'trizel-monitor-snapshot'`
2. Extract `client_payload.run_date` and `client_payload.snapshot_latest`
3. Check out or fetch the snapshot from `trizel-monitor` at the committed ref
4. Write the snapshot into DAILY's governed preservation path
5. Open a PR (not a direct push) against DAILY's protected `main` branch
6. Emit provenance block referencing `source_repo`, `run_date`, and `retrieved_utc`

This PR-based path is required for branch-protection compliance.

---

## 6. Durable Preservation Guarantee

- The dispatch event is accepted by GitHub's API synchronously (HTTP 204)
- A failed dispatch exits the monitor workflow with a non-zero code, which
  surfaces in CI and prevents silent data loss
- The snapshot committed to `trizel-monitor` is durable (in git history)
  regardless of DAILY's processing status, so no data is lost if DAILY's
  receiving workflow is delayed or retried
- DAILY's PR-based path ensures the snapshot enters a governed,
  branch-protection-compliant record in the preservation repository

---

## 7. Re-Run Admissibility for 2026-03-26

**Operational status after this PR merges:**

| Condition | Status |
|---|---|
| Monitor-to-DAILY handoff mechanism codified | ✅ YES — implemented in this PR |
| `DAILY_DISPATCH_TOKEN` secret present | ⚠ REQUIRES MANUAL CONFIGURATION |
| DAILY receiving workflow present | ⚠ MUST EXIST IN AUTO-DZ-ACT-3I-ATLAS-DAILY |

**Re-run admissibility:**

A governed re-run for 2026-03-26 is **operationally admissible** after this PR
merges, subject to the following conditions:

1. `DAILY_DISPATCH_TOKEN` is configured as a repository secret in `trizel-monitor`
2. `AUTO-DZ-ACT-3I-ATLAS-DAILY` has a `repository_dispatch` receiving workflow
3. A manual `workflow_dispatch` trigger is fired on `trizel-monitor`'s `daily.yml`

**Important provenance note:** A re-run triggered after 2026-03-26 will retrieve
current SBDB orbital elements, not the exact state of the API as of 2026-03-26.
The `retrieved_utc` field in the snapshot will correctly record the actual
retrieval timestamp (re-run date), not the original blocked date. This is
provenance-correct: the snapshot records when data was actually retrieved, not
when retrieval was intended.

**Residual blocker (if any):**

If `DAILY_DISPATCH_TOKEN` is not configured or DAILY's receiving workflow does
not exist, the residual blocker is:

> The dispatch step will fail with a clear error message. Preservation cannot
> proceed until both prerequisites are satisfied. The error message in the
> workflow log will specify exactly which prerequisite is missing.

No ambiguity remains in the monitor-to-DAILY handoff path itself.

---

## 8. What Changed and Why It Closes the Gap

**Before this PR:**
- `daily.yml` committed snapshots to `trizel-monitor` and stopped.
- No mechanism existed to notify or trigger `AUTO-DZ-ACT-3I-ATLAS-DAILY`.
- Preservation depended on manual intervention or knowledge of the gap.

**After this PR:**
- `daily.yml` dispatches a `repository_dispatch` event to DAILY after every
  successful or diagnostic run.
- The dispatch carries a structured payload with run date, timestamps, exit
  code, and snapshot reference.
- A missing `DAILY_DISPATCH_TOKEN` causes a hard failure (not silent skip),
  making the gap immediately visible in CI.
- The handoff is documented, deterministic, and reproducible.

This is the minimum change required to close the handoff gap without overreaching
into DAILY's preservation logic or ANALYSIS's execution layer.

---

## 9. Document Provenance

| Field | Value |
|---|---|
| Gap identified | `docs/TRIZEL_REPOSITORY_ROLE_MAP_CORRECTED_2026-03-26.md` §8.4 |
| Fix implemented | `.github/workflows/daily.yml` — "Dispatch to DAILY preservation layer" step |
| Change type | Workflow addition + documentation |
| Layer boundaries violated | None |
| Data fabricated | None |
