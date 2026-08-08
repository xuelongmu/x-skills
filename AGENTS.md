# Repository Instructions

Keep Codex and Claude skill implementations in sync. For every new skill or behavior change:

- Update `.codex/skills/` and `.claude/skills/`, adapting only host-specific syntax and metadata.
- Update related templates, scripts, references, and README inventory and installation lists; remove stale names and paths after renames.
- Document unsupported host exceptions in the README instead of silently omitting them.
- Compare both implementations for behavioral parity and run relevant checks.
