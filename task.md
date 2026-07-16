# Task

## Scope Guard

`task.md` 只追蹤已被擁有者接受的工作、目前的短期板與已定案的後續行動。外部理論、未定案研究與長期猜想必須先留在對應的設計文件，不能被任一代理自行升格為 implementation roadmap。

---

## Active Short Board: Clean Public Foundation (2026-07-15)

> Owner requested a clean `main` for Accountable Dialogue. This board creates a
> documentation-first public baseline; it intentionally imports no legacy Git
> history, runtime code, memory data, private dialogue, automated self-update
> mechanism, or training dataset.

## Phase 1: Establish public identity

- [x] Create an independent repository with a new root commit.
- [x] State the system's observable purpose and explicit non-claims in `README.md`.
- [x] Preserve the owner-selected Apache-2.0 license rather than guessing a legal grant.
**Success criteria**: a new reader can distinguish accountability infrastructure from consciousness or honesty claims.

## Phase 2: Establish the public boundary

- [x] Define what may and may not enter the public repository.
- [x] State that private dialogue and self-modifying mechanisms do not enter by default.
- [x] Add a proposed philosophy/engineering contract with human authority boundaries.
**Success criteria**: the public repository can explain its limits without relying on hidden data.

## Phase 3: Keep research separate from claim

- [x] Record a falsifiable research boundary for accountable epistemic behavior.
- [ ] Owner decides whether to ratify the contract vocabulary.
- [ ] Owner decides whether any future research data may be public, private, or not collected.
**Success criteria**: no dataset, training system, or runtime gate is claimed before consent and evaluation exist.

## Phase 4: First implementation slice

- [x] Owner authorizes a bounded `change-case-v0` prototype, while the wider contract remains under review.
- [x] Add companion tests and a retrospective public record of its Artifact, evidence, authority declaration and limits.
**Success criteria**: the first code change proves the contract is useful without constructing a premature platform.

Historical limitation: commit `d9b7a31` introduced the first tests and implementation together. Public Git
history therefore proves companion tests, but not a preserved red-test stage before that initial code. The
retrospective record explicitly retains this limitation instead of rewriting it as a stronger claim.

Verification evidence (2026-07-15): all local Markdown links resolve; no Markdown
trailing whitespace or legacy system labels remain in the initial public files.
There is intentionally no runtime code, build, lint, test suite, dataset, or
deployment claim in this foundation commit.

---

## Active Short Board: Public Surface Intake (2026-07-15)

> Owner asked to organize what, if anything, should follow the clean public
> foundation. This board is a curation boundary, not authorization to bulk-copy
> a legacy repository.

## Phase 1: Classify legacy material

- [x] Identify that no legacy accountability document or schema is safe to copy unchanged.
- [x] Separate rewriteable concepts from private, historical, generated, or domain-coupled artifacts.
- [x] Record the classification in `docs/plans/public-surface-intake-v0.md`.
**Success criteria**: old public availability is not mistaken for semantic or privacy portability.

## Phase 2: Preserve only generic public contracts

- [x] Add a rewritten observability/evidence boundary without runtime-specific claims.
- [x] Link the new contract from the public README.
**Success criteria**: readers can distinguish shell evidence, partial observability, opacity, authority, and verification without learning the old system's ontology.

## Phase 3: Await a bounded first implementation decision

- [ ] Owner ratifies, narrows, or rejects the proposed contract vocabulary.
- [x] Owner chooses a bounded `change-case-v0` as the first public code slice (2026-07-15).
**Success criteria**: no schema, examples, validator, dataset, or runtime is described as accepted before the owner chooses its boundary.

---

## Active Short Board: Change Case v0 (2026-07-15)

> Owner authorized a small prototype and corrected the model: `Proposal` is a
> subject type; `superseded` is an event. This board does not ratify the wider
> philosophy contract, create a persistence service, or authorize private data.

## Phase 1: Separate semantic layers

