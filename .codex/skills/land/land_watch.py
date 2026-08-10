#!/usr/bin/env python3
import asyncio
import json
import os
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

DEFAULT_POLL_SECONDS = 30
MIN_POLL_SECONDS = 30
MAX_POLL_SECONDS = 300
POLL_SECONDS_ENV = "LAND_WATCH_POLL_SECONDS"


def parse_poll_seconds(raw_value: str | None) -> int:
    if raw_value is None:
        return DEFAULT_POLL_SECONDS
    try:
        poll_seconds = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(
            f"{POLL_SECONDS_ENV} must be an integer from {MIN_POLL_SECONDS} "
            f"to {MAX_POLL_SECONDS} seconds",
        ) from exc
    if poll_seconds < MIN_POLL_SECONDS:
        raise RuntimeError(
            f"{POLL_SECONDS_ENV} must be at least {MIN_POLL_SECONDS} seconds",
        )
    if poll_seconds > MAX_POLL_SECONDS:
        raise RuntimeError(
            f"{POLL_SECONDS_ENV} must be at most {MAX_POLL_SECONDS} seconds",
        )
    return poll_seconds


POLL_SECONDS = parse_poll_seconds(os.environ.get(POLL_SECONDS_ENV))
CHECKS_APPEAR_TIMEOUT_SECONDS = 120
FEEDBACK_GRACE_SECONDS = 600
CODEX_BOT_LOGINS = {
    "chatgpt-codex-connector",
    "chatgpt-codex-connector[bot]",
    "codex-gc-app[bot]",
    "app/codex-gc-app",
}
# Bridge authors are trusted only after the comment body or parent review
# proves the comment is Codex feedback.
CODEX_REVIEW_BRIDGE_LOGINS = {
    "github-actions[bot]",
}
MAX_GH_RETRIES = 5
BASE_GH_BACKOFF_SECONDS = 2


def monotonic_seconds() -> float:
    return asyncio.get_running_loop().time()


async def sleep(seconds: int | float) -> None:
    await asyncio.sleep(seconds)


@dataclass
class PrInfo:
    number: int
    node_id: str
    hostname: str
    owner: str
    repo: str
    url: str
    head_sha: str
    mergeable: str | None
    merge_state: str | None


class RateLimitError(RuntimeError):
    pass


class WatchExit(Exception):
    def __init__(self, code: int):
        super().__init__(code)
        self.code = code


def get_repository_from_pr_url(url: str) -> tuple[str, str, str]:
    parsed_url = urlsplit(url)
    path_parts = parsed_url.path.strip("/").split("/")
    if (
        not parsed_url.hostname
        or parsed_url.scheme not in ("http", "https")
        or len(path_parts) != 4
        or path_parts[2] != "pull"
        or not path_parts[3].isdigit()
    ):
        raise RuntimeError(f"Unexpected pull request URL: {url}")
    return parsed_url.netloc, path_parts[0], path_parts[1]


def is_rate_limit_error(error: str) -> bool:
    return "HTTP 429" in error or "rate limit" in error.lower()


