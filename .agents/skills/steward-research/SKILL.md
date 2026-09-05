---
name: steward-research
description: Make research work reproducible and ready for handoff through provenance, experiment records, artifact separation, and reusable tooling.
---

# Steward research

Preserve the user's data and unfinished work while producing the requested audit,
organization, or handoff. An audit is inspect-only. Do not infer permission to
rerun costly experiments, delete artifacts, stop processes, or upload data.

## Reproducible evidence

Use existing research records and conventions. Record the details needed to
reproduce or interpret each meaningful result:

- objective, status, and next action;
- input identity and provenance, access or license constraints;
- code revision, environment, configuration, seeds, and data split;
- exact command, reused artifacts or caches, and the variable changed;
- results with units, diagnostics, uncertainty, and artifact locations.

Distinguish observations, inferences, and proxies. Preserve negative results and
append corrections when they affect later interpretation. Methodology changes
made after seeing results are new experiments.

For ablations, keep claimed controls fixed. A successful exit is not scientific
evidence: inspect relevant diagnostics and representative output, and label
partial, invalid, or unverified results accurately.

## Source and artifacts

Keep reusable source, configuration, and documentation distinct from datasets,
weights, caches, checkpoints, and generated media. Follow repository policy for
canonical fixtures; otherwise keep artifacts in ignored scratch space and record
their locations. Do not commit credentials, private machine paths, or restricted
assets. Upload only within the user's authorization and applicable data policy.

Promote a helper when it is reusable: use explicit inputs, configurable paths,
input validation before costly work, and a manifest for data transformations.
Preserve overwrite protections. Test fragile transforms at their behavioral seam.

## Handoff

Verify the evidence needed for the requested handoff without rerunning the full
research program by default. Distinguish configuration checks, smoke tests, and
actual experiment reproduction.

Report reproducible results, the intended contribution, excluded local work,
pending experiments, and next action. Use the repository's publishing workflow
only when publication is requested.
