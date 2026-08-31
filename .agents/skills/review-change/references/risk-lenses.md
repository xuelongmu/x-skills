# Diff-Routed Risk Lenses

Select a lens only when changed files, symbols, dependencies, contracts, or
behavior activate it. Record the signal and inspect the relevant implementation,
callers, tests, and authority. Do not turn this list into a fixed checklist for
every change.

## Tenancy, authorization, and data access

Activate for tenant or account identifiers, authentication or authorization
guards, support/admin modes, queries, caches, object storage, search indexes,
exports, or user-controlled resource references.

- Trace identity and tenant scope from admission through every read, write,
  cache key, job, and provider call.
- Verify authorization at the authoritative server or domain seam, including
  direct callers that bypass the UI.
- Check support, impersonation, background, and retry paths against the same
  policy and audit requirements.

A data-access change that omits the tenant guard on a reachable path is a P0
when the concrete failure path exposes or mutates another tenant's data. Do not
report generic auth advice without that path.

## Schema and migrations

Activate for schema, migration, persistence format, index, constraint, backfill,
or ORM model changes.

- Check old/new application compatibility, safe defaults, nullability, locks,
  table rewrites, ordering, restartability, and rollback or forward recovery.
- Verify backfills are bounded, observable, idempotent when retried, and safe
  for mixed-version readers and writers.
- Treat generated migrations according to repository policy; do not recommend
  rewriting applied history for style.

## Billing and pricing

Activate for money, prices, credits, entitlements, quotas, invoices, ledgers,
settlement, or billing-provider events.

- Check exact units, currency, rounding, tax and effective-time semantics.
- Trace idempotency and uniqueness across retries, duplicate webhooks, partial
  failures, and reconciliation.
- Verify authorization and entitlement decisions cannot fail open or grant free
  fallback after an unknown outcome.

## Providers, queues, and retries

Activate for external providers, background jobs, queues, schedulers, webhooks,
timeouts, retry policy, or compensation.

- Check enqueue/commit and acknowledge/effect ordering, deduplication,
  idempotency keys, backoff, poison messages, and terminal handling.
- Preserve provider identity and correlation across retries; distinguish an
  unknown outcome from a confirmed failure.
- Verify cleanup and compensation do not duplicate or strand durable effects.

## Cross-service contracts

Activate for APIs, events, shared schemas, SDKs, public functions, service
boundaries, or producer/consumer changes.

- Compare canonical contract, producer, and affected consumers.
- Check compatibility, versioning, ordering, error semantics, optional fields,
  and rollout sequence.
- Identify behavior asserted only by one side's tests and missing from the
  contract or consumer verification.

Architectural rationale belongs in the repository ADR process; the contract
owns the resulting callable or serialized behavior.

## UI, accessibility, and evidence

Activate for components, routes, layouts, styles, interaction state, copy that
changes behavior, or user-visible error handling.

- Check loading, empty, error, disabled, focus, keyboard, screen-reader,
  responsive, and state-preservation behavior affected by the diff.
- Confirm server-side authorization remains authoritative; UI hiding is not an
  access control.
- Look for focused component or end-to-end coverage and trustworthy manual or
  browser evidence for the visible flow.

Missing evidence is reported under verification gaps unless the code itself
demonstrates a concrete failure. Product acceptance and release testing remain
with specialized QA workflows.

## Infrastructure, secrets, and portability

Activate for infrastructure as code, CI/CD, containers, deployment manifests,
cloud bindings, configuration, permissions, networking, or observability.

- Check secrets stay out of code, diffs, logs, artifacts, screenshots, and
  generated configuration.
- Verify least privilege, environment separation, failure and rollback paths,
  and that provider-specific assumptions are intentional rather than accidental.
- Check machine-local paths, ambient credentials, region assumptions, and
  undeclared services that break portability or reproducibility.

## Imported, vendored, generated, and dependency code

Activate for lockfiles, generated clients, migrations, code generation,
vendored sources, copied assets, or dependency changes.

- Establish provenance, version, license expectations, regeneration command,
  and whether the source or output is authoritative.
- Review dependency and lockfile behavior changes, transitive impact, and
  compatibility evidence.
- Do not spend review signal on generated-code style; review the generator,
  inputs, unsafe deltas, or divergence from reproducible output.

## Documentation, skills, and authority staleness

Activate for docs, instructions, skills, templates, runbooks, ADRs, contracts,
or code changes that invalidate them.

- Verify commands, links, paths, names, counts, ownership, and current behavior.
- Check the rule is in the correct authority and is updated or superseded rather
  than duplicated.
- Route durable architecture decisions to ADRs, procedures to runbooks,
  executable regressions to tests, current-state observations to dated system
  docs, and unimplemented work to issues.

A trivial documentation-only diff activates this lens for accuracy and
staleness. It does not activate generic tenancy, security, billing, provider,
or infrastructure review unless its actual content changes one of those
contracts or exposes sensitive data.

## Resulting-design and performance signals

Apply this focused lens when the diff changes a hot path, query shape,
pagination, caching, concurrency, memory ownership, or a module boundary.

- Inspect the resulting call graph and data volume rather than inferring cost
  from line count.
- Look for unbounded work, N+1 access, duplicated ownership, speculative
  abstraction, or complexity moved into callers.
- Require measurements for performance claims. Put unmeasured concern under
  residual risk unless a concrete input demonstrates failure.