- [x] Replace the ambiguous `change-record-v0` working name with `change-case-v0`.
- [x] Separate subject, artifact, evidence, event, and derived projection.
- [x] Remove writable `authority.status` and status-axis fields from the v0 input.
**Success criteria**: type, occurrence, authority, evidence, and display state cannot silently overwrite one another.

## Phase 2: Specify and test the boundary

- [x] Add a public JSON Schema and two synthetic cases.
- [x] Write red tests for valid cases and for rejected conflated/private fields.
**Success criteria**: a reader can see both the accepted shape and the dangerous shapes it rejects.

## Phase 3: Implement only the minimum interpreter

- [x] Add a standard-library validator for local shape and cross-reference checks.
- [x] Add a pure, read-only projection for a subject's recorded history.
- [x] Reject missing or duplicate creation, invalid governance order, and terminal lifecycle conflicts rather than using last-write wins.
- [x] Reject unsafe public locators, delegation references, and common credential-shaped values.
**Success criteria**: validation and projection have no network, database, LLM, memory, or mutation dependency.

## Phase 4: Verify and publish accurately

- [x] Re-run tests, lint, Markdown link checks, and staged-diff checks after the pre-push correction.
- [x] Update README with the exact prototype scope and known limits.
**Success criteria**: the public claim matches the files, tests, and limits actually present.

Initial verification (2026-07-15) passed 6 tests, lint, Schema and document checks. A
pre-push review then found that the tested shape still allowed invalid event history and
unsafe public locators. The local commit was not pushed. This board remains open until the
new semantic and privacy regression tests, lint, Schema, document, and staged-diff checks
have all been repeated.

Final verification (2026-07-15): `python -m pytest tests/ -x` passed 9 tests;
`python -m ruff check accountable_dialogue tests` passed; the public Schema and both
synthetic cases validated with Draft 2020-12; all local Markdown links resolve; no trailing
whitespace or legacy labels remain; and `git diff --check` passed. The pytest warnings came
from the pre-installed `pytest-freezegun` plugin, not from this repository's code.

---

## Active Short Board: Accountable Agent Continuity v0 (2026-07-15)

> Owner asked to record and develop the direction that joins accountable epistemic behavior, continuity,
> correction and governance. It remains a public research/design proposal, not a claim of consciousness,
> an honesty score, a trained capability, or a runtime self-model.

## Phase 1: Record the direction without inflating it

- [x] Write the public-safe research proposal with candidate hypotheses and explicit operationalization gaps.
- [x] Record a separate under-review change case rather than treating the discussion as ratification.
- [x] Write the legacy-concept integration boundary without copying legacy data or runtime.
**Success criteria**: a reader can distinguish the research target, its observable dimensions and its non-claims.

## Phase 2: Dogfood the existing public prototype

- [x] Record `change-case-v0` itself with its Artifact, evidence, authority declaration and limitations.
- [x] Test that repository records pass both structural and semantic checks.
- [x] Record the sequence-ordered report projection revision after it has a stable Artifact revision.
**Success criteria**: the public format can account for its own bounded change without silently overwriting history.

## Phase 3: Evaluation design before model or data work

- [ ] Owner ratifies, narrows or rejects the research vocabulary and any future data boundary.
- [x] Draft a reviewable synthetic evaluation protocol without creating an evaluation-case format or evaluator.
- [x] Record the protocol as an under-review Proposal rather than a model capability or implementation.
- [x] Separate output-level H4a from untested reader-attribution H4b, and add control fixtures and falsification gates.
- [ ] Propose a synthetic, low-risk evaluation-case format only after the protocol and research proposal are reviewed.
- [x] Define candidate baseline, independent-labeling requirements and failure conditions without making an intervention claim.
- [ ] Pre-register run-specific sample, labels, thresholds and model settings before any actual intervention claim.
**Success criteria**: no training dataset, honesty score, personality claim or runtime gate is built ahead of an evaluable protocol.
