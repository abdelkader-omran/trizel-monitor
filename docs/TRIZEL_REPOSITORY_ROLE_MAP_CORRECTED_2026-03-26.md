# TRIZEL Repository Role Map — Corrected Architectural Record
**Date:** 2026-03-26
**Status:** CANONICAL — supersedes the control-center conclusion from the 2026-03-26 inspection session

---

## Scope of This Document

This document is the authoritative repository-fixed record of the corrected architectural position
reached on 2026-03-26. It exists to institutionalise a correction that was accepted in analysis but
had not yet been written into a repository file.

**Sections 1–6 of the original 2026-03-26 inspection remain unchanged and are not reproduced here.**
Those sections cover: repository map, canonical roles, file/workflow ownership, execution ownership
matrix, boundary violations, and handoff flow. All findings in those sections are accepted as-is.

**Sections 7–8 of the original inspection are superseded by this document in their entirety.**
The previous formulation of Section 7 incorrectly concluded that `AUTO-DZ-ACT-ANALYSIS-3I-ATLAS`
was the project-wide control center. That conclusion went beyond what is warranted at this stage and
is replaced by the corrected position below.

---

## CORRECTED SECTION 7: Control-Center Assessment

### 7.1 Current Architecture Is Layered and Distributed

The current TRIZEL architecture is formally **multi-repository with strict layer separation**.
No single repository acts as a global control center. The confirmed layer assignments are:

| Layer | Repository | Role |
|-------|-----------|------|
| Layer-0 (Governance) | `trizel-core` | Governance root; defines invariants, cross-repo rules, epistemic pipeline |
| Layer-1 (Monitor/Retrieval) | `trizel-monitor` | Upstream retrieval, snapshot generation, data classification |
| Layer-1 (Preservation) | `AUTO-DZ-ACT-3I-ATLAS-DAILY` | Authoritative daily archive, provenance records, dispatch trigger |
| Layer-3 (Analysis) | `AUTO-DZ-ACT-ANALYSIS-3I-ATLAS` | Deterministic epistemic analysis, admissibility gate, observation population |
| Lab (future) | `TRIZEL-LAB` | Planned lab execution environment |
| Publication/Coordination (future) | `trizel-site-artifacts` / `phase-e-gateway` | Publication surface; pre-lab coordination |
| Portal/Display | `trizel-AI` | Official reference portal, governance registry display |

This separation is actively enforced by the provenance HARD GATE (ANALYSIS will not process data
without verified DAILY provenance), by PR-mediated handoffs between repositories, and by
human-authorised gate workflows.

### 7.2 What `AUTO-DZ-ACT-ANALYSIS-3I-ATLAS` Is Today

`AUTO-DZ-ACT-ANALYSIS-3I-ATLAS` is the **analysis execution repository**. Within its layer scope it
performs cross-repository coordination as a natural consequence of being the analysis consumer:
it checks out DAILY (read-only), builds observations, and dispatches to the publication surface via PR.

This behaviour is **local orchestration within the analysis execution path**. It reflects the natural
position of the analysis layer, which must receive inputs and emit outputs. It does **not** make
ANALYSIS the project-wide control center, and it must not be elevated to that role at this stage.

The distinction is:
- **Current role (confirmed):** ANALYSIS executes the analysis layer and, as part of that execution,
  coordinates with its immediate upstream (DAILY) and immediate downstream (site artifacts).
- **Not confirmed, not locked:** ANALYSIS as the global orchestration hub for the entire TRIZEL
  project, including governance, lab execution, publication coordination, and future layers.

### 7.3 Control-Center as a Future Concept (Optional, Not Yet Locked)

A dedicated control-center concept — a separate orchestration repository that coordinates all
repositories without owning any scientific execution — is **plausible as a future addition** to the
architecture. It is **not a currently established role** and must not be treated as one.

**If a control-center repository is introduced later, the following constraints apply:**

- It must be a **new, dedicated repository** — not a redefinition or expansion of ANALYSIS.
- Its role must be **governance-neutral**: it may coordinate triggers and monitor handoffs, but
  must not own epistemic logic, preservation records, or publication authority.
- It must defer governance definitions to `trizel-core`.
- It must defer scientific execution to ANALYSIS.
- It must defer preservation to DAILY.
- It must defer publication to the site layer.
- It must never absorb the responsibilities of any existing layer.

**Conditions that would justify introducing a control center:**
- The pipeline has expanded to more than ~4 active execution repositories requiring cross-repo
  state tracking.
- Handoff gaps cannot be resolved by direct layer-to-layer workflow triggers.
- Temporal or dependency coordination between multiple active lab repositories requires
  centralised orchestration.

**Until those conditions are met, the distributed layered model is the correct and formally
declared architecture.**

### 7.4 Summary of Control-Center Decision

| Question | Answer |
|----------|--------|
| Is a control-center currently established? | **NO** |
| Should ANALYSIS be declared the control center? | **NO** — it is the analysis layer, not a global orchestrator |
| Is a future control-center plausible? | **YES** — as a separate, dedicated repository |
| Is it a locked decision now? | **NO** — not yet warranted by current system complexity |
| Where does governance authority live? | `trizel-core` (Layer-0) — this is locked |

---

