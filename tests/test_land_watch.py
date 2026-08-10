import asyncio
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch


WATCHER_PATH = (
    Path(__file__).parents[1] / ".codex" / "skills" / "land" / "land_watch.py"
)
SPEC = importlib.util.spec_from_file_location("land_watch", WATCHER_PATH)
assert SPEC is not None and SPEC.loader is not None
land_watch = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = land_watch
SPEC.loader.exec_module(land_watch)


class PollIntervalTests(unittest.TestCase):
    def test_default_poll_interval_is_30_seconds(self) -> None:
        self.assertEqual(land_watch.parse_poll_seconds(None), 30)

    def test_poll_interval_can_be_increased(self) -> None:
        self.assertEqual(land_watch.parse_poll_seconds("60"), 60)

    def test_poll_interval_rejects_values_below_minimum(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "at least 30 seconds"):
            land_watch.parse_poll_seconds("29")

    def test_poll_interval_rejects_non_integer_values(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "must be an integer from 30 to 300"):
            land_watch.parse_poll_seconds("slow")

    def test_poll_interval_rejects_values_above_grace_safe_maximum(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "at most 300 seconds"):
            land_watch.parse_poll_seconds("301")

    def test_long_poll_interval_does_not_skip_check_appearance_timeout(self) -> None:
        checks_done = asyncio.Event()
        get_ci_results = AsyncMock(
            side_effect=[[], land_watch.WatchExit(99)],
        )

        with (
            patch.object(land_watch, "POLL_SECONDS", 300),
            patch.object(land_watch, "get_ci_results", get_ci_results),
            patch.object(land_watch, "monotonic_seconds", return_value=0),
            patch.object(land_watch, "sleep", AsyncMock()),
        ):
            with self.assertRaises(land_watch.WatchExit):
                asyncio.run(
                    land_watch.wait_for_checks(
                        "abc123",
                        "github.com",
                        "owner",
                        "repo",
                        checks_done,
                    ),
                )

        self.assertFalse(checks_done.is_set())

    def test_check_appearance_timeout_uses_monotonic_elapsed_time(self) -> None:
        checks_done = asyncio.Event()
        get_ci_results = AsyncMock(
            side_effect=[[], [], land_watch.WatchExit(99)],
        )

        with (
            patch.object(land_watch, "POLL_SECONDS", 300),
            patch.object(land_watch, "get_ci_results", get_ci_results),
            patch.object(land_watch, "monotonic_seconds", side_effect=[0, 121]),
            patch.object(land_watch, "sleep", AsyncMock()),
        ):
            with self.assertRaises(land_watch.WatchExit):
                asyncio.run(
                    land_watch.wait_for_checks(
                        "abc123",
                        "github.com",
                        "owner",
                        "repo",
                        checks_done,
                    ),
                )

        self.assertTrue(checks_done.is_set())


