from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml
from skills_ref import validate


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"


def skill_dirs(container: Path) -> list[Path]:
    # Include directories missing SKILL.md so validation reports broken packages.
    return sorted(path for path in container.glob("*") if path.is_dir())


def validate_skill(skill: Path) -> list[str]:
    errors = validate(skill)
    if errors:
        return errors

    # Upstream StrictYAML treats scalar values as strings and does not enforce
    # metadata or allowed-tools types. Check those gaps using YAML scalar types.
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    data = yaml.safe_load(text.split("---", 2)[1])
    for field in ("name", "description", "license", "compatibility", "allowed-tools"):
        if field in data and not isinstance(data[field], str):
            errors.append(f"{field} must be a string")
    if "metadata" in data:
        metadata = data["metadata"]
        if not isinstance(metadata, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in metadata.items()
        ):
            errors.append("metadata must map strings to strings")
    return errors


class SkillLayoutTests(unittest.TestCase):
    def test_canonical_layout(self) -> None:
        self.assertTrue(skill_dirs(SKILLS), "No canonical skills found")
        for host in (".codex", ".claude"):
            self.assertEqual(skill_dirs(ROOT / host / "skills"), [])
        for skill in skill_dirs(SKILLS):
            with self.subTest(skill=skill.name):
                self.assertFalse(skill.is_symlink() or skill.is_junction())
                self.assertTrue((skill / "SKILL.md").is_file())

    def test_every_skill_validates(self) -> None:
        for skill in skill_dirs(SKILLS):
            with self.subTest(skill=skill.name):
                self.assertEqual(validate_skill(skill), [])

    def test_validation_covers_upstream_type_gaps(self) -> None:
        cases = (
            ("description: 123", "description must be a string"),
            ("metadata: invalid", "metadata must map strings to strings"),
            ("metadata:\n  enabled: true", "metadata must map strings to strings"),
            ("metadata:\n  123: value", "metadata must map strings to strings"),
            ("allowed-tools:\n  - Bash", "allowed-tools must be a string"),
            ('description: "123"', None),
            ('metadata:\n  version: "2"', None),
        )
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "example"
            skill.mkdir()
            for field, error in cases:
                with self.subTest(field=field):
                    description = "" if field.startswith("description:") else "description: Example\n"
                    (skill / "SKILL.md").write_text(
                        f"---\nname: example\n{description}{field}\n---\nInstructions.\n",
                        encoding="utf-8",
                    )
                    self.assertEqual(validate_skill(skill), [error] if error else [])

    def test_openai_metadata_is_consistent(self) -> None:
        for skill in skill_dirs(SKILLS):
            metadata = skill / "agents" / "openai.yaml"
            if not metadata.is_file():
                continue
            with self.subTest(skill=skill.name):
                data = yaml.safe_load(metadata.read_text(encoding="utf-8"))
                interface = data["interface"]
                short_description = interface["short_description"]
                default_prompt = interface["default_prompt"]
                self.assertIsInstance(short_description, str)
                self.assertIsInstance(default_prompt, str)
                self.assertTrue(25 <= len(short_description) <= 64)
                self.assertIn(f"${skill.name}", default_prompt)


if __name__ == "__main__":
    unittest.main()
