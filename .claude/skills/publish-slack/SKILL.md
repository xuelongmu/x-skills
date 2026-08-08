---
name: publish-slack
description: >-
  Post the current branch's PR to Slack with its Vercel preview link. Use when
  sharing the current PR in Slack with /publish-slack [channel]; the default
  channel is #zerogen.
allowed-tools:
  - Bash
  - mcp__claude_ai_Slack__slack_search_channels
  - mcp__claude_ai_Slack__slack_send_message_draft
  - mcp__claude_ai_Slack__slack_send_message
---

# Publish Slack: Share PR in Slack

Post the current branch's open PR to a Slack channel with a Vercel preview link.

**Arguments:** `$ARGUMENTS`
- First positional arg: Slack channel name (default: `zerogen`)

## Step 1: Get the PR

```
gh pr view --json number,title,url,body
```

If no PR exists on the current branch, stop and tell the user to run `/publish` first.

## Step 2: Wait for Vercel preview

Poll for the Vercel bot comment on the PR. Check every 10 seconds, up to 90 seconds:

```
gh api repos/{owner}/{repo}/issues/{number}/comments --jq '.[].body' | grep -i vercel
```

- Look for a comment from the Vercel bot containing a preview URL
- Extract the branch-level preview URL (pattern: `*-git-{branch-slug}-*.vercel.app`)
- If no Vercel comment appears after 90 seconds, use "deploying..." as placeholder

## Step 3: Post to Slack

1. Search for the target channel:
   - Use `slack_search_channels` with the channel name and `public_channel,private_channel` types
   - If not found, warn and stop

2. Compose the message:
   ```
   *PR: <title>* — <github_url>

   <2-3 bullet summary extracted from PR body>

   Preview: <vercel_branch_url or "deploying...">
   ```

3. Send as a draft via `slack_send_message_draft` so the user can review before it goes out.

## Output

```
Slack: draft posted to #<channel>
PR: <github_url>
Preview: <vercel_url or "deploying...">
```