class FinalReadinessTests(unittest.TestCase):
    @staticmethod
    def pr_info(
        head_sha: str = "abc123",
        mergeable: str = "MERGEABLE",
        merge_state: str = "CLEAN",
    ) -> land_watch.PrInfo:
        return land_watch.PrInfo(
            number=42,
            node_id="PR_node_id",
            hostname="github.com",
            owner="owner",
            repo="repo",
            url="https://github.com/owner/repo/pull/42",
            head_sha=head_sha,
            mergeable=mergeable,
            merge_state=merge_state,
        )

    def test_final_readiness_accepts_current_head_with_no_checks(self) -> None:
        checks_done = asyncio.Event()
        checks_done.set()
        with (
            patch.object(land_watch, "get_ci_results", AsyncMock(return_value=[])),
            patch.object(
                land_watch,
                "get_pr_info",
                AsyncMock(return_value=self.pr_info()),
            ),
        ):
            ready = asyncio.run(
                land_watch.validate_final_readiness(
                    "abc123",
                    "github.com",
                    "owner",
                    "repo",
                    checks_done,
                ),
            )

        self.assertTrue(ready)
        self.assertTrue(checks_done.is_set())

    def test_final_readiness_restarts_for_pending_checks(self) -> None:
        checks_done = asyncio.Event()
        checks_done.set()
        pending_check = {
            "id": 1,
            "name": "tests",
            "status": "in_progress",
            "conclusion": None,
            "app": {"id": 1},
        }
        with patch.object(
            land_watch,
            "get_ci_results",
            AsyncMock(return_value=[pending_check]),
        ):
            ready = asyncio.run(
                land_watch.validate_final_readiness(
                    "abc123",
                    "github.com",
                    "owner",
                    "repo",
                    checks_done,
                ),
            )

        self.assertFalse(ready)
        self.assertFalse(checks_done.is_set())

    def test_final_readiness_rejects_failed_checks(self) -> None:
        failed_check = {
            "id": 1,
            "name": "tests",
            "status": "completed",
            "conclusion": "failure",
            "app": {"id": 1},
        }
        with patch.object(
            land_watch,
            "get_ci_results",
            AsyncMock(return_value=[failed_check]),
        ):
            with self.assertRaisesRegex(land_watch.WatchExit, "3"):
                asyncio.run(
                    land_watch.validate_final_readiness(
                        "abc123",
                        "github.com",
                        "owner",
                        "repo",
                        asyncio.Event(),
                    ),
                )

    def test_final_readiness_rejects_changed_head(self) -> None:
        with (
            patch.object(land_watch, "get_ci_results", AsyncMock(return_value=[])),
            patch.object(
                land_watch,
                "get_pr_info",
                AsyncMock(return_value=self.pr_info(head_sha="def456")),
            ),
        ):
            with self.assertRaisesRegex(land_watch.WatchExit, "4"):
                asyncio.run(
                    land_watch.validate_final_readiness(
                        "abc123",
                        "github.com",
                        "owner",
                        "repo",
                        asyncio.Event(),
                    ),
                )

    def test_final_readiness_rejects_conflicting_pr(self) -> None:
        with (
            patch.object(land_watch, "get_ci_results", AsyncMock(return_value=[])),
            patch.object(
                land_watch,
                "get_pr_info",
                AsyncMock(return_value=self.pr_info(mergeable="CONFLICTING")),
            ),
        ):
            with self.assertRaisesRegex(land_watch.WatchExit, "5"):
                asyncio.run(
                    land_watch.validate_final_readiness(
                        "abc123",
                        "github.com",
                        "owner",
                        "repo",
                        asyncio.Event(),
                    ),
                )

    def test_final_readiness_honors_newer_unsatisfied_ci_poll(self) -> None:
        checks_done = asyncio.Event()
        checks_done.set()

        async def clear_checks_during_pr_refresh() -> land_watch.PrInfo:
            checks_done.clear()
            return self.pr_info()

        with (
            patch.object(land_watch, "get_ci_results", AsyncMock(return_value=[])),
            patch.object(
                land_watch,
                "get_pr_info",
                AsyncMock(side_effect=clear_checks_during_pr_refresh),
            ),
        ):
            ready = asyncio.run(
                land_watch.validate_final_readiness(
                    "abc123",
                    "github.com",
                    "owner",
                    "repo",
                    checks_done,
                ),
            )

        self.assertFalse(ready)


class WatcherCompletionTests(unittest.TestCase):
    def test_feedback_is_refetched_after_final_readiness_validation(self) -> None:
        checks_done = asyncio.Event()
        checks_done.set()
        check_review_feedback = AsyncMock()

        with (
            patch.object(land_watch, "FEEDBACK_GRACE_SECONDS", 0),
            patch.object(land_watch, "monotonic_seconds", return_value=0),
            patch.object(land_watch, "sleep", AsyncMock()),
            patch.object(
                land_watch,
                "check_review_feedback",
                check_review_feedback,
            ),
            patch.object(
                land_watch,
                "validate_final_readiness",
                AsyncMock(return_value=True),
            ),
        ):
            asyncio.run(
                land_watch.wait_for_codex(
                    42,
                    "PR_node_id",
                    "github.com",
                    "owner",
                    "repo",
                    "abc123",
                    checks_done,
                ),
            )

        self.assertEqual(check_review_feedback.await_count, 3)


