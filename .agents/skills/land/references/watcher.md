# PR watcher contract

Resolve the active `land` directory from the loaded skill path. The
[bundled helper](../scripts/land_watch.py) runs with
`python <land-directory>/scripts/land_watch.py` (or `python3`) from the PR
repository, with `LAND_WATCH_PR` set to the selected PR URL. The helper requires
Python and an authenticated `gh` for that host. Use the host's asynchronous
execution or bounded wait facility so monitoring does not prevent communication.

| Setting | Default | Accepted seconds |
| --- | --- | --- |
| `LAND_WATCH_POLL_SECONDS` | 30 | 30–300 |
| `LAND_WATCH_FEEDBACK_GRACE_SECONDS` | 900 | 30–86400 |

Honor an explicit feedback-wait policy; otherwise retain the helper's default.
Checks and feedback are monitored independently. Even if no checks appear, the
helper waits through the grace period and continues polling for checks. Codex
feedback need not arrive unless repository policy requires that review.

| Exit | Action |
| --- | --- |
| 0 | Read `LAND_WATCH_VALIDATED_HEAD=<sha>`; assess repository approval gates. |
| 2 | Assess and handle outstanding feedback. |
| 3 | Diagnose failed checks. |
| 4 | Fetch and inspect the changed PR head; refresh applicable validation. |
| 5 | Synchronize the verified base or resolve conflicts. |
| 6 | Refresh terminal state; stop on merge or closure. |

Restart after remediation. Unknown exits, API failures, or absent success output
are not readiness. Before success the helper repeatedly refreshes feedback, CI,
head, and merge state until the feedback and PR snapshots converge. Retain this
protection and pass its validated head to the merge operation; a later head needs
new validation.

The helper is a mechanical gate, not a replacement for judgment: acknowledgements
must reflect actual fixes or justified disposition, and required repository
approvals must be checked separately. Connector-only monitoring must preserve the
same grace, feedback, CI, terminal-state, and expected-head guarantees.
