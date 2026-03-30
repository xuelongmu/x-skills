---
name: pr
description: Create a PR from current branch with auto-generated title, summary, and test plan. Pure GitHub — no Slack.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
---

# PR: Create Pull Request

Create a PR from the current branch. GitHub only — use `/slack-pr` afterward to share.

## Step 1: Gather branch context

Run these commands to understand the current state:

```
git status
git log master...HEAD --oneline
git diff master...HEAD --stat
git branch -vv
```

- If working tree is dirty (uncommitted changes), **warn the user** and ask whether to proceed or stop.
- If there are no commits ahead of master, stop — nothing to PR.
- Note the base branch is `master`.

## Step 2: Create the PR

1. Push the branch to remote if needed:
   ```
   git push -u origin HEAD
   ```

2. Generate a PR title and body from the commit history:
   - Title: concise, under 70 characters, summarizing the changeset
   - Body: 2-4 summary bullets, a test plan section, and the footer

3. Create the PR:
   ```
   gh pr create --title "<title>" --body "$(cat <<'EOF'
   ## Summary
   - <bullet 1>
   - <bullet 2>
   - <bullet 3>

   ## Test plan
   - [ ] <test step 1>
   - [ ] <test step 2>

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

4. Capture the PR URL and number from the output.

## Output

```
PR #<number>: <title>
URL: <github_url>

Tip: run /slack-pr to share this in Slack with a Vercel preview link.
```
