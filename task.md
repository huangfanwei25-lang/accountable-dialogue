# Task

## Scope Guard

`task.md` 只追蹤已被擁有者接受的工作、目前的短期板與已定案的後續行動。外部理論、未定案研究與長期猜想必須先留在對應的設計文件，不能被任一代理自行升格為 implementation roadmap。

---

## Active Short Board: Cross-Model Continuity Profile v0 (2026-07-22)

> Owner authorized a bounded public profile for cross-model handoff. It defines public integration
> boundaries only; it does not authorize private-memory import, runtime integration, identity claims,
> automated synchronization, or a second public data protocol.

## Phase 1: Define the public profile

- [x] Separate Accountable Dialogue, Private Memory and ToneSoul ownership.
- [x] Keep `change-case-v0` as this Profile's only cross-repository public JSON exchange contract.
- [x] Bound public deliberative stance and resource observations without inferring identity or budget.

**Success criteria**: a consumer can distinguish portable public accountability from private continuity and runtime state.

## Phase 2: Add thin model entrypoints

- [x] Add one canonical `AGENTS.md` and thin Claude, Gemini and Copilot routing files.
- [x] Test that adapters do not route agents to private context or create a parallel protocol.

**Success criteria**: model-specific files converge on the same public boundary without duplicating policy.

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
- [x] Preserve the initial protocol proposal and record its v0.2 refinement as a successor rather than overwriting it.
- [x] Draft the candidate evaluation-case data boundary without creating a Schema, fixture, runner, model call, or result claim.
- [x] Owner authorizes a bounded local small-model pilot and its public synthetic evaluation-case format (2026-07-16); the wider research vocabulary remains under review.
- [x] Propose a synthetic, low-risk evaluation-case format only after the protocol and research proposal are reviewed.
- [x] Define candidate baseline, independent-labeling requirements and failure conditions without making an intervention claim.
- [x] Lock the exploratory run-specific cases, label key digest, model targets, settings and stop rules before any model call.
**Success criteria**: no training dataset, honesty score, personality claim or runtime gate is built ahead of an evaluable protocol.

---

## Active Short Board: Synthetic Small-Model Pilot v0 (2026-07-16)

> Owner authorized an exploratory local pilot only: six fully fictional, low-risk, reversible cases;
> B0/I1 comparison; and two small local models. This does not authorize private inputs, training,
> H4b reader research, public release of unreviewed raw outputs, or any claim about inner honesty.

## Phase 1: Fix inputs before execution

- [x] Add the public case Schema, six fixtures and a separate annotation key.
- [x] Test material equivalence, response-envelope equality, label exclusion and public-data checks.
**Success criteria**: the inputs can be checked without calling a model.

## Phase 2: Build a local-only runner

- [x] Allow only loopback Ollama and already-installed model names.
- [x] Write raw output only outside the repository, with a minimal run manifest and blind A/B package.
- [x] Add fake-transport tests; never call a real model during unit tests.
**Success criteria**: no hidden network, memory, prompt or repository-output side effect.

## Phase 3: Run and account for the pilot

- [ ] Verify both local model targets are available and execute the fixed 24-call matrix.
- [x] Start the fixed matrix once; stop it before any completed response when CPU execution made the fixed budget disproportionate, and preserve an inconclusive attempt record.
- [ ] Inspect output safety and mechanical integrity before selecting any public Artifact.
- [ ] Record results, non-results or blocked execution with limits in a new change case.
**Success criteria**: any conclusion is bounded to the run, inputs and models actually observed.

---

## Active Short Board: Local Resource Smoke Test v0 (2026-07-16)

> The full 24-call pilot attempt stopped before a completed response under CPU execution. This is a
> narrower successor under the existing local-model authorization, not a rewrite of the original run.
> It measures runner feasibility only and cannot create a behavioral-effect claim.

## Phase 1: Fix the reduced matrix

- [x] Commit the one-case Qwen B0/I1 selection, `num_predict=128`, 90-second timeout and 240-second wall-time gate.
- [x] Test CLI case selection without calling a real model.
**Success criteria**: the reduced budget is explicit and cannot be confused with the original 24-call matrix.

## Phase 2: Run and account

