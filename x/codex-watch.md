---
name: codex-watch
description: Watch the current branch's PR for Codex's done-signal (a 👍 from chatgpt-codex-connector[bot] on the PR body) and push a notification once CI is green and Codex has signed off — so you can merge it yourself. Designed for /loop 5m /x:codex-watch. Never merges.
allowed-tools:
  - Bash
  - PushNotification
---

# Codex Watch: Ping me when Codex signs off

You watch the current branch's PR and send **one** push notification the moment Codex
has finished reviewing and CI is green — then you stop. You never merge; that's the
human's call.

This pairs with the native **CI monitoring** task (Auto-fix CI & address comments),
which does the *fixing*. Run this on a loop to get the "Codex is done — your move" ping
that the native panel doesn't surface:

```
/loop 5m /x:codex-watch
```

## The signal

When Codex finishes a review with no further comments, `chatgpt-codex-connector[bot]`
adds a `+1` (👍) reaction to the PR **body**. GitHub emits no webhook for reactions, so
you poll the reactions endpoint each cycle.

## Step 1: Identify the PR

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
N=$(gh pr view --json number -q .number 2>/dev/null) || { echo "No PR for this branch — nothing to watch."; exit 0; }
URL=$(gh pr view --json url -q .url)
HEAD=$(gh pr view --json headRefOid -q .headRefOid)
```

If no PR exists on the current branch, say so and stop.

## Step 2: Has Codex signed off?

A 👍 on the PR body from the connector bot:

```bash
APPROVED=$(gh api "repos/$REPO/issues/$N/reactions" \
  -q '[.[]|select(.user.login=="chatgpt-codex-connector[bot]" and .content=="+1")]|length')
```

## Step 3: Is CI green?

Nothing failing, pending, or cancelled (the autofix check included):

```bash
NOTOK=$(gh pr checks "$N" --json bucket \
  -q '[.[]|select(.bucket=="fail" or .bucket=="pending" or .bucket=="cancel")]|length' 2>/dev/null || echo 1)
```

## Step 4: Have I already pinged for this commit?

A `codex-ok:<head-sha>` label is the notify-once sentinel. Present for the **current**
head ⇒ already pinged; absent ⇒ re-armed (a new commit re-arms automatically, since its
sha won't match the old label):

```bash
ALREADY=$(gh pr view --json labels -q "[.labels[].name|select(.==\"codex-ok:$HEAD\")]|length")
```

## Step 5: Decide

- **If `APPROVED ≥ 1` AND `NOTOK == 0` AND `ALREADY == 0`** → it just became ready:
  1. Send a push with the **PushNotification** tool — title `PR #<N> approved by Codex`,
     body `CI green + Codex 👍 — ready to merge: <URL>`.
  2. Mark this head so the next cycles stay quiet, clearing any stale sentinel first:
     ```bash
     for L in $(gh pr view --json labels -q '.labels[].name|select(startswith("codex-ok:"))'); do
       gh pr edit "$N" --remove-label "$L" 2>/dev/null || true
     done
     gh label create "codex-ok:$HEAD" -c 2DA44E -f 2>/dev/null || true
     gh pr edit "$N" --add-label "codex-ok:$HEAD"
     ```
  3. Tell the user it's ready and print the merge command — but do **NOT** run it:
     ```
     gh pr merge <number> --squash --delete-branch
     ```
- **If already pinged** (`ALREADY ≥ 1`) → say so in one line and stop quietly.
- **Otherwise** → report the current state in one line and stop; the next loop cycle re-checks.

## Hard rules

- **Never merge.** This command only notifies. Merging stays a human action.
- **One ping per ready-commit.** The `codex-ok:<sha>` label guarantees it even though
  `/loop` restarts the session each cycle (in-memory state never survives).
- **Scope is the current branch's PR.** To watch another PR, switch to its branch first.

## Output format

Be concise:

```
PR #<number>: <one-line state>
Action: <pinged / already pinged / waiting>
```
