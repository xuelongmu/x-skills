# Share a PR in Slack

Use this only when sharing is requested. Read the selected PR's title, URL,
body, and head branch. Resolve the requested channel with the authenticated
Slack capability, following its current schema and discovery instructions.
Ask for a channel only if it cannot be established from the request or context.

Draft by default; send only when sending is explicitly authorized. If drafts are
unavailable, return the composed message instead of silently sending. Sharing
does not authorize merging.

Include the PR link and a short description of its impact. If a deployment
preview is relevant, read the PR's top-level issue comments for the deployment
provider's matching branch preview. For Vercel, use the selected PR head rather
than the current checkout and look for `*-git-{branch-slug}-*.vercel.app`.
If still deploying, say so instead of inventing a URL. Poll briefly only when
waiting for the preview is part of the request.