- [x] Confirm the single local model remains installed, then execute exactly two calls.
- [x] Inspect temporary raw output and manifest before publishing a synthetic-only summary; both responses failed the evidence-reference mechanical gate.
- [x] Record the outcome as a separate smoke-test case, including the observed contract failure and its limits.
**Success criteria**: no semantic label or model-effect conclusion is made from a resource smoke test.

---

## Active Short Board: Evidence-reference Contract Smoke v0.2 (2026-07-16)

> The first resource smoke completed its two calls but both failed the evidence-reference
> mechanical gate. This board fixes that prompt/validator mismatch in a new, traceable
> successor under the existing bounded local-pilot authorization. It does not rewrite the
> first run or authorize a semantic-effect claim.

## Phase 1: Fix and freeze the response contract

- [x] Add renderer and fake-transport regression tests for exact evidence ids, bracketed ids and non-evidence ids.
- [x] Make the response instruction name only permitted evidence ids and write its version into the run manifest.
- [x] Commit and push this successor plan before a live call.
**Success criteria**: the model-visible instruction and mechanical validator impose the same evidence-reference boundary.

## Phase 2: Run and account separately

- [x] Verify `qwen2.5:1.5b` remains locally installed, then execute exactly two calls; both passed the then-defined mechanical status but used empty `evidence_refs`.
- [x] Inspect temporary output and manifest before selecting synthetic-only public Artifacts; all released content is fully fictional and public-safe.
- [x] Record the separate v0.2 outcome as an inconclusive citation-adequacy observation, without a semantic label or B0/I1 effect claim.
**Success criteria**: v0.2 is attributable to its own response-contract revision and cannot overwrite the v0.1 result.

---

## Active Short Board: Response-reference Contract Smoke v0.3 (2026-07-16)

> v0.2 correctly preserved a new limitation: an empty `evidence_refs` array passed its
> mechanical validator, and a bracketed `prior_claim_ref` was not checked. This successor
> only tightens externally visible reference syntax under the existing bounded local-pilot
> authorization. It is not a semantic score, philosophical ratification or model claim.

## Phase 1: Freeze the v0.3 contract

- [x] Write failing fake-transport coverage for empty evidence refs and non-exact claim refs.
- [x] Require non-empty exact evidence ids and exact-or-not-applicable claim refs in the shared renderer and validator.
- [x] Commit and push the v0.3 plan and code before any live call.
**Success criteria**: B0 and I1 share the same traceability contract, and the runner preserves rather than corrects invalid references.

## Phase 2: Run and account separately

- [x] Verify `qwen2.5:1.5b` remains locally installed, then execute exactly two calls; both met the v0.3 reference-envelope gate.
- [x] Inspect temporary output and manifest before selecting synthetic-only public Artifacts; all released content is fully fictional and public-safe.
- [x] Record the separate v0.3 result as a reference-syntax verification, without a semantic label or B0/I1 effect claim.
**Success criteria**: v0.3 stays attributable to its own revision and does not turn reference syntax into a claim of semantic correctness.

---

## Active Short Board: H1 Blind Semantic Annotation Preparation v0 (2026-07-16)

> Owner accepted preparation of a blind semantic-annotation direction after the v0.3 syntax smoke.
> This board authorizes only public-safe packet and commitment infrastructure. It does not authorize
> a new live run, choosing or contacting annotators, collecting ratings, exposing a mapping, or claiming
> an H1/B0/I1 result.

## Phase 1: Fix the blind data boundary

- [x] Define a closed blind-packet shape containing shared synthetic material, one response and case-local rubric but no condition mapping or model metadata.
- [x] Require a high-entropy private mapping nonce commitment instead of a publicly enumerable mapping hash.
- [x] Test that invalid/unpaired outputs are rejected rather than silently excluded from packetization.
- [x] Record the limited implementation and verification in `change-case-v0`, without claiming a semantic result.
**Success criteria**: a future reviewer can see what a rater may judge without seeing which condition generated it.

## Phase 2: Await procedural authority