class PullRequestIdentityTests(unittest.TestCase):
    def test_run_gh_routes_custom_port_through_process_environment(self) -> None:
        process = AsyncMock()
        process.returncode = 0
        process.communicate.return_value = (b"{}", b"")
        create_process = AsyncMock(return_value=process)

        with patch.object(
            land_watch.asyncio,
            "create_subprocess_exec",
            create_process,
        ):
            result = asyncio.run(
                land_watch.run_gh(
                    "api",
                    "user",
                    api_host="github.example:8443",
                ),
            )

        self.assertEqual(result, "{}")
        self.assertEqual(
            create_process.await_args.kwargs["env"]["GH_HOST"],
            "github.example:8443",
        )
        self.assertEqual(create_process.await_args.args[:3], ("gh", "api", "user"))

    def test_get_pr_info_includes_graphql_node_id(self) -> None:
        payload = {
            "number": 42,
            "id": "PR_node_id",
            "url": "https://github.example:8443/owner/repo/pull/42",
            "headRefOid": "abc123",
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }
        run_gh = AsyncMock(return_value=json.dumps(payload))

        with patch.object(land_watch, "run_gh", run_gh):
            pr = asyncio.run(land_watch.get_pr_info())

        self.assertEqual(pr.node_id, "PR_node_id")
        self.assertEqual(pr.hostname, "github.example:8443")
        self.assertEqual((pr.owner, pr.repo), ("owner", "repo"))
        run_gh.assert_awaited_once_with(
            "pr",
            "view",
            "--json",
            "number,id,url,headRefOid,mergeable,mergeStateStatus",
        )

    def test_review_threads_are_looked_up_by_pull_request_node_id(self) -> None:
        payload = {
            "data": {
                "node": {
                    "reviewThreads": {
                        "nodes": [
                            {
                                "id": "thread-id",
                                "isResolved": False,
                                "isOutdated": False,
                                "comments": {
                                    "nodes": [{"id": "comment-id"}],
                                    "pageInfo": {
                                        "hasNextPage": False,
                                        "endCursor": None,
                                    },
                                },
                            },
                        ],
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": None,
                        },
                    },
                },
            },
        }
        run_gh = AsyncMock(return_value=json.dumps(payload))

        with patch.object(land_watch, "run_gh", run_gh):
            comment_ids = asyncio.run(
                land_watch.get_active_review_thread_comment_node_ids(
                    "PR_node_id",
                    "github.example:8443",
                ),
            )

        self.assertEqual(comment_ids, {"comment-id"})
        args = run_gh.await_args.args
        self.assertEqual(args[:2], ("api", "graphql"))
        self.assertEqual(
            run_gh.await_args.kwargs,
            {"api_host": "github.example:8443"},
        )
        self.assertIn("pullRequestId=PR_node_id", args)
        self.assertNotIn("owner", " ".join(args))
        self.assertNotIn("repo", " ".join(args))

    def test_rest_review_queries_use_selected_pull_request_repository(self) -> None:
        run_gh = AsyncMock(side_effect=[json.dumps([{"id": 1}]), "[]"])

        with patch.object(land_watch, "run_gh", run_gh):
            comments = asyncio.run(
                land_watch.get_issue_comments(
                    42,
                    "github.example:8443",
                    "selected-owner",
                    "selected-repo",
                ),
            )

        self.assertEqual(comments, [{"id": 1}])
        run_gh.assert_any_await(
            "api",
            "--method",
            "GET",
            "repos/selected-owner/selected-repo/issues/42/comments",
            "-f",
            "per_page=100",
            "-f",
            "page=1",
            api_host="github.example:8443",
        )

    def test_ci_queries_use_selected_pull_request_repository(self) -> None:
        payload = {"total_count": 0, "check_runs": []}
        run_gh = AsyncMock(return_value=json.dumps(payload))

        with patch.object(land_watch, "run_gh", run_gh):
            check_runs = asyncio.run(
                land_watch.get_check_runs(
                    "abc123",
                    "github.example:8443",
                    "selected-owner",
                    "selected-repo",
                ),
            )

        self.assertEqual(check_runs, [])
        run_gh.assert_awaited_once_with(
            "api",
            "--method",
            "GET",
            "repos/selected-owner/selected-repo/commits/abc123/check-runs",
            "-f",
            "per_page=100",
            "-f",
            "page=1",
            api_host="github.example:8443",
        )


if __name__ == "__main__":
    unittest.main()
