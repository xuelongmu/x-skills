from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CANONICAL = {
    "babysit",
    "browser-evidence",
    "capture-learning",
    "design-architecture",
    "drive-agent-orchestrator",
    "evaluate-skill",
    "google-developer-style",
    "land",
    "orchestrate",
    "prompt-agent-orchestrator",
    "publish",
    "review-architecture",
    "review-change",
    "review-complexity",
    "steward-research",
}
STANDARD_FRONTMATTER_FIELDS = {
    "allowed-tools",
    "compatibility",
    "description",
    "license",
    "metadata",
    "name",
}
NON_STRING_YAML_SCALAR = re.compile(
    r"(?:~|null|true|false|"
    r"[-+]?(?:\.inf|\.nan|0x[0-9a-f_]+|0o[0-7_]+|"
    r"(?:\d[\d_]*)(?:\.\d[\d_]*)?(?:e[-+]?\d[\d_]*)?))",
    re.IGNORECASE,
)


def skill_dirs(container: Path) -> set[str]:
    if not container.is_dir():
        return set()
    return {
        child.name
        for child in container.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    }


def all_skill_paths() -> list[Path]:
    paths: list[Path] = []
    for container in (".agents", ".codex", ".claude"):
        root = ROOT / container / "skills"
        paths.extend(root / name for name in sorted(skill_dirs(root)))
    return paths


