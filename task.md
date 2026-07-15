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

- [ ] Choose one small, testable public capability after the contract is ratified.
- [ ] Add tests before implementation and record its Artifact, evidence, authority and limits.
**Success criteria**: the first code change proves the contract is useful without constructing a premature platform.

Verification evidence (2026-07-15): all local Markdown links resolve; no Markdown
trailing whitespace or legacy system labels remain in the initial public files.
There is intentionally no runtime code, build, lint, test suite, dataset, or
deployment claim in this foundation commit.
