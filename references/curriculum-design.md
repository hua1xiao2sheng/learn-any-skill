# Curriculum construction

## Define a capability rather than a topic

Weak: “Learn RAG.” Strong: “Build a retrieval pipeline, evaluate retrieval separately from answer quality, diagnose failures, and compare one controlled change.” Do not turn “research readiness” into a guarantee of a publishable idea.

Build a directed acyclic prerequisite graph. Known prerequisites may be skipped when the learner explicitly confirms them or demonstrates them; a degree is not proof. Keep optional extensions separate from the minimum path.

## Compose lessons, not a link dump

Each lesson contains an original short explanation connecting the selected sections, a worked example, an exercise on different inputs, an artifact, and pass criteria. Source sections may be reordered to respect prerequisites. Explain transitions: what the previous lesson made possible and why the next concept is needed.

Start from a small runnable slice rather than a large production repository when the learner lacks a system map. Advanced learners may start by tracing a real codebase. Do not require rebuilding an entire industrial framework from scratch; isolate the mechanism being learned.

## Practice ladder

Guided work teaches one mechanism with scaffolding. Independent work removes the solution walkthrough but permits API docs. Transfer changes the data, interface, constraint, or failure mode. Debugging should include an intentional failure and a test that would catch it. Tailor this ladder to the skill; non-programming skills need domain-appropriate observable work, not artificial coding projects.

For AI-assisted learning, distinguish code written by the agent from code independently produced by the learner. Running agent-written code is useful practice but is not evidence of independent mastery.

## Time accounting

Track input, practice, and assessment separately. Include installation/debugging in practice or an explicit buffer. `budget_hours` includes `buffer_hours`; therefore `sum(lesson hours) + buffer_hours <= budget_hours`.

Do not equate video runtime with learning time. Use ranges in narrative estimates and a clearly labeled planning estimate in machine-readable totals. The defaults are planning heuristics, not empirically guaranteed compression ratios. Recalibrate after observing the learner's first task.

When over budget: remove optional material, shrink the capstone, or narrow the target. Do not remove all testing, prerequisite instruction, or recovery time just to claim the deadline is met.

## Research and production extensions

Research: primary sources, a reproducible baseline, a stated hypothesis, controlled comparisons, resource requirements, and uncertainty. Production: reliability, observable traces/metrics, tests, cost/performance, deployment assumptions, and failure recovery. Add these only when the user requests that depth.

## Revising a course

Preserve IDs and completed work. Describe which requirement changed, which resources/lessons are affected, and whether a learned concept or just an API example needs updating. Do not restart the course merely because a different resource looks newer.