def yaml_string_scalar(value: str, label: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        parsed = ast.literal_eval(value)
        if not isinstance(parsed, str):
            raise AssertionError(f"{label} must be a YAML string")
        return parsed
    if value.startswith(("[", "{", "&", "*", "!", "- ")) or (
        value and NON_STRING_YAML_SCALAR.fullmatch(value)
    ):
        raise AssertionError(f"{label} must be a YAML string")
    return value


def top_level_yaml(text: str) -> dict[str, tuple[str, list[str]]]:
    fields: dict[str, tuple[str, list[str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            match = re.fullmatch(r"([a-z][a-z0-9-]*):(?:\s*(.*))?", line)
            if not match:
                raise AssertionError(f"Invalid top-level YAML line: {line}")
            current = match.group(1)
            if current in fields:
                raise AssertionError(f"duplicate top-level key: {current}")
            fields[current] = (match.group(2) or "", [])
        elif current is not None:
            fields[current][1].append(line)
        else:
            raise AssertionError(f"Indented YAML without a parent: {line}")
    return fields


def scalar_field(fields: dict[str, tuple[str, list[str]]], key: str) -> str:
    value, continuation = fields[key]
    if value in {">", ">-", ">+", "|", "|-", "|+"}:
        return " ".join(line.strip() for line in continuation if line.strip())
    if value == "" and continuation:
        nested = [line.strip() for line in continuation if line.strip()]
        if any(
            line.startswith(("- ", "[", "{"))
            or re.match(r"[^:]+:(?:\s+.*)?$", line)
            for line in nested
        ):
            raise AssertionError(f"Expected scalar YAML field: {key}")
        return " ".join(nested)
    if continuation:
        raise AssertionError(f"Expected scalar YAML field: {key}")
    return yaml_string_scalar(value, f"Expected scalar YAML field: {key}")


def metadata_strings(field: tuple[str, list[str]]) -> dict[str, str]:
    value, nested = field
    if value != "" or not nested:
        raise AssertionError("metadata must be a non-empty mapping")

    parsed: dict[str, str] = {}
    for line in nested:
        match = re.fullmatch(r"\s+([\w.-]+):\s*(.+)", line)
        if not match:
            raise AssertionError(f"metadata values must be scalar strings: {line}")
        key, raw_value = match.groups()
        raw_value = raw_value.strip()
        if key in parsed:
            raise AssertionError(f"duplicate metadata key: {key}")
        parsed[key] = yaml_string_scalar(raw_value, "metadata value")
    return parsed


def frontmatter(skill: Path) -> dict[str, tuple[str, list[str]]]:
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise AssertionError(f"Missing YAML frontmatter: {skill}")
    return top_level_yaml(match.group(1))


class SkillLayoutTests(unittest.TestCase):
    def test_top_level_frontmatter_rejects_duplicate_keys(self) -> None:
        with self.assertRaisesRegex(AssertionError, "duplicate top-level key: name"):
            top_level_yaml("name: wrong\nname: publish")

    def test_scalar_frontmatter_rejects_structured_yaml(self) -> None:
        for continuation in (("  - Bash",), ("  nested: value",), ("  [Bash, Read]",)):
            with self.subTest(continuation=continuation):
                with self.assertRaisesRegex(AssertionError, "Expected scalar YAML"):
                    scalar_field({"allowed-tools": ("", list(continuation))}, "allowed-tools")
        self.assertEqual(
            scalar_field({"description": ("", ["  See https://example.com"])}, "description"),
            "See https://example.com",
        )
        for value in ("[one, two]", "{tool: true}", "false", "2", "1.5"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(AssertionError, "YAML string"):
                    scalar_field({"description": (value, [])}, "description")
        self.assertEqual(
            scalar_field({"description": ('"false"', [])}, "description"),
            "false",
        )

    def test_metadata_rejects_non_string_child_values(self) -> None:
        invalid_values = (
            "  version: [1, 2]",
            "  config: {mode: strict}",
            "  enabled: true",
            "  version: 2",
        )
        for line in invalid_values:
            with self.subTest(line=line):
                with self.assertRaisesRegex(AssertionError, "YAML string"):
                    metadata_strings(("", [line]))
        self.assertEqual(
            metadata_strings(("", ["  author: openai", '  version: "2"'])),
            {"author": "openai", "version": "2"},
        )

    def test_inventory_matches_the_audited_layout(self) -> None:
        self.assertEqual(skill_dirs(ROOT / ".agents" / "skills"), CANONICAL)
        self.assertEqual(skill_dirs(ROOT / ".codex" / "skills"), set())
        self.assertEqual(skill_dirs(ROOT / ".claude" / "skills"), set())

    def test_canonical_skills_have_no_host_source_copies(self) -> None:
        for name in CANONICAL:
            with self.subTest(skill=name):
                self.assertFalse(
                    (ROOT / ".codex" / "skills" / name / "SKILL.md").exists()
                )
                self.assertFalse(
                    (ROOT / ".claude" / "skills" / name / "SKILL.md").exists()
                )

    def test_every_skill_uses_standard_frontmatter(self) -> None:
        name_pattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        for skill in all_skill_paths():
            with self.subTest(skill=skill.relative_to(ROOT)):
                data = frontmatter(skill)
                self.assertLessEqual(set(data), STANDARD_FRONTMATTER_FIELDS)
                self.assertIn("name", data)
                self.assertEqual(scalar_field(data, "name"), skill.name)
                self.assertRegex(skill.name, name_pattern)
                self.assertLessEqual(len(skill.name), 64)

                self.assertIn("description", data)
                description = scalar_field(data, "description")
                self.assertGreater(len(description.strip()), 0)
                self.assertLessEqual(len(description), 1024)

                if "compatibility" in data:
                    self.assertLessEqual(len(scalar_field(data, "compatibility")), 500)
                if "metadata" in data:
                    self.assertTrue(metadata_strings(data["metadata"]))
                if "allowed-tools" in data:
                    scalar_field(data, "allowed-tools")

    def test_openai_metadata_is_consistent(self) -> None:
        for skill in all_skill_paths():
            metadata = skill / "agents" / "openai.yaml"
            if not metadata.is_file():
                continue
            with self.subTest(skill=skill.relative_to(ROOT)):
                text = metadata.read_text(encoding="utf-8")
                short_match = re.search(r"^\s+short_description:\s*(.+)$", text, re.MULTILINE)
                prompt_match = re.search(r"^\s+default_prompt:\s*(.+)$", text, re.MULTILINE)
                self.assertIsNotNone(short_match)
                self.assertIsNotNone(prompt_match)
                short_description = yaml_string_scalar(
                    short_match.group(1), "interface.short_description"
                )
                default_prompt = yaml_string_scalar(
                    prompt_match.group(1), "interface.default_prompt"
                )
                self.assertTrue(25 <= len(short_description) <= 64)
                self.assertIn(f"${skill.name}", default_prompt)

    def test_land_bundles_watcher_under_scripts(self) -> None:
        watcher = ROOT / ".agents" / "skills" / "land" / "scripts" / "land_watch.py"
        self.assertTrue(watcher.is_file())
        self.assertFalse(
            (ROOT / ".agents" / "skills" / "land" / "land_watch.py").exists()
        )

    def test_retired_skill_name_is_limited_to_cli_cleanup(self) -> None:
        retired = "-".join(("code", "meta", "reviewer"))
        occurrences: list[tuple[Path, str]] = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for line in text.splitlines():
                if retired in line:
                    occurrences.append((path.relative_to(ROOT), line.strip()))

        self.assertEqual(
            occurrences,
            [(Path("README.md"), f"npx skills@latest remove {retired}")],
        )

    def test_reusable_skills_do_not_name_a_local_product(self) -> None:
        local_product = "".join(("zero", "gen"))
        for path in (ROOT / ".agents" / "skills").rglob("*"):
            if path.is_file():
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                with self.subTest(path=path.relative_to(ROOT)):
                    self.assertNotIn(
                        local_product,
                        text.lower(),
                    )

    def test_documentation_uses_cli_only_for_install_lifecycle(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        layout = (ROOT / "docs" / "skill-layout.md").read_text(encoding="utf-8")
        combined = f"{readme}\n{layout}"

        for stale_recipe in ("New-Item -ItemType Junction", "ln -s ", "Copy-Item", "cp -R "):
            with self.subTest(recipe=stale_recipe):
                self.assertNotIn(stale_recipe, combined)

        self.assertIn("npx skills@latest add xuelongmu/x-skills", readme)
        self.assertIn("npx skills@latest update", readme)
        self.assertIn("npx skills@latest remove", readme)
        self.assertEqual(readme.count("npx skills@latest add xuelongmu/x-skills"), 1)
        self.assertIn("Refresh installed skills and reconcile upstream deletions", readme)
        self.assertIn("updates the complete selected", layout)
        self.assertNotRegex(
            readme,
            r"npx skills@latest add xuelongmu/x-skills[^\n]*--global",
        )
        self.assertNotIn("--agent codex claude-code", readme)
        self.assertNotIn("--skill '*'", readme)
        self.assertNotIn("--copy", readme)
        self.assertNotIn("tree/main/.agents/skills", readme)
        self.assertNotIn("tree/main/.codex/skills", readme)
        self.assertNotIn("tree/main/.claude/skills", readme)


if __name__ == "__main__":
    unittest.main()
