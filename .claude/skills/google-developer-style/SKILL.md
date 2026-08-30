---
name: google-developer-style
description: Draft, revise, or review English developer documentation in Google developer documentation style. Use for tutorials, procedures, concepts, API or CLI reference, UI instructions, and editorial audits; project-specific guidance takes precedence.
license: CC-BY-4.0
argument-hint: "[documentation, path, or review request]"
---

# Write Google-style developer documentation

Use `$ARGUMENTS` as the documentation, path, or editorial request.

Make technical content clear, direct, consistent, accessible, and useful to a
global audience without changing its technical meaning.

## Establish authority

- Follow the user's instructions and the target project's style, terminology,
  templates, and format before this skill.
- Treat the Google guide as a house style, not an objective standard. Depart
  from it when that improves clarity for the actual audience, and be consistent.
- Preserve commands, examples, links, anchors, product names, and markup unless
  changing them is in scope. Surface technical ambiguity instead of guessing.
- Verify unstable facts, commands, APIs, and UI labels separately. Editorial
  fluency does not prove technical correctness.

## Apply the essential style

- Address the reader as **you**. Prefer active voice and present tense.
- Use conversational, friendly, respectful US English. Prefer familiar,
  precise words and short sentences over jargon, formality, or cleverness.
- Put the outcome or critical information first. Put a condition before the
  instruction that depends on it. Give each paragraph one main idea.
- Use one term, spelling, and capitalization for one concept. Define unfamiliar
  abbreviations and replace ambiguous pronouns with the specific noun.
- Write for translation and inclusion: avoid idioms, slang, culture-specific
  references, forced humor, and ableist, violent, or unnecessarily gendered
  language. Use diverse fictional examples and never expose personal data.
- Do not call work easy, simple, obvious, quick, or trivial. Avoid routine
  **please**, **let's**, excessive claims, and unsupported future promises.
- Distinguish obligation precisely: use an imperative or **must** for a required
  action, **can** for an option, **might** for a possibility, and an explicit
  recommendation for preferred but optional guidance. Avoid ambiguous **should**.

## Structure for scanning and access

- Use sentence case. Start task headings with a base-form verb; use noun phrases
  for conceptual headings. Keep heading levels logical.
- Use numbered lists for sequences, bullets for unordered items, and tables for
  items with several comparable properties. Keep list items parallel.
- Introduce lists, tables, code samples, and procedures with a complete sentence.
- Keep required context on the page. Use concise, descriptive link text and link
  to the most relevant destination.
- Format code-related identifiers and literal input as code. Bold visible UI
  labels. Use semantic Markdown or HTML rather than visual-only formatting.
- Do not rely on color, position, shape, sound, punctuation, or an image alone.
  Refer to controls by their accessible label. Give meaningful images alt text
  and equivalent prose; do not use images for text, code, or terminal output.

## Write procedures and technical examples

- Put prerequisites and consequential warnings before the actions they govern.
- Use numbered steps for a sequence. Begin each step with an imperative and
  normally keep one coherent user action per step. Mark optional steps clearly.
- Prefer one short, accessible path. Separate genuinely different environments
  or methods instead of mixing branches into individual steps.
- State the goal when UI mechanics are obvious; otherwise use the exact visible
  label and enough interaction detail to find the control.
- Follow the project's language-specific code style. Keep samples focused but
  runnable, explain descriptive placeholders near their first use, and use
  reserved fictional data. Test examples when practical.
- For API reference, document every public item the generator supports. Describe
  methods in third-person present tense by what they do, and make deprecations
  name a replacement or migration path when one exists.

## Review and deliver

Prioritize findings in this order: technical correctness, task completion,
safety and accessibility, clarity and structure, then mechanics. Distinguish a
project requirement or objective defect from a Google-style recommendation or
optional improvement. For each finding, give a location, reader impact, and
specific fix.

Return the requested artifact or review, not a narration of the editing process.
When editing repository files, run available documentation checks and inspect
rendered output when layout, links, tables, or images changed.

For an exact or current ruling, consult the live
[Google developer documentation style guide](https://developers.google.com/style),
especially its [highlights](https://developers.google.com/style/highlights),
[word list](https://developers.google.com/style/word-list),
[procedures](https://developers.google.com/style/procedures),
[code guidance](https://developers.google.com/style/code-in-text), and
[accessibility guidance](https://developers.google.com/style/accessibility).
This skill paraphrases and reorganizes that guide under CC BY 4.0.
