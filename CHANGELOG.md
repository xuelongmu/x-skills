# Changelog

Notable changes to the skills and their installation, grouped by date. Add new
entries under the current date. Backfilled entries use mainline commit dates;
these are not versioned releases. For current installation instructions, see the
[README](README.md#setup).

## 2026-09-13

### Changed

- PR base updates follow repository conventions, using rebase for linear history
  or an established rebase workflow.

## 2026-09-06

### Added

- This changelog, backfilled from repository history through 2026-09-05.

### Changed

- Tightened skill selection around the requested outcome and current task phase.
  Browser evidence applies to specific UI verification or captures; learning
  capture, research stewardship, coordination, and review workflows have clearer
  boundaries. Publication, maintenance, and landing retain separate endpoints.

### Removed

- `drive-agent-orchestrator` and `prompt-agent-orchestrator`, including their
  metadata and prompt template. General delegated coordination remains available
  through `orchestrate`.

### Fixed

- Stopped the PR watcher from treating the Codex connector's generated review
  activity summary as actionable feedback. Separate findings still block merging.

## 2026-09-05

- Added `orchestrate` for coordinating delegated engineering work across agent
  harnesses, then simplified its guidance around ownership, dependencies, and
  useful progress updates. [Addition](https://github.com/xuelongmu/x-skills/commit/ce9a2ec),
  [simplification](https://github.com/xuelongmu/x-skills/commit/d41ad36).
- Added `show-me` for visual technical explanations and made it an optional
  supporting skill for architecture, review, and learning workflows. Simplified
  recurring-learning handoffs. [PR #32](https://github.com/xuelongmu/x-skills/pull/32).
- Adopted the pinned upstream Agent Skills validator and retained focused local
  metadata, layout, resource, and watcher checks. Removed redundant tests and
  repository-owned installer lifecycle tests.
  [PR #33](https://github.com/xuelongmu/x-skills/pull/33).

## 2026-09-04

- Shortened skill entrypoints and moved conditional detail into supporting
  references. Consolidated shared publication and maintenance operations under
  `land`; `publish` and `babysit` use those resources.
- Moved browser fallback launchers into bundled scripts. Simplified review and
  architecture guidance, removing mandatory report templates and host-specific
  approval rules from portable workflows.
- Kept continuous babysitting active through quiet cycles and made merge the
  default base-sync method when no repository policy says otherwise.
  [Changes](https://github.com/xuelongmu/x-skills/commit/aa1e151).

## 2026-09-01

- Added `capture-learning` for durable, verified engineering knowledge and
  `review-change` for evidence-backed change review.
  [Addition](https://github.com/xuelongmu/x-skills/commit/0f673ff).
- Renamed `code-meta-reviewer` to `review-complexity` and integrated it as optional
  support for change reviews. Kept ordinary change review self-contained.
  [Integration](https://github.com/xuelongmu/x-skills/commit/7c98d1e),
  [review boundary](https://github.com/xuelongmu/x-skills/commit/775ddc7).
- Added `design-architecture` and `review-architecture` for consequential system
  choices and assessment of proposals before acceptance.
  [PR #29](https://github.com/xuelongmu/x-skills/pull/29).

## 2026-08-31

- Consolidated shared skills under `.agents/skills` using standard Agent Skills
  frontmatter, with product metadata kept separately. Moved the PR watcher into
  its skill's `scripts/` directory.
  [Consolidation](https://github.com/xuelongmu/x-skills/commit/e325d54).
- Folded `publish-slack` into `land` as a PR-sharing mode that does not imply
  merging. [Change](https://github.com/xuelongmu/x-skills/commit/a5496c5).
- Pinned merging to the exact PR head validated by the watcher.
  [Fix](https://github.com/xuelongmu/x-skills/commit/5c58fb9).
- Added overengineering review, initially called `code-simplifier` and renamed
  to `code-meta-reviewer`, with edits conditional on user intent.
  [Addition](https://github.com/xuelongmu/x-skills/commit/8f9e06b),
  [rename](https://github.com/xuelongmu/x-skills/commit/96c8628).
- Added repository-aware base synchronization to `babysit`.
  [Change](https://github.com/xuelongmu/x-skills/commit/53e3be7).
- Established `npx skills update` as the refresh path, including reconciliation
  of upstream removals, and clarified installation scope and legacy migration.
  [Refresh](https://github.com/xuelongmu/x-skills/commit/8728ae2),
  [migration](https://github.com/xuelongmu/x-skills/commit/7d25fbc).

## 2026-08-30

- Added `google-developer-style` for English developer documentation.
  [Addition](https://github.com/xuelongmu/x-skills/commit/18c2dca).
- Introduced canonical shared skill sources and switched documented installation
  to the Skills CLI. [Shared sources](https://github.com/xuelongmu/x-skills/commit/f69fcba),
  [installation](https://github.com/xuelongmu/x-skills/commit/8035ff7).

## 2026-08-16

- Let `land` publish a missing PR before maintaining and merging it. Hardened
  publication-state handling, repository targeting, and check identity, and
  stopped treating clean Codex review summaries as actionable feedback.
  [PR #20](https://github.com/xuelongmu/x-skills/pull/20).

## 2026-08-15

- Made the landing feedback grace window configurable.
  [PR #19](https://github.com/xuelongmu/x-skills/pull/19).

## 2026-08-10

- Reduced watcher polling frequency and used elapsed time for timeouts.
  Rechecked final PR state to avoid declaring readiness from stale observations.
  [PR #17](https://github.com/xuelongmu/x-skills/pull/17).
- Stopped babysitting and cleaned up its monitor when a PR is merged or closed.
  [PR #18](https://github.com/xuelongmu/x-skills/pull/18).

## 2026-08-08

- Migrated Claude commands into skill packages and added shared repository
  guidance for both hosts. [PR #12](https://github.com/xuelongmu/x-skills/pull/12),
  [PR #14](https://github.com/xuelongmu/x-skills/pull/14).
- Added `steward-research` for reproducibility and research handoff, and added
  the Codex variant of the Agent Orchestrator driver.
  [PR #13](https://github.com/xuelongmu/x-skills/pull/13),
  [PR #16](https://github.com/xuelongmu/x-skills/pull/16).
- Fixed review-thread lookup and scoped PR feedback and check requests to the
  selected repository and GitHub host, including custom enterprise ports.
  [PR #15](https://github.com/xuelongmu/x-skills/pull/15).

## 2026-08-05

- Added the Agent Orchestrator driver and renamed `author-ao-orchestrator` to
  `prompt-agent-orchestrator`.
  [PR #10](https://github.com/xuelongmu/x-skills/pull/10).
- Renamed `slack-pr` to `publish-slack`.
  [PR #11](https://github.com/xuelongmu/x-skills/pull/11).

## 2026-08-04

- Added browser evidence workflows for both hosts.
  [PR #5](https://github.com/xuelongmu/x-skills/pull/5).
- Added the Codex `publish` skill and renamed the Claude PR-creation command to
  `publish`, separating publication from readiness maintenance and landing.
  [PR #6](https://github.com/xuelongmu/x-skills/pull/6).
- Folded `codex-watch` readiness notifications into Claude babysitting and
  removed the separate command.
  [PR #7](https://github.com/xuelongmu/x-skills/pull/7).

## 2026-07-23

- Added Agent Orchestrator prompt authoring for both hosts under the original
  name `author-ao-orchestrator`.
  [PR #3](https://github.com/xuelongmu/x-skills/pull/3).

## 2026-07-21

- Made `land` follow repository merge conventions instead of assuming squash
  merging. [PR #4](https://github.com/xuelongmu/x-skills/pull/4).

## 2026-06-25

- Added the `codex-watch` command to notify when Codex sign-off and green CI
  were observed, leaving merging to the user.
  [Addition](https://github.com/xuelongmu/x-skills/commit/405f9f8).

## 2026-05-06

- Added Codex `babysit` and `land` skill packages with a shared PR watcher.
  Changed Claude babysitting to report readiness without merging.
  [PR #2](https://github.com/xuelongmu/x-skills/pull/2).

## 2026-04-21

- Added idle-cycle tracking to stop Claude babysitting after three unchanged
  cycles. This historical stop condition was replaced by duration-aware
  continuous monitoring on 2026-09-04.
  [PR #1](https://github.com/xuelongmu/x-skills/pull/1).

## 2026-04-19

- Kept babysitting scoped to the original PR and directed unrelated review
  requests to separate work.
  [Change](https://github.com/xuelongmu/x-skills/commit/d7fd1e4).

## 2026-03-30

- Introduced the initial Claude commands for PR creation, Slack PR sharing,
  and PR babysitting. [Initial commit](https://github.com/xuelongmu/x-skills/commit/a9a7420).
