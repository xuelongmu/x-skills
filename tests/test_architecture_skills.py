from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"


def read(skill: str, relative: str = "SKILL.md") -> str:
    return (SKILLS / skill / relative).read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def description(skill: str) -> str:
    text = read(skill)
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not match:
        raise AssertionError(f"Missing frontmatter: {skill}")
    lines = match.group(1).splitlines()
    collecting = False
    parts: list[str] = []
    for line in lines:
        if line.startswith("description:"):
            collecting = True
            value = line.partition(":")[2].strip()
            if value not in {">-", ">", "|", "|-"}:
                parts.append(value.strip('"'))
            continue
        if collecting:
            if line.startswith("  "):
                parts.append(line.strip())
            else:
                break
    return " ".join(parts)


class ArchitectureSkillBehaviorTests(unittest.TestCase):
    def test_routing_cross_service_durable_execution_to_design(self) -> None:
        """A new durable execution model across services is architecture design."""
        route = description("design-architecture")
        self.assertIn("service", route)
        self.assertIn("durable workflows", route)
        self.assertIn("important choices are still open", route)

    def test_routing_local_function_extraction_away_from_design(self) -> None:
        """Extracting one local function stays with ordinary implementation work."""
        route = description("design-architecture")
        self.assertIn("not for routine implementation planning", route)
        self.assertIn("small local refactors", route)

    def test_unfamiliar_billing_uses_a_blindspot_decision_map(self) -> None:
        """A driver unfamiliar with billing gets grounded choices, not a quiz."""
        entrypoint = read("design-architecture")
        surfaces = read("design-architecture", "references/decision-surfaces.md")
        self.assertIn("turn unknown unknowns into decisions", entrypoint)
        self.assertIn("decision map, not a lesson", surfaces)
        self.assertIn("recommended default", surfaces)
        self.assertIn("falsification test", surfaces)
        self.assertIn("judgment call under judgment decisions", surfaces)
        self.assertIn("rationale and reversal trigger", surfaces)
        self.assertIn("assumption only when evidence can falsify", surfaces)

    def test_existing_proposal_handoff_survives_missing_review_skill(self) -> None:
        """A selective install returns an actionable fallback instead of a dead route."""
        entrypoint = compact(read("design-architecture"))
        self.assertIn("when that skill is available", entrypoint)
        self.assertIn("Review handoff required", entrypoint)
        self.assertIn("install or enable `review-architecture`", entrypoint)
        self.assertIn("Do not emulate its verdict", entrypoint)

    def test_library_only_options_are_not_distinct_architectures(self) -> None:
        """Two queue libraries inside one ownership model collapse to one design."""
        comparison = read(
            "design-architecture", "references/consequence-analysis.md"
        )
        self.assertIn("library, vendor product, transport", comparison)
        self.assertIn("collapse the pair into one architecture", comparison)
        self.assertIn("ownership/boundary/state/execution", comparison)

    def test_missing_unknown_outcome_semantics_is_reviewable(self) -> None:
        """A technical plan that ignores timed-out provider effects earns a finding."""
        entrypoint = compact(read("review-architecture"))
        lenses = read("review-architecture", "references/review-lenses.md")
        findings = compact(
            read("review-architecture", "references/findings-and-verdict.md")
        )
        self.assertIn("timeout, and unknown outcomes", entrypoint)
        self.assertIn("timeout with unknown outcome", lenses)
        self.assertIn("name the exact unknown state", findings)

    def test_speculative_hundred_x_scale_concern_is_suppressed(self) -> None:
        """A 100x warning without baseline evidence is not a consequential finding."""
        entrypoint = compact(read("review-architecture"))
        findings = compact(
            read("review-architecture", "references/findings-and-verdict.md")
        )
        self.assertIn("speculative scaling concerns without a", entrypoint)
        self.assertIn("measured baselines", findings)
        self.assertIn("unbounded future scale story", findings)

    def test_accepted_adr_requires_new_basis_to_revisit(self) -> None:
        """An accepted ADR is stable absent evidence, changed constraints, or supersession."""
        entrypoint = compact(read("review-architecture"))
        self.assertIn("Do not re-litigate", entrypoint)
        self.assertIn("new evidence, a changed constraint", entrypoint)
        self.assertIn("explicit supersession proposal", entrypoint)

    def test_adr_draft_review_separates_assumptions_from_decisions(self) -> None:
        """Unknown provider behavior is an assumption; write ownership is a decision."""
        findings = compact(
            read("review-architecture", "references/findings-and-verdict.md")
        )
        self.assertIn("Do not mislabel a judgment decision as an assumption", findings)
        self.assertIn("who owns writes", findings)
        self.assertIn("provider retry behavior", findings)

    def test_design_hands_accepted_direction_to_existing_adr_process(self) -> None:
        """Design produces pending history and waits for driver acceptance."""
        entrypoint = read("design-architecture")
        brief = read("design-architecture", "references/decision-brief.md")
        self.assertIn("Only after explicit acceptance", entrypoint)
        self.assertIn("existing `write-adr` skill or ADR process", entrypoint)
        self.assertIn("Driver decision", brief)
        self.assertIn("`Pending`", brief)
        self.assertIn("Do not include implementation code", brief)

    def test_review_is_report_only_and_cross_model_is_per_invocation(self) -> None:
        entrypoint = read("review-architecture")
        self.assertIn("Review is report-only", entrypoint)
        self.assertIn("opt-in for each invocation", entrypoint)
        self.assertIn("exact prompt, tool or provider", entrypoint)
        self.assertIn("read-only boundary", entrypoint)

    def test_progressive_references_are_present_and_discoverable(self) -> None:
        expected = {
            "design-architecture": {
                "references/decision-surfaces.md",
                "references/consequence-analysis.md",
                "references/decision-brief.md",
                "references/project-invariants.md",
            },
            "review-architecture": {
                "references/review-lenses.md",
                "references/findings-and-verdict.md",
                "references/project-invariants.md",
            },
        }
        for skill, references in expected.items():
            with self.subTest(skill=skill):
                entrypoint = read(skill)
                for reference in references:
                    self.assertTrue((SKILLS / skill / reference).is_file())
                    self.assertIn(reference, entrypoint)

    def test_project_lens_is_evidence_activated_and_codebase_agnostic(self) -> None:
        for skill in ("design-architecture", "review-architecture"):
            with self.subTest(skill=skill):
                entrypoint = read(skill)
                lens = compact(read(skill, "references/project-invariants.md"))
                self.assertIn("project-invariants.md", entrypoint)
                self.assertIn("named products and providers", entrypoint)
                self.assertIn("tenant isolation", lens)
                self.assertIn("external pricing or metering authority", lens)
                self.assertIn("deliberate provider coupling", lens)
                self.assertIn("expand-contract", lens)
                self.assertIn("do not infer one from a checkout path", lens)
                self.assertIn("do not hard-code these as universal facts", lens.lower())

    def test_review_routes_code_and_meta_review_to_their_owners(self) -> None:
        entrypoint = compact(read("review-architecture"))
        self.assertIn("`review-change` owns general implementation-diff", entrypoint)
        self.assertIn("`review-complexity` owns review-driven accretion", entrypoint)
        self.assertIn("route exploration to `design-architecture`", entrypoint)
        self.assertIn("when that skill is available", entrypoint)
        self.assertIn("Design handoff required", entrypoint)
        self.assertIn("preserve the review verdict", entrypoint)
        self.assertIn("Do not invent the missing", entrypoint)


if __name__ == "__main__":
    unittest.main()
