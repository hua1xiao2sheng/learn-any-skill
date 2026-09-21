# Output contract

## Plan response

Show the target and assumptions, prerequisite map, short selected-resource table with evidence status and exact sections, phased lessons, projects and gates, estimated budget including buffer, what to skip, known gaps, and the first concrete action. Include portable source URLs in file exports. Do not pad every small request with a full report.

## File export

Default to `.learning/<topic-slug>/` in the user's approved workspace, not the installed skill directory. Inspect existing files before updating. A new course should contain:

```text
.learning/<topic-slug>/
├── brief.json
├── resources.json
├── plan.json
├── curriculum.md
├── progress.json
└── lessons/          # Required for build mode; optional for plan mode
    ├── 01-....md
    └── ...
```

A complete course has actual lesson explanations and exercises. A heading-only outline is not a complete course.

## Machine-readable plan

The canonical structure is defined in `schemas/plan.schema.json` at the skill root. Fields:

- `schema_version`: `"0.2"`; `skill`: topic; `mode`: `verified` or `offline`; `language`.
- `budget_hours`, `buffer_hours`: non-negative finite numbers; budget must be positive.
- `max_core_resources`: optional positive integer limiting selected `core` entries.
- `capabilities`: objects with `id`, `title`, `requires` (capability IDs), and `required` boolean.
- `known_capabilities`: confirmed-known IDs from that map.
- `selected_resource_ids`: IDs present in the sibling evidence ledger.
- `lessons`: ordered objects with `id`, `title`, `kind`, ordered `capabilities`, `resource_ids`, `section_refs`, `hours`, `exercise`, `output`, and `exit_criteria`.
- `kind`: `guided`, `independent`, `transfer`, or `review`.
- `hours`: `input`, `practice`, and `assessment`; every scheduled lesson has positive total time.
- `section_refs`: objects with `resource_id` and `section_id` referring to inspected sections. This can be empty for a learner's independent exercise, but never invent source sections.

All selected resources must be used. All required capabilities must be known or scheduled. Lessons must respect prerequisite ordering even within a lesson's capability list. Every new capability needs a referenced resource whose declared `covers` includes it; an original local exercise/reference is permitted. A verified plan may only schedule `content-verified` or inspected `local` sources and verified section locators. Offline plans may use provisional candidates but must report that limitation.

The local validator checks metadata consistency, not truth, pedagogical effectiveness, URL availability, exact weekly calendars, or whether a learner mastered anything. Schemas additionally support editor/CI type checking; neither fetches remote content.

## Course card

Use `templates/lesson.md`. Include the objective, prerequisite, sources and limitations, original explanation, distinct worked example, learner exercise, graduated hints, expected artifact, tests/rubric, and a next-step branch on pass/fail. Keep solutions out of the initial independent exercise unless requested.

## Honest handoff

Report actual written paths and validation commands/results. With no file access, provide inline text and say it was not saved. With no runtime, describe tests as instructions, not successful executions. Do not claim all course lessons are complete when only some were written.
