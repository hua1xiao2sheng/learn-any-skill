# Selection and scoring rubric

## Hard gates first

Honor cost, access, language, hardware, software version, and format constraints before scoring. A free-only learner must not get a paid required course because it earned a high score. A metadata-only resource is not a verified lesson source. A high-star repository is not automatically well taught or runnable.

## Six subjective dimensions

Use 0–5 only when evidence supports an assessment. The numbers are declared judgments, not objective measurements or a trained quality model.

| Dimension | Weight | Interpretation |
|---|---:|---|
| authority | 0.20 | Provenance and accountability for the topic |
| relevance | 0.25 | Coverage of the required capability nodes |
| practicality | 0.20 | Appropriate exercises, code, worked examples, or reproducible experiments |
| currency | 0.15 | Suitability for the intended concepts/API versions, not merely recency |
| learner_fit | 0.15 | Match to prerequisites, depth, language, and goal |
| accessibility | 0.05 | Permitted access, setup burden, and affordability |

Suggested anchors: 0 = demonstrably unsuitable on this dimension; 1 = major shortcomings; 2 = limited; 3 = adequate; 4 = strong; 5 = unusually well aligned. **Unknown is not 0**. Leave scores absent and explain uncertainty when evidence is insufficient.

The helper computes `100 × Σ(normalized_weight × score / 5)`. A partial custom weight mapping replaces those dimensions' default weights, then renormalizes the full mapping. `{}` means default weights; `null`, arrays, booleans, negatives, non-finite values, and an all-zero mapping are invalid. Ties retain input order; ranking uses unrounded totals, while display uses one decimal place.

`score_resources.py` accepts the v0.1 list/object format and the richer v0.2 ledger if every resource has all six scores. It deliberately **does not** enforce access or evidence status, fetch URLs, or select a curriculum. Apply those hard gates as a separate step. Do not interpret ranked synthetic fixtures as real course recommendations.

## Coverage-aware selection

For each candidate, map exact sections to capabilities. Start with a source providing the best useful coverage for this learner. Add a source only when it fills a missing requirement or provides genuinely different practice. Prefer a lower-scoring source with unique coverage over another high-scoring duplicate. Record skipped chapters and the reason.

Typically keep 2–4 core/practice sources; this is a heuristic, not a guarantee or universal cap. When a user's limit is impossible, identify the uncovered capability and propose narrowing scope instead of pretending it is covered.

A selected resource can be `core`, `practice`, or `optional`; a rejected one is `skip`. Optional work is outside the main time budget unless explicitly scheduled. If it appears in `selected_resource_ids` and a lesson, its hours count like any other work.

## Source-type caution

Official docs may be accurate but unsuitable as a first explanation. University courses may include unnecessary breadth. A paper may require more prerequisites than the learner has. Commercial courses must be judged by inspected material, not sales promises. A GitHub README does not establish code execution. Videos without inspectable chapters cannot support invented timestamp recommendations.

When ranking a v0.2 ledger, the helper preserves its top-level schema/fixture metadata and adds an optional `total_score` field to each resource; the ranked result still conforms to the resource schema. This does not upgrade its verification status.
