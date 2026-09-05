from __future__ import annotations

import re
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def missing_resources(root: Path) -> list[str]:
    missing: list[str] = []
    for source in root.rglob("*.md"):
        for raw in LINK.findall(source.read_text(encoding="utf-8")):
            target = raw.strip("<>")
            if target.startswith("#") or urlsplit(target).scheme:
                continue
            path = unquote(target.split("#", 1)[0])
            if path and not (source.parent / path).exists():
                missing.append(f"{source.relative_to(root)} -> {path}")
    return missing


class SkillResourceTests(unittest.TestCase):
    def test_bundled_relative_resources_resolve(self) -> None:
        self.assertEqual(missing_resources(SKILLS), [])

    def test_resources_resolve_after_relocated_installation(self) -> None:
        # The same canonical directories install under either host's layout.
        # Include siblings because publication and babysitting depend on land.
        with tempfile.TemporaryDirectory() as directory:
            relocated = Path(directory) / "installation with spaces" / "skills"
            shutil.copytree(SKILLS, relocated)
            self.assertEqual(missing_resources(relocated), [])

    def test_audit_detects_a_missing_relative_resource(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text(
                "[missing](references/absent.md)\n"
                "[web](https://example.com/guide)\n"
                "[section](#scope)\n",
                encoding="utf-8",
            )
            self.assertEqual(
                missing_resources(root), ["SKILL.md -> references/absent.md"]
            )


if __name__ == "__main__":
    unittest.main()
