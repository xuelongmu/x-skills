# Repository Instructions

## Cross-platform parity

- Treat this as one portable skill collection. Implement every new skill and behavior change for both Codex and Claude Code under `.codex/skills/` and `.claude/skills/`, respectively.
- Keep the two implementations semantically aligned while adapting syntax and metadata to each host. If a host genuinely cannot support a capability, document the exception and reason in the README skill table instead of silently omitting it.
- Mirror a rule everywhere it is duplicated, including `SKILL.md`, referenced prompt templates, embedded prompt skeletons, scripts, and agent metadata. Search for the affected wording before considering a change complete.
- When adding, renaming, moving, or removing a skill, update both directory trees, frontmatter and agent metadata, cross-skill references, the README skill inventory, and every applicable Windows and macOS/Linux setup list. Search for stale names and paths.

## Repository conventions

- Keep global-install documentation link-based: Windows uses directory junctions and macOS/Linux uses symbolic links. Keep project-local installation copy-based, create destination directories explicitly, and note that copies must be reinstalled to receive updates.
- Preserve documented dependencies. In particular, Codex `babysit` uses `land/land_watch.py`, so Codex install instructions must include `land` whenever they include `babysit`.
- Preserve workflow boundaries: `babysit` must never merge, enable auto-merge, or delete branches; only `land` merges. `publish` opens a ready-for-review PR unless the user explicitly requests a draft.
- Scope repository and project commands explicitly when a workflow may run outside the target checkout; do not rely on ambient CLI context.

## Validation

- Review the complete diff and compare corresponding Codex and Claude files for behavioral parity.
- Run the most relevant available checks for changed scripts or skills, and verify README examples and install commands when their paths or names change.
