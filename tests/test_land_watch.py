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


class PullRequestIdentityTests(unittest.TestCase):
    def test_get_pr_info_includes_graphql_node_id(self) -> None:
        payload = {
            "number": 42,
            "id": "PR_node_id",
            "url": "https://github.example/owner/repo/pull/42",
            "headRefOid": "abc123",
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
        }
        run_gh = AsyncMock(return_value=json.dumps(payload))

        with patch.object(land_watch, "run_gh", run_gh):
            pr = asyncio.run(land_watch.get_pr_info())

        self.assertEqual(pr.node_id, "PR_node_id")
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
                ),
            )

        self.assertEqual(comment_ids, {"comment-id"})
        args = run_gh.await_args.args
        self.assertIn("pullRequestId=PR_node_id", args)
        self.assertNotIn("owner", " ".join(args))
        self.assertNotIn("repo", " ".join(args))


if __name__ == "__main__":
    unittest.main()
