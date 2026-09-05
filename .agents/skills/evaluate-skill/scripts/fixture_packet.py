#!/usr/bin/env python3
"""Validate bundled decision fixtures or emit one rubric-free input packet.

This is an evaluator-side serializer, not a runner or an isolation boundary.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
INITIAL_KEYS = {"request", "artifacts", "environment", "constraints", "termination"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def fields(value: object, required: set[str], optional: set[str], label: str) -> None:
    require(isinstance(value, dict), f"{label} must be an object")
    require(required <= value.keys(), f"{label} is missing required fields")
    require(value.keys() <= required | optional, f"{label} has unknown fields")


def nonempty(value: object, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be text")


def strings(value: object, label: str) -> None:
    require(isinstance(value, list), f"{label} must be a list")
    for item in value:
        nonempty(item, label)


def artifacts(value: object) -> None:
    require(isinstance(value, dict), "artifacts must map relative names to content")
    for name, content in value.items():
        path = PurePosixPath(name)
        require(
            bool(name) and not path.is_absolute() and ".." not in path.parts
            and "\\" not in name and ":" not in name and path.name != "",
            "artifact names must be relative paths without traversal",
        )
        nonempty(content, "artifact content")


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def load_fixture(directory: Path) -> tuple[dict, dict]:
    agent = read_json(directory / "agent.json")
    evaluator = read_json(directory / "evaluator.json")
    fields(agent, INITIAL_KEYS, {"events"}, "agent")
    for key in ("request", "environment"):
        nonempty(agent[key], key)
    artifacts(agent["artifacts"])
    strings(agent["constraints"], "constraints")
    fields(agent["termination"], {"condition", "max_responses"}, set(), "termination")
    nonempty(agent["termination"]["condition"], "termination condition")
    limit = agent["termination"]["max_responses"]
    require(type(limit) is int and limit > 0, "max_responses must be a positive integer")
    events = agent.get("events", [])
    require(isinstance(events, list), "events must be a list")
    for event in events:
        fields(event, {"observation"}, {"artifacts"}, "event")
        nonempty(event["observation"], "observation")
        if "artifacts" in event:
            artifacts(event["artifacts"])

    fields(
        evaluator,
        {"id", "version", "target_skill", "question", "kind", "split", "mode", "criteria"},
        {"known_defects", "catalog_note", "provenance"},
        "evaluator",
    )
    for key in ("id", "target_skill"):
        nonempty(evaluator[key], key)
        require(bool(SLUG.fullmatch(evaluator[key])), f"invalid {key}")
    require(evaluator["id"] == directory.name, "fixture ID must match its directory")
    version = evaluator["version"]
    require(type(version) is int and version > 0, "version must be a positive integer")
    for key in ("question", "kind", "catalog_note", "provenance"):
        if key in evaluator:
            nonempty(evaluator[key], key)
    require(evaluator["split"] in ("development", "held-out"), "invalid split")
    require(evaluator["mode"] == "simulated-decision", "only simulated-decision fixtures are supported")
    criteria = evaluator["criteria"]
    require(isinstance(criteria, list) and bool(criteria), "criteria must be a nonempty list")
    seen = set()
    for criterion in criteria:
        fields(criterion, {"id", "expectation", "evidence", "consequential"}, set(), "criterion")
        for key in ("id", "expectation", "evidence"):
            nonempty(criterion[key], key)
        require(criterion["id"] not in seen, "duplicate criterion ID")
        seen.add(criterion["id"])
        require(type(criterion["consequential"]) is bool, "consequential must be boolean")
    if "known_defects" in evaluator:
        strings(evaluator["known_defects"], "known_defects")
    return agent, evaluator


def packet(directory: Path, event: int | None = None, release_held_out: bool = False) -> dict:
    agent, evaluator = load_fixture(directory)
    require(evaluator["split"] != "held-out" or release_held_out,
            "held-out packet requires --release-held-out after candidate freeze")
    if event is None:
        return {key: value for key, value in agent.items() if key in INITIAL_KEYS}
    events = agent.get("events", [])
    require(type(event) is int and 1 <= event <= len(events), "event number is out of range")
    return events[event - 1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="validate all bundled fixture pairs")
    emit = commands.add_parser("packet", help="emit initial inputs or one event as JSON")
    emit.add_argument("fixture_id")
    emit.add_argument("--event", type=int, help="one-based event number; omit for initial inputs")
    emit.add_argument("--release-held-out", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            directories = sorted(path for path in FIXTURES.iterdir() if path.is_dir())
            require(bool(directories), "no fixtures found")
            for directory in directories:
                load_fixture(directory)
            print(f"Validated {len(directories)} fixtures; no evaluations were run.")
        else:
            require(bool(SLUG.fullmatch(args.fixture_id)), "invalid fixture ID")
            directory = FIXTURES / args.fixture_id
            require(directory.resolve().parent == FIXTURES.resolve(), "fixture leaves bundled root")
            output = packet(directory, args.event, args.release_held_out)
            print(json.dumps(output, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        print(f"Fixture error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
