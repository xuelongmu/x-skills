from __future__ import annotations

import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "evaluate-skill"
SCRIPT = SKILL / "scripts" / "fixture_packet.py"
HELPER = runpy.run_path(str(SCRIPT))


class FixturePacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.case = Path(self.temp.name) / "capture-unverified"
        shutil.copytree(SKILL / "fixtures" / self.case.name, self.case)

    def edit(self, filename: str, change) -> None:
        path = self.case / filename
        value = json.loads(path.read_text(encoding="utf-8"))
        change(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_all_bundled_fixtures_are_valid(self) -> None:
        for case in (SKILL / "fixtures").iterdir():
            with self.subTest(case=case.name):
                HELPER["load_fixture"](case)

    def test_initial_packet_omits_evaluator_data_and_future_events(self) -> None:
        self.edit("evaluator.json", lambda value: value.update(question="SECRET-RUBRIC"))
        self.edit("agent.json", lambda value: value.update(events=[
            {"observation": "FUTURE-ONE"}, {"observation": "FUTURE-TWO"}
        ]))
        initial = HELPER["packet"](self.case)
        encoded = json.dumps(initial)
        self.assertNotIn("SECRET-RUBRIC", encoded)
        self.assertNotIn("target_skill", initial)
        self.assertNotIn("FUTURE", encoded)
        self.assertEqual(HELPER["packet"](self.case, event=1), {"observation": "FUTURE-ONE"})
        self.assertEqual(HELPER["packet"](self.case, event=2), {"observation": "FUTURE-TWO"})

    def test_packet_preserves_task_artifacts_and_constraints_exactly(self) -> None:
        source = json.loads((self.case / "agent.json").read_text(encoding="utf-8"))
        self.assertEqual(HELPER["packet"](self.case), source)

    def test_unknown_input_fields_are_rejected_instead_of_forwarded(self) -> None:
        for location in ("root", "termination", "event"):
            with self.subTest(location=location):
                path = self.case / "agent.json"
                original = path.read_bytes()
                try:
                    def inject(value):
                        if location == "root":
                            value["criteria"] = "SECRET"
                        elif location == "termination":
                            value["termination"]["expected_answer"] = "SECRET"
                        else:
                            value["events"] = [{"observation": "update", "criteria": "SECRET"}]
                    self.edit("agent.json", inject)
                    with self.assertRaisesRegex(ValueError, "unknown fields"):
                        HELPER["packet"](self.case)
                finally:
                    path.write_bytes(original)

    def test_invalid_budgets_and_events_fail(self) -> None:
        for limit in (0, -1, True, "1"):
            self.edit("agent.json", lambda value: value["termination"].update(max_responses=limit))
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                HELPER["packet"](self.case)
        self.edit("agent.json", lambda value: value["termination"].update(max_responses=1))
        for event in (0, -1, 1):
            with self.subTest(event=event), self.assertRaisesRegex(ValueError, "out of range"):
                HELPER["packet"](self.case, event=event)

    def test_held_out_requires_deliberate_release(self) -> None:
        case = SKILL / "fixtures" / "review-job-boundary"
        with self.assertRaisesRegex(ValueError, "held-out"):
            HELPER["packet"](case)
        self.assertIn("request", HELPER["packet"](case, release_held_out=True))

    def test_unsupported_execution_mode_fails(self) -> None:
        self.edit("evaluator.json", lambda value: value.update(mode="execution"))
        with self.assertRaisesRegex(ValueError, "only simulated-decision"):
            HELPER["packet"](self.case)

    def test_duplicate_keys_and_missing_files_fail(self) -> None:
        path = self.case / "agent.json"
        path.write_text('{"request":"first","request":"second"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            HELPER["packet"](self.case)
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            HELPER["packet"](self.case)

    def test_cli_uses_relocated_resources_and_fails_without_emitting_packet(self) -> None:
        relocated = Path(self.temp.name) / "installed skill with spaces"
        shutil.copytree(SKILL, relocated)
        script = relocated / "scripts" / "fixture_packet.py"
        command = [sys.executable, "-B", str(script)]
        result = subprocess.run(command + ["packet", "capture-unverified"],
                                cwd=self.temp.name, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), HELPER["packet"](self.case))
        for args in (["packet", "missing-case"], ["packet", "../capture-unverified"],
                     ["packet", "capture-unverified", "--event", "1"]):
            result = subprocess.run(command + args, cwd=self.temp.name,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("Fixture error:", result.stderr)
        (relocated / "fixtures" / "capture-unverified" / "evaluator.json").unlink()
        result = subprocess.run(command + ["validate"], cwd=self.temp.name,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


class FixtureFactTests(unittest.TestCase):
    """Check supplied code facts, not any model's ability to find or repair them."""

    def source(self, case: str, path: str) -> dict:
        agent, _ = HELPER["load_fixture"](SKILL / "fixtures" / case)
        namespace = {}
        exec(compile(agent["artifacts"][path], path, "exec"), namespace)
        return namespace

    def test_review_pair_distinguishes_bypass_from_owning_guard(self) -> None:
        actor = SimpleNamespace(account_id="one")
        reads = []
        store = SimpleNamespace(read=lambda account: reads.append(account) or "data")
        bypass = self.source("review-bypass", "src/routes.py")
        self.assertEqual(bypass["preview"](actor, "two", store), "data")
        self.assertEqual(reads, ["two"])
        reads.clear()
        guarded = self.source("review-owned-guard", "src/routes.py")
        with self.assertRaises(PermissionError):
            guarded["preview"](actor, "two", store)
        self.assertEqual(reads, [])
        self.assertEqual(guarded["preview"](actor, "one", store), "data")

    def test_supplied_parser_fix_preserves_stated_cases(self) -> None:
        parser = self.source("capture-verified", "src/parser.py")["first_token"]
        self.assertIsNone(parser(""))
        self.assertIsNone(parser("   "))
        self.assertEqual(parser("alpha beta"), "alpha")


if __name__ == "__main__":
    unittest.main()
