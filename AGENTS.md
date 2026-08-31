# Repository Instructions

Use the universal skill layout for behavior shared by Codex and Claude:

- Store genuinely host-neutral skills once under `.agents/skills/<skill>/`.
- Keep separate `.codex/skills/<skill>/` and `.claude/skills/<skill>/` sources when instructions, tools, invocation syntax, or lifecycle behavior differ meaningfully.
- Do not create checked-in host-directory links for canonical skills. Codex discovers `.agents/skills` directly; installers expose canonical skills to hosts such as Claude with symlinks or Windows junctions.
- Document `npx skills` as the only installation, refresh, migration, and removal path. Do not add manual junction, symlink, or copy recipes.
- For every new skill or behavior change, audit whether it is canonical or host-specific. Keep real variants behaviorally aligned where their capabilities overlap without flattening host-specific behavior.
- Update related templates, scripts, references, README inventory, installation lists, and `docs/skill-layout.md`; remove stale names and paths after moves or renames.
- Document unsupported hosts and intentional variants instead of silently omitting them.
- Run the layout audit and relevant behavioral checks.

When a user asks to install skills without specifying scope, ask whether they want a global or project-local installation.