## CORRECTED SECTION 8: Final Governance Recommendation

### 8.1 Canonical Structure

The canonical project-wide governance structure, as determined by the 2026-03-26 inspection and
fixed by this correction, is:

```
trizel-core                        → Governance root (Layer-0)
    ↓ defines rules for all layers

trizel-monitor                     → Retrieval and monitoring (Layer-1)
    ↓ feeds (handoff gap — must be codified)

AUTO-DZ-ACT-3I-ATLAS-DAILY         → Authoritative preservation (Layer-1)
    ↓ dispatches to

AUTO-DZ-ACT-ANALYSIS-3I-ATLAS      → Analysis execution (Layer-3)
    ↓ (future) gates through

phase-e-gateway                    → Pre-lab coordination (future)
    ↓ passes to

TRIZEL-LAB                         → Lab execution (future)

AUTO-DZ-ACT-ANALYSIS-3I-ATLAS      → Also dispatches publication artifacts to
    ↓

trizel-site-artifacts              → Publication surface (future)
    ↓ displays on

trizel-AI                          → Governance-compliant public portal
```

Each node in this graph **owns its layer and its layer only**. No node currently coordinates all
other nodes. **The graph is the architecture.**

### 8.2 Canonical Role Summary

| Repository | Canonical Role | Notes |
|-----------|---------------|-------|
| `trizel-core` | Governance root | Layer-0; all other layers defer to it |
| `trizel-monitor` | Retrieval / monitoring | Upstream data collection; feeds DAILY |
| `AUTO-DZ-ACT-3I-ATLAS-DAILY` | Authoritative preservation | Archive record; dispatch trigger to ANALYSIS |
| `AUTO-DZ-ACT-ANALYSIS-3I-ATLAS` | Analysis execution | Admissibility gate; structural execution |
| `TRIZEL-LAB` | Lab execution | Future; not active until provenance continuity confirmed |
| `phase-e-gateway` | Pre-lab coordination | Future; read-and-validate gate between ANALYSIS and LAB |
| `trizel-site-artifacts` | Publication surface | Future; receives PRs from ANALYSIS |
| `trizel-AI` | Governance portal | Displays canonical documentation and registry |

### 8.3 No Repository Holds a Global Control Role Today

This is the explicit corrected position replacing the previous overclaim:

> **No repository currently holds a global control role in the TRIZEL project.**
>
> - `trizel-core` holds governance authority (definitions, rules, invariants).
> - `AUTO-DZ-ACT-ANALYSIS-3I-ATLAS` holds analysis execution authority (admissibility, observations).
> - These are distinct roles. Governance authority and analysis execution authority are not the same thing as project-wide operational control.
>
> A future control-center repository is plausible but is not a locked architectural decision.
> If introduced, it must be a new dedicated repository, not an expansion of any existing layer.

### 8.4 The One Structural Action Required

The only gap that prevents the existing distributed architecture from operating end-to-end without
manual intervention is:

> **The `trizel-monitor` → `AUTO-DZ-ACT-3I-ATLAS-DAILY` handoff must be codified in a workflow.**

Currently `trizel-monitor`'s `daily.yml` commits SNAPSHOT data to its own repository and stops.
No mechanism delivers those snapshots — with proper provenance blocks — to DAILY. All other
handoffs in the pipeline have explicit, automated workflow steps. This one does not.

Resolving this gap closes the only broken link in the chain. It requires changes only to
`trizel-monitor` (or DAILY) and does **not** require introducing a control center.

### 8.5 Final Safety Judgment

The TRIZEL project can be safely operated long-term under the current layered, distributed model,
**without a global control-center repository**, provided:

1. The `trizel-monitor` → DAILY handoff is codified in a workflow.
2. Provisional data without provenance blocks in ANALYSIS is removed or explicitly tagged
   non-canonical.
3. Site generation scripts in `trizel-monitor` (`site/`, `scripts/generate_pages.py`) are
   acknowledged as a tolerated display convenience or eventually migrated to the publication layer.
4. `TRIZEL-LAB` and `phase-e-gateway` are not activated until provenance continuity past
   2026-03-17 is established.
5. If a control-center concept is introduced in the future, it is implemented as a new dedicated
   repository, **not** as an expansion of ANALYSIS.

---

## Explicit Supersession Statement

The following conclusion from the 2026-03-26 inspection session is hereby **superseded and must
not be treated as an authoritative architectural record**:

> *"AUTO-DZ-ACT-ANALYSIS-3I-ATLAS is the project-wide control center."*

The corrected and now repository-fixed position is:

> *"No repository currently holds a global control role. The architecture is layered and distributed.
> A future control-center concept is plausible but not locked. If introduced, it must be a
> separate dedicated repository."*

---

## Document Provenance

| Field | Value |
|-------|-------|
| Original inspection date | 2026-03-26 |
| Correction accepted date | 2026-03-26 |
| Repository-fixed date | 2026-03-26 |
| Sections unchanged | 1, 2, 3, 4, 5, 6 |
| Sections superseded | 7, 8 |
| Superseding document | This file: `docs/TRIZEL_REPOSITORY_ROLE_MAP_CORRECTED_2026-03-26.md` |
| Change type | Documentation only — no code, no workflow, no data changes |
