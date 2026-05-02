#!/usr/bin/env python3
import asyncio
import json
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any

POLL_SECONDS = 10
CHECKS_APPEAR_TIMEOUT_SECONDS = 120
FEEDBACK_GRACE_SECONDS = 600
CODEX_BOTS = {
    "chatgpt-codex-connector",
    "chatgpt-codex-connector[bot]",
    "codex-gc-app[bot]",
    "app/codex-gc-app",
}
CODEX_BRIDGE_BOTS = {
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


def is_rate_limit_error(error: str) -> bool:
    return "HTTP 429" in error or "rate limit" in error.lower()


async def run_gh(*args: str) -> str:
    max_delay = BASE_GH_BACKOFF_SECONDS * (2 ** (MAX_GH_RETRIES - 1))
    delay_seconds = BASE_GH_BACKOFF_SECONDS
    last_error = "gh command failed"
    for attempt in range(1, MAX_GH_RETRIES + 1):
        proc = await asyncio.create_subprocess_exec(
            "gh",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
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
        "number,url,headRefOid,mergeable,mergeStateStatus",
    )
    parsed = json.loads(data)
    return PrInfo(
        number=parsed["number"],
        url=parsed["url"],
        head_sha=parsed["headRefOid"],
        mergeable=parsed.get("mergeable"),
        merge_state=parsed.get("mergeStateStatus"),
    )


async def get_paginated_list(endpoint: str) -> list[dict[str, Any]]:
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
        )
        batch = json.loads(data)
        if not batch:
            break
        items.extend(batch)
        page += 1
    return items


async def get_issue_comments(pr_number: int) -> list[dict[str, Any]]:
    return await get_paginated_list(
        f"repos/{{owner}}/{{repo}}/issues/{pr_number}/comments",
    )


async def get_review_comments(pr_number: int) -> list[dict[str, Any]]:
    return await get_paginated_list(
        f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/comments",
    )


async def get_reviews(pr_number: int) -> list[dict[str, Any]]:
    page = 1
    reviews: list[dict[str, Any]] = []
    while True:
        data = await run_gh(
            "api",
            "--method",
            "GET",
            f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/reviews",
            "-f",
            "per_page=100",
            "-f",
            f"page={page}",
        )
        batch = json.loads(data)
        if not batch:
            break
        reviews.extend(batch)
        page += 1
    return reviews


async def get_authenticated_user_login() -> str | None:
    data = await run_gh("api", "user", "--jq", ".login")
    login = data.strip()
    return login or None


