# Teaching, feedback, and continuation

## Teach one observable capability at a time

Read the saved lesson and learner state. Briefly recall the necessary prerequisite, explain the mechanism, walk through a small example, and ask the learner to perform a different task. Do not spend the entire session reprinting the roadmap. Match explanation depth to observed answers, not a guessed personal profile.

Start with hints when the learner is trying to solve an exercise. A useful sequence is conceptual hint → relevant interface/pseudocode → small fragment → full worked solution when asked. After a full solution, provide a changed problem to check independent transfer. Do not withhold an answer when the user explicitly asks for it.

## Feedback records

Distinguish conceptual errors, implementation errors, tool/environment failures, and missing evidence. Feedback should state what was observed, why it matters, the smallest repair, and the next check. A submitted command output is evidence of that run, not proof that all unstated tests pass. If the agent executes code, record the actual command and concise result; do not store hidden reasoning or secrets.

## Progress states

Use `not_started`, `in_progress`, `needs_review`, `passed`, and `skipped`. A pass requires a non-empty evidence record. Mark whether assistance was `independent`, `assisted`, `self_reported`, or `not_assessed`; a self-report must not be presented as independently verified.

A checkpoint uses `schema_version`, `course_id`, `updated_at`, `current_lesson_id`, `lesson_status`, and `next_action`. Preserve stable IDs and prior evidence. Record only relevant learner information. `templates/progress.json` is a blank template, not a record of successful learning.

## Resume

Load `plan.json`, `progress.json`, and the relevant lesson. Validate that IDs belong to the same course before changing them. Continue from the first unmet gate or explicitly recorded next action. When two checkpoints conflict, prefer an identified newer actual file and show the conflict; do not invent reconciliation. The date alone is not proof that a lesson was completed.

No persistent files: produce a short checkpoint the user can save. Never claim automatic memory across unrelated conversations. No background reminders or automatic daily lessons unless the host truly provides and the user explicitly authorizes scheduling.

## Refresh

Recheck only materially affected resources. Reuse prior sources with their actual check dates; do not relabel a cached observation as newly verified. A learner passing a concept need not redo it when only package setup changed. Report changed resource IDs, lesson revisions, and any newly required work.
