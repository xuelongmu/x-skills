from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CANONICAL = {
    "drive-agent-orchestrator",
    "google-developer-style",
    "steward-research",
}
VARIANTS = {
    "babysit",
    "browser-evidence",
    "prompt-agent-orchestrator",
    "publish",
}
CODEX_ONLY = {"land"}
CLAUDE_ONLY = {"publish-slack"}


def skill_dirs(container: Path) -> set[str]:
    return {
        child.name
        for child in container.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    }


class SkillLayoutTests(unittest.TestCase):
    def test_inventory_matches_the_audited_layout(self) -> None:
        self.assertEqual(skill_dirs(ROOT / ".agents" / "skills"), CANONICAL)
        self.assertEqual(
            skill_dirs(ROOT / ".codex" / "skills"), VARIANTS | CODEX_ONLY
        )
        self.assertEqual(
            skill_dirs(ROOT / ".claude" / "skills"), VARIANTS | CLAUDE_ONLY
        )

    def test_canonical_skills_have_no_host_source_copies(self) -> None:
        for name in CANONICAL:
            with self.subTest(skill=name):
                self.assertFalse(
                    (ROOT / ".codex" / "skills" / name / "SKILL.md").exists()
                )
                self.assertFalse(
                    (ROOT / ".claude" / "skills" / name / "SKILL.md").exists()
                )
                self.assertTrue(
                    (ROOT / ".agents" / "skills" / name / "agents" / "openai.yaml").is_file()
                )

    def test_intentional_variants_are_not_identical(self) -> None:
        for name in VARIANTS:
            with self.subTest(skill=name):
                codex = (ROOT / ".codex" / "skills" / name / "SKILL.md").read_bytes()
                claude = (ROOT / ".claude" / "skills" / name / "SKILL.md").read_bytes()
                self.assertNotEqual(codex, claude)

    def test_frontmatter_names_match_directories(self) -> None:
        for container in (".agents", ".codex", ".claude"):
            for name in skill_dirs(ROOT / container / "skills"):
                with self.subTest(container=container, skill=name):
                    text = (
                        ROOT / container / "skills" / name / "SKILL.md"
                    ).read_text(encoding="utf-8")
                    match = re.match(r"^---\s+name:\s*([^\r\n]+)", text)
                    self.assertIsNotNone(match)
                    self.assertEqual(match.group(1).strip(), name)
                    self.assertRegex(text, r"(?m)^description:")

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
        self.assertIn("--agent codex", readme)
        self.assertIn("--agent claude-code --copy", readme)


if __name__ == "__main__":
    unittest.main()
