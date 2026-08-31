from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]

CANONICAL = {
    "babysit",
    "browser-evidence",
    "drive-agent-orchestrator",
    "google-developer-style",
    "land",
    "prompt-agent-orchestrator",
    "publish",
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


def frontmatter(skill: Path) -> dict[str, object]:
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise AssertionError(f"Missing YAML frontmatter: {skill}")
    parsed = yaml.safe_load(match.group(1))
    if not isinstance(parsed, dict):
        raise AssertionError(f"Frontmatter must be a mapping: {skill}")
    return parsed


class SkillLayoutTests(unittest.TestCase):
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
                self.assertEqual(data.get("name"), skill.name)
                self.assertRegex(skill.name, name_pattern)
                self.assertLessEqual(len(skill.name), 64)

                description = data.get("description")
                self.assertIsInstance(description, str)
                self.assertGreater(len(description.strip()), 0)
                self.assertLessEqual(len(description), 1024)

                if "compatibility" in data:
                    self.assertIsInstance(data["compatibility"], str)
                    self.assertLessEqual(len(data["compatibility"]), 500)
                if "metadata" in data:
                    self.assertIsInstance(data["metadata"], dict)
                    self.assertTrue(
                        all(
                            isinstance(key, str) and isinstance(value, str)
                            for key, value in data["metadata"].items()
                        )
                    )
                if "allowed-tools" in data:
                    self.assertIsInstance(data["allowed-tools"], str)

    def test_openai_metadata_is_consistent(self) -> None:
        for skill in all_skill_paths():
            metadata = skill / "agents" / "openai.yaml"
            if not metadata.is_file():
                continue
            with self.subTest(skill=skill.relative_to(ROOT)):
                data = yaml.safe_load(metadata.read_text(encoding="utf-8"))
                interface = data["interface"]
                self.assertTrue(25 <= len(interface["short_description"]) <= 64)
                self.assertIn(f"${skill.name}", interface["default_prompt"])

    def test_land_bundles_watcher_under_scripts(self) -> None:
        watcher = ROOT / ".agents" / "skills" / "land" / "scripts" / "land_watch.py"
        self.assertTrue(watcher.is_file())
        self.assertFalse(
            (ROOT / ".agents" / "skills" / "land" / "land_watch.py").exists()
        )
        for name in ("babysit", "land"):
            text = (
                ROOT / ".agents" / "skills" / name / "SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn("scripts/land_watch.py", text)
            self.assertNotIn(".codex/skills/land", text)

    def test_land_absorbs_slack_sharing_and_native_autofix(self) -> None:
        land = (ROOT / ".agents" / "skills" / "land" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Share the PR in Slack", land)
        self.assertRegex(land, r"Auto-fix CI &\s+address comments")
        self.assertIn("Auto-merge when ready", land)
        self.assertIn("authorizes the Slack phase, not merging", land)
        self.assertFalse(
            (ROOT / ".claude" / "skills" / "publish-slack" / "SKILL.md").exists()
        )

    def test_documentation_uses_cli_only_for_install_lifecycle(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        layout = (ROOT / "docs" / "skill-layout.md").read_text(encoding="utf-8")
        combined = f"{readme}\n{layout}"

        for stale_recipe in ("New-Item -ItemType Junction", "ln -s ", "Copy-Item", "cp -R "):
            with self.subTest(recipe=stale_recipe):
                self.assertNotIn(stale_recipe, combined)

        self.assertIn("npx skills add", readme)
        self.assertIn("npx skills update", readme)
        self.assertIn("npx skills remove", readme)
        self.assertIn("--agent codex claude-code", readme)
        self.assertNotIn("--copy", readme)
        self.assertNotIn("tree/main/.codex/skills", readme)
        self.assertNotIn("tree/main/.claude/skills", readme)


if __name__ == "__main__":
    unittest.main()
