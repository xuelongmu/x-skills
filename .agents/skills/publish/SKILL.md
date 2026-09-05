---
name: publish
description: Commit and publish intended local changes to a ready-for-review GitHub PR. Use when asked to push work, open a PR, or publish an update to an existing PR.
---

# Publish changes

Publish the intended change and return the PR URL with a concise account of
validation and remaining limitations. Create a ready-for-review PR unless the
user requests a draft; preserve an existing PR's readiness state unless changing
it is requested. Publication does not include merging or ongoing monitoring.

Use the publication section of the shared
[PR workflow](../land/references/pr-workflow.md), owned by the sibling `land`
skill. Install `land` alongside `publish` in the same scope; the installer does
not resolve this dependency automatically. Resolve the link relative to the
active skill directory. If the dependency is missing, report it and complete
publication using the host's available workflow when possible.

An existing PR is an update target when the user's request and branch scope
establish that intent. Ask only when the target or included work is materially
ambiguous. Preserve unrelated changes and collaborator commits.
