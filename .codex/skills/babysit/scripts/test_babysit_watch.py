#!/usr/bin/env python3
import asyncio
import contextlib
import unittest

import babysit_watch


@contextlib.contextmanager
def patched(**attrs):
    original = {name: getattr(babysit_watch, name) for name in attrs}
    try:
        for name, value in attrs.items():
            setattr(babysit_watch, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(babysit_watch, name, value)


def human_comment(body="please fix"):
    return {
        "body": body,
        "created_at": "2026-05-01T00:00:00Z",
        "updated_at": "2026-05-01T00:00:00Z",
        "user": {"login": "reviewer"},
    }


def no_feedback_context():
    return [], [], [], None


class FakeClock:
    def __init__(self):
        self.now = 0

    async def sleep(self, seconds):
        self.now += seconds
        await asyncio.sleep(0)


class BabysitWatchTest(unittest.IsolatedAsyncioTestCase):
    async def test_feedback_before_checks_pass_exits_2(self):
        async def fetch_review_context(_pr_number):
            return [human_comment()], [], [], None

        with patched(fetch_review_context=fetch_review_context):
            with self.assertRaises(babysit_watch.WatchExit) as raised:
                await babysit_watch.wait_for_feedback(1, asyncio.Event())

        self.assertEqual(2, raised.exception.code)

    async def test_feedback_during_post_green_grace_exits_2(self):
        contexts = [no_feedback_context(), ([human_comment()], [], [], None)]
        checks_done = asyncio.Event()
        checks_done.set()
        clock = FakeClock()

        async def fetch_review_context(_pr_number):
            return contexts.pop(0)

        with patched(
            fetch_review_context=fetch_review_context,
            sleep=clock.sleep,
            monotonic_seconds=lambda: clock.now,
        ):
            with self.assertRaises(babysit_watch.WatchExit) as raised:
                await babysit_watch.wait_for_feedback(1, checks_done)

        self.assertEqual(2, raised.exception.code)

    async def test_no_feedback_through_post_green_grace_succeeds(self):
        checks_done = asyncio.Event()
        checks_done.set()
        clock = FakeClock()

        async def fetch_review_context(_pr_number):
            return no_feedback_context()

        with patched(
            FEEDBACK_GRACE_SECONDS=60,
            fetch_review_context=fetch_review_context,
            sleep=clock.sleep,
            monotonic_seconds=lambda: clock.now,
        ):
            await babysit_watch.wait_for_feedback(1, checks_done)

        self.assertEqual(60, clock.now)

    async def test_pr_head_update_during_feedback_grace_exits_4(self):
        initial = babysit_watch.PrInfo(
            number=1,
            title="Test PR",
            url="https://github.test/repo/pull/1",
            head_sha="initial",
            mergeable="MERGEABLE",
            merge_state="CLEAN",
        )
        updated = babysit_watch.PrInfo(
            number=1,
            title="Test PR",
            url="https://github.test/repo/pull/1",
            head_sha="updated",
            mergeable="MERGEABLE",
            merge_state="CLEAN",
        )
        calls = 0

        async def get_pr_info():
            nonlocal calls
            calls += 1
            return initial if calls == 1 else updated

        async def wait_for_checks(_head_sha, checks_done):
            checks_done.set()
            await asyncio.Event().wait()

        async def wait_for_feedback(_pr_number, checks_done):
            await checks_done.wait()
            await asyncio.Event().wait()

        with patched(
            get_pr_info=get_pr_info,
            wait_for_checks=wait_for_checks,
            wait_for_feedback=wait_for_feedback,
        ):
            with self.assertRaises(babysit_watch.WatchExit) as raised:
                await babysit_watch.watch_pr()

        self.assertEqual(4, raised.exception.code)


if __name__ == "__main__":
    unittest.main()