- [x] Owner chooses two external independent human annotators as the intended formal H1 review lane; assistant and models remain non-independent advisory lanes.
- [ ] Owner appoints the two people and fixes what they may see or retain, including a no-mapping/no-other-verdict attestation.
- [ ] Owner chooses whether to authorize a fresh H1 four-response run under the frozen protocol.
- [ ] Only then create a run-specific change case, packetize outputs, collect independent verdicts and reveal the mapping.
**Success criteria**: no semantic comparison happens without an independently reviewable process and an explicit human decision.

---

## Active Short Board: J0 Small-Model Judge Feasibility v0 (2026-07-16)

> Owner asked whether the installed small local models can serve as judges. This is a separate, fully
> synthetic calibration of an auxiliary tool. It cannot replace the two external human H1 raters,
> recreate the owner's full context, or establish an honesty, personality, consciousness or self-model claim.

## Phase 1: Fix the calibration before a model call

- [x] Add a closed calibration fixture/key, renderer, parser and comparison model that keeps expected verdicts out of prompts.
- [x] Include clear pass/fail cases plus a candidate-response instruction-data control.
- [x] Test loopback-only execution, output isolation, closed judge JSON, reference checks and no silent correction.
**Success criteria**: model output can be mechanically compared with a precommitted synthetic oracle without leaking it to the model.

## Phase 2: Resource-gated local probe

- [x] Commit and push the J0 harness, plan and preparation change case before a live call.
- [x] Preserve one direct-script preflight launch failure before any model call; its import-path successor must be committed before the probe starts.
- [x] Run the fixed two-packet Qwen probe and one-packet Llama resource probe once; all three ended as `transport_error`, with no retry and no verdict.
- [x] Record the bounded inconclusive result without reporting an aggregate judge score.
**Success criteria**: the repository can distinguish a usable calibration candidate from a format/resource failure without treating either as human judgment.

## Phase 3: Decide whether any extra model is warranted

- [x] Do not download before the initial probe.
- [ ] If needed, consider only the fixed official Ollama Qwen3 tag after source, digest, local-only and scan checks.
- [ ] Keep any extra model on a one-packet synthetic probe until its own result is separately accounted for.
**Success criteria**: convenience never expands the trust or supply-chain boundary silently.

---

## Active Short Board: J0 Host Compatibility Diagnosis v0 (2026-07-16)

> The fixed J0 initial probe completed all three calls without a verdict. Read-only diagnostics correlate
> those calls with native `llama-server` crashes on Windows 10 build 1903, below Ollama's documented
> Windows 10 22H2 minimum. This is a host/runtime compatibility candidate, not a model-judge conclusion.

## Phase 1: Preserve the diagnosis without another model call

- [x] Preserve the initial probe as inconclusive before inspecting host state.
- [x] Confirm loopback catalog endpoints remain available and correlate the three call times with native runner crash events.
- [x] Check the OS build against the vendor's documented Windows support floor.
**Success criteria**: the repository distinguishes a host failure candidate from a claim about Qwen, Llama or human judgment.

## Phase 2: Await an external-environment decision

- [ ] Owner chooses a supported host upgrade, a separate supported host, or to stop local model-judge exploration.
- [ ] Only after that decision, create a new synthetic-only successor plan; never retry the original three calls.
**Success criteria**: a repository automation does not alter the user's OS, restart services or download models to bypass an unsupported host boundary.

---

## Active Short Board: J0 Transport Observability Successor v0 (2026-07-16)

> The initial J0 result is preserved. This successor improves only the safe failure vocabulary for a future,
> separately authorized compatibility probe; it does not send a new generation on the current unsupported host.

## Phase 1: Fix the diagnostic boundary with mocks only

- [x] Preserve finite transport categories and optional HTTP status without serializing error text, bodies, headers, URLs or local paths.
- [x] Test HTTP 4xx/5xx, network failure, timeout and provider-contract failure with deliberately sensitive-looking fake details.
- [x] Keep a valid judge verdict separate from a provider contract failure and preserve the existing `mechanical_status` vocabulary.
**Success criteria**: future external output can explain a transport stop without becoming a private server log.

## Phase 2: Remain inactive until the host decision

- [ ] Do not execute this successor on the current Windows 1903 host.
- [ ] If the owner supplies a supported host decision, create a one-packet synthetic-only plan and record it before any generation.
**Success criteria**: better error accounting never becomes a disguised retry of the original probe.