async def get_check_runs(head_sha: str) -> list[dict[str, Any]]:
    page = 1
    check_runs: list[dict[str, Any]] = []
    while True:
        data = await run_gh(
            "api",
            "--method",
            "GET",
            f"repos/{{owner}}/{{repo}}/commits/{head_sha}/check-runs",
            "-f",
            "per_page=100",
            "-f",
            f"page={page}",
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


def parse_time(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
CODEX_REVIEW_HEADING_RE = re.compile(
    r"^#{2,3}\s*(?:[^\w#]+\s*)?Codex Review\b",
    re.IGNORECASE,
)


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
    latest_by_name: dict[str, dict[str, Any]] = {}
    for check in check_runs:
        name = check.get("name", "unknown")
        timestamp = check_timestamp(check)
        if name not in latest_by_name:
            latest_by_name[name] = check
            continue
        existing = latest_by_name[name]
        existing_timestamp = check_timestamp(existing)
        if timestamp is None:
            continue
        if existing_timestamp is None or timestamp > existing_timestamp:
            latest_by_name[name] = check
    return list(latest_by_name.values())


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


def is_codex_bot_user(user: dict[str, Any]) -> bool:
    login = user.get("login") or ""
    return login in CODEX_BOTS


def is_codex_bridge_bot_user(user: dict[str, Any]) -> bool:
    login = user.get("login") or ""
    return login in CODEX_BRIDGE_BOTS


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
        return False
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
    latest_by_user: dict[str, dict[str, Any]] = {}
    for review in reviews:
        user_login = review.get("user", {}).get("login")
        if not user_login:
            continue
        timestamp = review_timestamp(review)
        if user_login not in latest_by_user:
            latest_by_user[user_login] = review
            continue
        existing = latest_by_user[user_login]
        existing_timestamp = review_timestamp(existing)
        if timestamp is None:
            continue
        if existing_timestamp is None or timestamp > existing_timestamp:
            latest_by_user[user_login] = review
    return list(latest_by_user.values())


def filter_blocking_reviews(
    reviews: list[dict[str, Any]],
    review_requested_at: datetime | None,
) -> list[dict[str, Any]]:
    return [
        review
        for review in dedupe_reviews(reviews)
        if is_blocking_review(review, review_requested_at)
    ]


def is_merge_conflicting(pr: PrInfo) -> bool:
    return pr.mergeable == "CONFLICTING" or pr.merge_state == "DIRTY"


async def fetch_review_context(
    pr_number: int,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    datetime | None,
    set[str],
]:
    issue_comments = await get_issue_comments(pr_number)
    review_request_at = latest_review_request_at(issue_comments)
    review_comments = await get_review_comments(pr_number)
    reviews = await get_reviews(pr_number)
    authenticated_login = await get_authenticated_user_login()
    trusted_ack_logins = {authenticated_login} if authenticated_login else set()
    return (
        issue_comments,
        review_comments,
        reviews,
        review_request_at,
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
    blocking_reviews = filter_blocking_reviews(reviews, review_request_at)
    if blocking_reviews:
        print("Review states/comments detected. Address before merge.")
        print(
            "Reminder: keep PR title/description aligned with the full scope "
            "when changes expand.",
        )
        raise WatchExit(2)


async def wait_for_codex(pr_number: int, checks_done: asyncio.Event) -> None:
    print("Waiting for review feedback...", flush=True)
    feedback_grace_started_at: float | None = None
    while True:
        (
            issue_comments,
            review_comments,
            reviews,
            review_request_at,
            trusted_ack_logins,
        ) = await fetch_review_context(pr_number)
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
            review_comments,
            review_request_at,
            codex_review_ids,
            trusted_ack_logins,
        )
        bot_comments = bot_issue_comments + bot_review_comments
        raise_on_human_feedback(
            issue_comments,
            review_comments,
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
                    f"Checks passed; waiting {FEEDBACK_GRACE_SECONDS}s for review feedback before merge...",
                    flush=True,
                )
            elif now - feedback_grace_started_at >= FEEDBACK_GRACE_SECONDS:
                print("Feedback wait complete; no review feedback detected.", flush=True)
                return
        await sleep(POLL_SECONDS)


async def wait_for_checks(head_sha: str, checks_done: asyncio.Event) -> None:
    print("Waiting for CI checks...", flush=True)
    empty_seconds = 0
    while True:
        check_runs = await get_check_runs(head_sha)
        if not check_runs:
            empty_seconds += POLL_SECONDS
            if empty_seconds >= CHECKS_APPEAR_TIMEOUT_SECONDS:
                print(
                    "No checks detected after 120s; check CI configuration",
                )
                raise WatchExit(3)
            await sleep(POLL_SECONDS)
            continue
        empty_seconds = 0
        pending, failed, failures = summarize_checks(check_runs)
        if failed:
            print("Checks failed:")
            for failure in failures:
                print(f"- {failure}")
            raise WatchExit(3)
        if not pending:
            print("Checks passed")
            checks_done.set()
            return
        await sleep(POLL_SECONDS)


async def watch_pr() -> None:
    pr = await get_pr_info()
    if is_merge_conflicting(pr):
        print(
            "PR has merge conflicts. Resolve/rebase against main and push before "
            "running land_watch again.",
        )
        raise WatchExit(5)
    head_sha = pr.head_sha
    checks_done = asyncio.Event()
    codex_task = asyncio.create_task(wait_for_codex(pr.number, checks_done))
    checks_task = asyncio.create_task(wait_for_checks(head_sha, checks_done))

    async def head_monitor() -> None:
        while True:
            current = await get_pr_info()
            if is_merge_conflicting(current):
                print(
                    "PR has merge conflicts. Resolve/rebase against main and push "
                    "before running land_watch again.",
                )
                raise WatchExit(5)
            if current.head_sha != head_sha:
                print("PR head updated; pull/amend/force-push to retrigger CI")
                raise WatchExit(4)
            await sleep(POLL_SECONDS)

    monitor_task = asyncio.create_task(head_monitor())
    success_task = asyncio.gather(codex_task, checks_task)

    done, pending = await asyncio.wait(
        [monitor_task, success_task],
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