async def run_gh(*args: str, api_host: str | None = None) -> str:
    max_delay = BASE_GH_BACKOFF_SECONDS * (2 ** (MAX_GH_RETRIES - 1))
    delay_seconds = BASE_GH_BACKOFF_SECONDS
    last_error = "gh command failed"
    process_env = None
    if api_host:
        process_env = os.environ.copy()
        process_env["GH_HOST"] = api_host
    for attempt in range(1, MAX_GH_RETRIES + 1):
        proc = await asyncio.create_subprocess_exec(
            "gh",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=process_env,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            return stdout.decode()
        error = stderr.decode().strip() or "gh command failed"
        if not is_rate_limit_error(error):
            raise RuntimeError(error)
        last_error = error
        if attempt >= MAX_GH_RETRIES:
            break
        jitter = random.uniform(0, delay_seconds)
        await sleep(min(delay_seconds + jitter, max_delay))
        delay_seconds = min(delay_seconds * 2, max_delay)
    raise RateLimitError(last_error)


async def get_pr_info() -> PrInfo:
    data = await run_gh(
        "pr",
        "view",
        "--json",
        "number,id,url,headRefOid,mergeable,mergeStateStatus",
    )
    parsed = json.loads(data)
    hostname, owner, repo = get_repository_from_pr_url(parsed["url"])
    return PrInfo(
        number=parsed["number"],
        node_id=parsed["id"],
        hostname=hostname,
        owner=owner,
        repo=repo,
        url=parsed["url"],
        head_sha=parsed["headRefOid"],
        mergeable=parsed.get("mergeable"),
        merge_state=parsed.get("mergeStateStatus"),
    )


async def get_paginated_list(
    hostname: str,
    endpoint: str,
) -> list[dict[str, Any]]:
    page = 1
    items: list[dict[str, Any]] = []
    while True:
        data = await run_gh(
            "api",
            "--method",
            "GET",
            endpoint,
            "-f",
            "per_page=100",
            "-f",
            f"page={page}",
            api_host=hostname,
        )
        batch = json.loads(data)
        if not batch:
            break
        items.extend(batch)
        page += 1
    return items


async def get_issue_comments(
    pr_number: int,
    hostname: str,
    owner: str,
    repo: str,
) -> list[dict[str, Any]]:
    return await get_paginated_list(
        hostname,
        f"repos/{owner}/{repo}/issues/{pr_number}/comments",
    )


async def get_review_comments(
    pr_number: int,
    hostname: str,
    owner: str,
    repo: str,
) -> list[dict[str, Any]]:
    return await get_paginated_list(
        hostname,
        f"repos/{owner}/{repo}/pulls/{pr_number}/comments",
    )


async def get_reviews(
    pr_number: int,
    hostname: str,
    owner: str,
    repo: str,
) -> list[dict[str, Any]]:
    page = 1
    reviews: list[dict[str, Any]] = []
    while True:
        data = await run_gh(
            "api",
            "--method",
            "GET",
            f"repos/{owner}/{repo}/pulls/{pr_number}/reviews",
            "-f",
            "per_page=100",
            "-f",
            f"page={page}",
            api_host=hostname,
        )
        batch = json.loads(data)
        if not batch:
            break
        reviews.extend(batch)
        page += 1
    return reviews


async def get_authenticated_user_login(hostname: str) -> str | None:
    data = await run_gh(
        "api",
        "user",
        "--jq",
        ".login",
        api_host=hostname,
    )
    login = data.strip()
    return login or None


async def get_active_review_thread_comment_node_ids(
    pull_request_id: str,
    hostname: str,
) -> set[str]:
    cursor: str | None = None
    active_comment_ids: set[str] = set()
    while True:
        args = [
            "api",
            "graphql",
            "-f",
            f"query={REVIEW_THREADS_QUERY}",
            "-F",
            f"pullRequestId={pull_request_id}",
        ]
        if cursor:
            args.extend(["-F", f"cursor={cursor}"])
        data = await run_gh(*args, api_host=hostname)
        payload = json.loads(data)
        threads = payload["data"]["node"]["reviewThreads"]
        for thread in threads.get("nodes") or []:
            if thread.get("isResolved") or thread.get("isOutdated"):
                continue
            active_comment_ids.update(
                await get_review_thread_comment_node_ids(thread, hostname),
            )
        page_info = threads["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]
    return active_comment_ids


async def get_review_thread_comment_node_ids(
    thread: dict[str, Any],
    hostname: str,
) -> set[str]:
    thread_id = thread.get("id")
    comments = thread.get("comments") or {}
    comment_ids = comment_node_ids(comments.get("nodes") or [])
    page_info = comments.get("pageInfo") or {}
    cursor = page_info.get("endCursor") if page_info.get("hasNextPage") else None
    while thread_id and cursor:
        data = await run_gh(
            "api",
            "graphql",
            "-f",
            f"query={REVIEW_THREAD_COMMENTS_QUERY}",
            "-F",
            f"threadId={thread_id}",
            "-F",
            f"cursor={cursor}",
            api_host=hostname,
        )
        payload = json.loads(data)
        comments_page = payload["data"]["node"]["comments"]
        comment_ids.update(comment_node_ids(comments_page.get("nodes") or []))
        page_info = comments_page["pageInfo"]
        cursor = page_info["endCursor"] if page_info["hasNextPage"] else None
    return comment_ids


def comment_node_ids(comments: list[dict[str, Any]]) -> set[str]:
    return {
        comment["id"]
        for comment in comments
        if comment.get("id")
    }


async def get_check_runs(
    head_sha: str,
    hostname: str,
    owner: str,
    repo: str,
) -> list[dict[str, Any]]:
    endpoint = f"repos/{owner}/{repo}/commits/{head_sha}/check-runs"
    page = 1
    check_runs: list[dict[str, Any]] = []
    while True:
        data = await run_gh(
            *check_runs_page_args(endpoint, page),
            api_host=hostname,
        )
        payload = json.loads(data)
        batch = payload.get("check_runs", [])
        if not batch:
            break
        check_runs.extend(batch)
        total_count = payload.get("total_count")
        if total_count is not None and len(check_runs) >= total_count:
            break
        page += 1
    return check_runs


def check_runs_page_args(
    endpoint: str,
    page: int,
) -> list[str]:
    return [
        "api",
        "--method",
        "GET",
        endpoint,
        "-f",
        "per_page=100",
        "-f",
        f"page={page}",
    ]


async def get_commit_status_checks(
    head_sha: str,
    hostname: str,
    owner: str,
    repo: str,
) -> list[dict[str, Any]]:
    data = await run_gh(
        "api",
        "--method",
        "GET",
        "--paginate",
        "--slurp",
        f"repos/{owner}/{repo}/commits/{head_sha}/statuses",
        "-f",
        "per_page=100",
        api_host=hostname,
    )
    pages = json.loads(data)
    statuses = [
        status
        for page in pages
        for status in page
    ]
    return [
        normalize_commit_status(status)
        for status in statuses
    ]


async def get_ci_results(
    head_sha: str,
    hostname: str,
    owner: str,
    repo: str,
) -> list[dict[str, Any]]:
    check_runs = await get_check_runs(head_sha, hostname, owner, repo)
    commit_statuses = await get_commit_status_checks(
        head_sha,
        hostname,
        owner,
        repo,
    )
    return check_runs + commit_statuses


def normalize_commit_status(status: dict[str, Any]) -> dict[str, Any]:
    state = status.get("state")
    completed = state != "pending"
    creator = status.get("creator") or {}
    creator_login = creator.get("login") or "commit-status"
    return {
        "name": status.get("context") or "legacy-status",
        "status": "completed" if completed else "in_progress",
        "conclusion": "success" if state == "success" else state,
        "started_at": status.get("created_at"),
        "completed_at": status.get("updated_at") if completed else None,
        "app": {
            "id": "commit-status",
            "name": creator_login,
        },
    }


def parse_time(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
CODEX_REVIEW_HEADING_RE = re.compile(
    r"^#{2,3}\s*(?:[^\w#]+\s*)?Codex Review\b",
    re.IGNORECASE,
)
REVIEW_THREADS_QUERY = """
query($pullRequestId: ID!, $cursor: String) {
  node(id: $pullRequestId) {
    ... on PullRequest {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          comments(first: 100) {
            pageInfo { hasNextPage endCursor }
            nodes { id }
          }
        }
      }
    }
  }
}
"""
REVIEW_THREAD_COMMENTS_QUERY = """
query($threadId: ID!, $cursor: String) {
  node(id: $threadId) {
    ... on PullRequestReviewThread {
      comments(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { id }
      }
    }
  }
}
"""


def sanitize_terminal_output(value: str) -> str:
    sanitized = CONTROL_CHARS_RE.sub("", value)
    encoding = sys.stdout.encoding
    if encoding:
        sanitized = sanitized.encode(encoding, errors="replace").decode(encoding)
    return sanitized


def check_timestamp(check: dict[str, Any]) -> datetime | None:
    for key in ("completed_at", "started_at", "run_started_at", "created_at"):
        value = check.get(key)
        if value:
            return parse_time(value)
    return None


def dedupe_check_runs(check_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for check in check_runs:
        key = check_run_key(check)
        timestamp = check_timestamp(check)
        if key not in latest_by_key:
            latest_by_key[key] = check
            continue
        existing = latest_by_key[key]
        existing_timestamp = check_timestamp(existing)
        if timestamp is None:
            continue
        if existing_timestamp is None or timestamp > existing_timestamp:
            latest_by_key[key] = check
    return list(latest_by_key.values())


def check_run_key(check: dict[str, Any]) -> tuple[str, str]:
    app = check.get("app") or {}
    app_key = app.get("id") or app.get("slug") or app.get("name") or "unknown-app"
    name = check.get("name") or "unknown"
    return str(app_key), str(name)


def summarize_checks(check_runs: list[dict[str, Any]]) -> tuple[bool, bool, list[str]]:
    if not check_runs:
        return True, False, ["no checks reported"]
    check_runs = dedupe_check_runs(check_runs)
    pending = False
    failed = False
    failures: list[str] = []
    for check in check_runs:
        status = check.get("status")
        conclusion = check.get("conclusion")
        name = check.get("name", "unknown")
        if status != "completed":
            pending = True
            continue
        if conclusion not in ("success", "skipped", "neutral"):
            failed = True
            failures.append(f"{name}: {conclusion}")
    return pending, failed, failures


def latest_review_request_at(comments: list[dict[str, Any]]) -> datetime | None:
    latest: datetime | None = None
    for comment in comments:
        if is_codex_bot_user(comment.get("user", {})):
            continue
        body = comment.get("body") or ""
        if "@codex review" not in body:
            continue
        timestamp = comment_time(comment)
        if timestamp is None:
            continue
        if latest is None or timestamp > latest:
            latest = timestamp
    return latest


def filter_codex_comments(
    comments: list[dict[str, Any]],
    review_requested_at: datetime | None,
    codex_review_ids: set[int] | None = None,
    trusted_ack_logins: set[str] | None = None,
) -> list[dict[str, Any]]:
    if codex_review_ids is None:
        codex_review_ids = set()
    if trusted_ack_logins is None:
        trusted_ack_logins = set()
    latest_codex_reply = latest_codex_reply_by_thread(
        comments,
        trusted_ack_logins,
    )
    latest_issue_ack = latest_codex_issue_reply_time(
        comments,
        trusted_ack_logins,
    )
    codex_comments = [
        c
        for c in comments
        if is_codex_feedback_comment(c, codex_review_ids)
    ]
    filtered: list[dict[str, Any]] = []
    for comment in codex_comments:
        created_time = comment_time(comment)
        if created_time is None:
            continue
        if review_requested_at is not None and created_time <= review_requested_at:
            continue
        is_threaded = bool(
            comment.get("in_reply_to_id") or comment.get("pull_request_review_id")
        )
        if not is_threaded:
            if latest_issue_ack is not None and created_time <= latest_issue_ack:
                continue
        else:
            thread_root = thread_root_id(comment)
            last_reply = None
            if thread_root is not None:
                last_reply = latest_codex_reply.get(thread_root)
            if last_reply and last_reply > created_time:
                continue
        filtered.append(comment)
    return filtered


def filter_active_review_thread_comments(
    comments: list[dict[str, Any]],
    active_comment_node_ids: set[str],
) -> list[dict[str, Any]]:
    return [
        comment
        for comment in comments
        if comment.get("node_id") in active_comment_node_ids
    ]


def is_codex_bot_user(user: dict[str, Any]) -> bool:
    login = user.get("login") or ""
    return login in CODEX_BOT_LOGINS


def is_codex_bridge_bot_user(user: dict[str, Any]) -> bool:
    login = user.get("login") or ""
    return login in CODEX_REVIEW_BRIDGE_LOGINS


def is_bot_user(user: dict[str, Any]) -> bool:
    login = user.get("login") or ""
    if is_codex_bot_user(user):
        return True
    if user.get("type") == "Bot":
        return True
    return login.endswith("[bot]")


def is_codex_reply_body(body: str) -> bool:
    return body.startswith("[codex]")


def is_codex_review_body(body: str) -> bool:
    for line in body.strip().splitlines()[:5]:
        if CODEX_REVIEW_HEADING_RE.match(line.strip()):
            return True
    return False


def is_codex_feedback_comment(
    comment: dict[str, Any],
    codex_review_ids: set[int],
) -> bool:
    review_id = comment.get("pull_request_review_id")
    if review_id in codex_review_ids:
        return True
    user = comment.get("user", {})
    if is_codex_bot_user(user):
        return True
    if is_codex_bridge_bot_user(user):
        body = (comment.get("body") or "").strip()
        return is_codex_reply_body(body) or is_codex_review_body(body)
    return False


def is_trusted_codex_ack_comment(
    comment: dict[str, Any],
    trusted_ack_logins: set[str],
) -> bool:
    body = (comment.get("body") or "").strip()
    if not is_codex_reply_body(body):
        return False
    if is_codex_feedback_comment(comment, set()):
        return True
    login = comment.get("user", {}).get("login")
    return bool(login and login in trusted_ack_logins)


def is_codex_review_issue_comment(comment: dict[str, Any]) -> bool:
    body = (comment.get("body") or "").strip()
    return is_codex_review_body(body) and is_codex_feedback_comment(comment, set())


def latest_codex_issue_reply_time(
    comments: list[dict[str, Any]],
    trusted_ack_logins: set[str],
) -> datetime | None:
    latest: datetime | None = None
    for comment in comments:
        if not is_trusted_codex_ack_comment(comment, trusted_ack_logins):
            continue
        created_time = comment_time(comment)
        if created_time is None:
            continue
        if latest is None or created_time > latest:
            latest = created_time
    return latest


def filter_human_issue_comments(
    comments: list[dict[str, Any]],
    trusted_ack_logins: set[str],
) -> list[dict[str, Any]]:
    latest_ack = latest_codex_issue_reply_time(comments, trusted_ack_logins)
    filtered: list[dict[str, Any]] = []
    for comment in comments:
        if is_bot_user(comment.get("user", {})):
            continue
        body = (comment.get("body") or "").strip()
        if "@codex review" in body:
            continue
        created_time = comment_time(comment)
        if (
            latest_ack is not None
            and created_time is not None
            and created_time <= latest_ack
        ):
            continue
        filtered.append(comment)
    return filtered


def filter_codex_review_issue_comments(
    comments: list[dict[str, Any]],
    trusted_ack_logins: set[str],
) -> list[dict[str, Any]]:
    latest_ack = latest_codex_issue_reply_time(comments, trusted_ack_logins)
    filtered: list[dict[str, Any]] = []
    for comment in comments:
        if not is_codex_review_issue_comment(comment):
            continue
        created_time = comment_time(comment)
        if (
            latest_ack is not None
            and created_time is not None
            and created_time <= latest_ack
        ):
            continue
        filtered.append(comment)
    return filtered


def thread_root_id(comment: dict[str, Any]) -> int | None:
    return comment.get("in_reply_to_id") or comment.get("id")


def comment_time(comment: dict[str, Any]) -> datetime | None:
    timestamp = comment.get("created_at") or comment.get("createdAt")
    if not timestamp:
        return None
    return parse_time(timestamp)


def latest_codex_reply_by_thread(
    comments: list[dict[str, Any]],
    trusted_ack_logins: set[str],
) -> dict[int, datetime]:
    latest: dict[int, datetime] = {}
    for comment in comments:
        if not is_trusted_codex_ack_comment(comment, trusted_ack_logins):
            continue
        thread_root = thread_root_id(comment)
        created_time = comment_time(comment)
        if thread_root is None or created_time is None:
            continue
        existing = latest.get(thread_root)
        if existing is None or created_time > existing:
            latest[thread_root] = created_time
    return latest


def filter_human_review_comments(
    comments: list[dict[str, Any]],
    trusted_ack_logins: set[str],
) -> list[dict[str, Any]]:
    latest_codex_reply = latest_codex_reply_by_thread(comments, trusted_ack_logins)
    filtered: list[dict[str, Any]] = []
    for comment in comments:
        if is_bot_user(comment.get("user", {})):
            continue
        thread_root = thread_root_id(comment)
        created_time = comment_time(comment)
        last_codex_reply = None
        if thread_root is not None:
            last_codex_reply = latest_codex_reply.get(thread_root)
        if last_codex_reply and created_time and created_time <= last_codex_reply:
            continue
        filtered.append(comment)
    return filtered


def is_blocking_review(
    review: dict[str, Any],
    review_requested_at: datetime | None,
    latest_ack: datetime | None,
) -> bool:
    created_at = review.get("submitted_at") or review.get("created_at")
    if not created_at:
        return False
    created_time = parse_time(created_at)
    codex_review = is_codex_review(review)
    if (
        codex_review
        and review_requested_at is not None
        and created_time <= review_requested_at
    ):
        return False
    body = (review.get("body") or "").strip()
    state = review.get("state")
    if codex_review:
        return state == "CHANGES_REQUESTED"
    if state in ("APPROVED", "DISMISSED"):
        return False
    if state == "CHANGES_REQUESTED":
        return True
    if state == "COMMENTED":
        if latest_ack is not None and created_time <= latest_ack:
            return False
        return bool(body)
    if body:
        return True
    if state:
        return True
    return False


def is_codex_review(review: dict[str, Any]) -> bool:
    user = review.get("user", {})
    if is_codex_bot_user(user):
        return True
    if not is_codex_bridge_bot_user(user):
        return False
    body = (review.get("body") or "").strip()
    return is_codex_reply_body(body) or is_codex_review_body(body)


def codex_review_ids_after_request(
    reviews: list[dict[str, Any]],
    review_requested_at: datetime | None,
) -> set[int]:
    ids: set[int] = set()
    for review in reviews:
        if not is_codex_review(review):
            continue
        timestamp = review_timestamp(review)
        if (
            review_requested_at is not None
            and timestamp is not None
            and timestamp <= review_requested_at
        ):
            continue
        review_id = review.get("id")
        if isinstance(review_id, int):
            ids.add(review_id)
    return ids


def review_timestamp(review: dict[str, Any]) -> datetime | None:
    created_at = review.get("submitted_at") or review.get("created_at")
    if not created_at:
        return None
    return parse_time(created_at)


def dedupe_reviews(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reviews_by_user: dict[str, list[dict[str, Any]]] = {}
    for review in reviews:
        user_login = review.get("user", {}).get("login")
        if not user_login:
            continue
        reviews_by_user.setdefault(user_login, []).append(review)

    effective_reviews: list[dict[str, Any]] = []
    for user_reviews in reviews_by_user.values():
        ordered = sorted(
            user_reviews,
            key=lambda review: review_timestamp(review)
            or datetime.min.replace(tzinfo=timezone.utc),
        )
        latest = ordered[-1]
        outstanding_change_request: dict[str, Any] | None = None
        latest_comment: dict[str, Any] | None = None
        latest_terminal: dict[str, Any] | None = None
        for review in ordered:
            state = review.get("state")
            if state == "CHANGES_REQUESTED":
                outstanding_change_request = review
                latest_comment = None
                continue
            if state in ("APPROVED", "DISMISSED"):
                outstanding_change_request = None
                latest_comment = None
                latest_terminal = review
                continue
            if state == "COMMENTED":
                latest_comment = review
                continue
            latest_terminal = review
        if outstanding_change_request is not None:
            effective_reviews.append(outstanding_change_request)
        elif latest_comment is not None:
            effective_reviews.append(latest_comment)
        elif latest_terminal is not None:
            effective_reviews.append(latest_terminal)
        else:
            effective_reviews.append(latest)
    return effective_reviews


def filter_blocking_reviews(
    reviews: list[dict[str, Any]],
    review_requested_at: datetime | None,
    latest_ack: datetime | None,
) -> list[dict[str, Any]]:
    return [
        review
        for review in dedupe_reviews(reviews)
        if is_blocking_review(review, review_requested_at, latest_ack)
    ]


def is_merge_conflicting(pr: PrInfo) -> bool:
    return pr.mergeable == "CONFLICTING" or pr.merge_state in ("BEHIND", "DIRTY")


async def validate_final_readiness(
    expected_head_sha: str,
    hostname: str,
    owner: str,
    repo: str,
    checks_done: asyncio.Event,
) -> bool:
    check_runs = await get_ci_results(expected_head_sha, hostname, owner, repo)
    if check_runs:
        pending, failed, failures = summarize_checks(check_runs)
        if failed:
            print("Checks failed during final readiness validation:")
            for failure in failures:
                print(f"- {failure}")
            raise WatchExit(3)
        if pending:
            checks_done.clear()
            print(
                "Checks are pending during final readiness validation; "
                "restarting feedback grace after they pass.",
                flush=True,
            )
            return False

    current_pr = await get_pr_info()
    if is_merge_conflicting(current_pr):
        print(
            "PR is behind, conflicting, or dirty during final readiness validation.",
        )
        raise WatchExit(5)
    if current_pr.head_sha != expected_head_sha:
        print("PR head updated during final readiness validation.")
        raise WatchExit(4)
    return True


async def fetch_review_context(
    pr_number: int,
    pull_request_id: str,
    hostname: str,
    owner: str,
    repo: str,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    datetime | None,
    set[str],
    set[str],
]:
    issue_comments = await get_issue_comments(pr_number, hostname, owner, repo)
    review_request_at = latest_review_request_at(issue_comments)
    review_comments = await get_review_comments(
        pr_number,
        hostname,
        owner,
        repo,
    )
    reviews = await get_reviews(pr_number, hostname, owner, repo)
    active_review_comment_node_ids = await get_active_review_thread_comment_node_ids(
        pull_request_id,
        hostname,
    )
    authenticated_login = await get_authenticated_user_login(hostname)
    trusted_ack_logins = {authenticated_login} if authenticated_login else set()
    return (
        issue_comments,
        review_comments,
        reviews,
        review_request_at,
        active_review_comment_node_ids,
        trusted_ack_logins,
    )


def raise_on_human_feedback(
    issue_comments: list[dict[str, Any]],
    review_comments: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    review_request_at: datetime | None,
    trusted_ack_logins: set[str],
) -> None:
    human_issue_comments = filter_human_issue_comments(
        issue_comments,
        trusted_ack_logins,
    )
    codex_review_comments = filter_codex_review_issue_comments(
        issue_comments,
        trusted_ack_logins,
    )
    human_review_comments = filter_human_review_comments(
        review_comments,
        trusted_ack_logins,
    )
    if human_issue_comments or human_review_comments or codex_review_comments:
        print("Review comments detected. Address before merge.")
        print(
            "Reminder: decide whether feedback stays in scope; defer if needed "
            "and note in your root-level update.",
        )
        raise WatchExit(2)
    latest_ack = latest_codex_issue_reply_time(issue_comments, trusted_ack_logins)
    blocking_reviews = filter_blocking_reviews(
        reviews,
        review_request_at,
        latest_ack,
    )
    if blocking_reviews:
        print("Review states/comments detected. Address before merge.")
        print(
            "Reminder: keep PR title/description aligned with the full scope "
            "when changes expand.",
        )
        raise WatchExit(2)


async def wait_for_codex(
    pr_number: int,
    pull_request_id: str,
    hostname: str,
    owner: str,
    repo: str,
    head_sha: str,
    checks_done: asyncio.Event,
) -> None:
    print("Waiting for review feedback...", flush=True)
    feedback_grace_started_at: float | None = None
    while True:
        (
            issue_comments,
            review_comments,
            reviews,
            review_request_at,
            active_review_comment_node_ids,
            trusted_ack_logins,
        ) = await fetch_review_context(
            pr_number,
            pull_request_id,
            hostname,
            owner,
            repo,
        )
        active_review_comments = filter_active_review_thread_comments(
            review_comments,
            active_review_comment_node_ids,
        )
        codex_review_ids = codex_review_ids_after_request(
            reviews,
            review_request_at,
        )
        bot_issue_comments = filter_codex_comments(
            issue_comments,
            review_request_at,
            trusted_ack_logins=trusted_ack_logins,
        )
        bot_review_comments = filter_codex_comments(
            active_review_comments,
            review_request_at,
            codex_review_ids,
            trusted_ack_logins,
        )
        bot_comments = bot_issue_comments + bot_review_comments
        raise_on_human_feedback(
            issue_comments,
            active_review_comments,
            reviews,
            review_request_at,
            trusted_ack_logins,
        )
        if bot_comments:
            latest = max(
                bot_comments,
                key=lambda comment: parse_time(comment["created_at"]),
            )
            body = sanitize_terminal_output(latest.get("body") or "").strip()
            if body:
                print("Codex left comments. Address feedback before merge.")
                print(body)
                raise WatchExit(2)
        if checks_done.is_set():
            now = monotonic_seconds()
            if feedback_grace_started_at is None:
                feedback_grace_started_at = now
                print(
                    f"Checks satisfied; waiting {FEEDBACK_GRACE_SECONDS}s for review feedback before merge...",
                    flush=True,
                )
            elif now - feedback_grace_started_at >= FEEDBACK_GRACE_SECONDS:
                if await validate_final_readiness(
                    head_sha,
                    hostname,
                    owner,
                    repo,
                    checks_done,
                ):
                    print(
                        "Feedback wait complete; no review feedback detected.",
                        flush=True,
                    )
                    return
                feedback_grace_started_at = None
        elif feedback_grace_started_at is not None:
            feedback_grace_started_at = None
            print(
                "Checks are no longer green; restarting feedback grace after checks pass.",
                flush=True,
            )
        await sleep(POLL_SECONDS)


async def wait_for_checks(
    head_sha: str,
    hostname: str,
    owner: str,
    repo: str,
    checks_done: asyncio.Event,
) -> None:
    print("Waiting for CI checks...", flush=True)
    empty_started_at: float | None = None
    checks_were_green = False
    reported_missing = False
    while True:
        check_runs = await get_ci_results(head_sha, hostname, owner, repo)
        if not check_runs:
            if checks_done.is_set():
                checks_done.clear()
                checks_were_green = False
                reported_missing = False
            now = monotonic_seconds()
            if empty_started_at is None:
                empty_started_at = now
            if now - empty_started_at >= CHECKS_APPEAR_TIMEOUT_SECONDS:
                if not reported_missing:
                    print(
                        f"No checks detected after {CHECKS_APPEAR_TIMEOUT_SECONDS}s; "
                        "continuing to monitor feedback and checks.",
                        flush=True,
                    )
                    reported_missing = True
                checks_done.set()
            await sleep(POLL_SECONDS)
            continue
        empty_started_at = None
        reported_missing = False
        pending, failed, failures = summarize_checks(check_runs)
        if failed:
            print("Checks failed:")
            for failure in failures:
                print(f"- {failure}")
            raise WatchExit(3)
        if pending:
            if checks_done.is_set():
                checks_done.clear()
                checks_were_green = False
                print("Checks are pending again; continuing to monitor")
            await sleep(POLL_SECONDS)
            continue
        if not pending:
            if not checks_were_green:
                print("Checks passed")
            checks_done.set()
            checks_were_green = True
        await sleep(POLL_SECONDS)


async def watch_pr() -> None:
    pr = await get_pr_info()
    if is_merge_conflicting(pr):
        print(
            "PR is behind, conflicting, or dirty. Merge/rebase against main and push before "
            "running land_watch again.",
        )
        raise WatchExit(5)
    head_sha = pr.head_sha
    checks_done = asyncio.Event()
    codex_task = asyncio.create_task(
        wait_for_codex(
            pr.number,
            pr.node_id,
            pr.hostname,
            pr.owner,
            pr.repo,
            head_sha,
            checks_done,
        ),
    )
    checks_task = asyncio.create_task(
        wait_for_checks(
            head_sha,
            pr.hostname,
            pr.owner,
            pr.repo,
            checks_done,
        ),
    )

    async def head_monitor() -> None:
        while True:
            current = await get_pr_info()
            if is_merge_conflicting(current):
                print(
                    "PR is behind, conflicting, or dirty. Merge/rebase against main and push "
                    "before running land_watch again.",
                )
                raise WatchExit(5)
            if current.head_sha != head_sha:
                print("PR head updated; pull/amend/force-push to retrigger CI")
                raise WatchExit(4)
            await sleep(POLL_SECONDS)

    monitor_task = asyncio.create_task(head_monitor())

    done, pending = await asyncio.wait(
        [monitor_task, codex_task, checks_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)
    for task in done:
        exc = task.exception()
        if exc:
            raise exc


if __name__ == "__main__":
    try:
        asyncio.run(watch_pr())
    except WatchExit as exc:
        raise SystemExit(exc.code) from None
    except SystemExit as exc:
        raise SystemExit(exc.code) from None
