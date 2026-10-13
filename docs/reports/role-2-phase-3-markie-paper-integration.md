# Role 2 Phase 3 Report: Professor and Portfolio Paper Drafts

**Owner:** Markie
**Date:** 2026-10-13
**Status:** In progress; both manuscript drafts ready for review, final evaluation integration pending.
**Branch:** feature/role-2-backend-bridge

## Deliverables

| Format | Manuscript text | Editable Word manuscript | Pages |
|---|---|---|---|
| Professor, primary graded deliverable | `docs/reports/paper.md` | `docs/reports/paper-draft.docx` | 25 |
| Portfolio, supplemental academic deliverable | `docs/reports/paper-portfolio.md` | `docs/reports/paper-portfolio-draft.docx` | 24 |

Both versions follow `docs/reports/paper_structure.md` and use the same experiments and evidence. The portfolio expansion introduces no new experiments or unsupported outcomes. The earlier user preference for 12-point body text was superseded by the request to follow the repository format.

## Formatting and completed writing

Professor: Times New Roman 11-point body, 1.5 spacing, one-inch margins, bottom-center page numbers, Roman top-level sections I–X, and Arabic decimal subsections. Model sections distinguish description, configuration, training procedure, and results. The 41-feature dictionary includes a role column. Search-space tables and the pending training-versus-validation comparison are included. The six-question Executive Summary fits one page.

Portfolio: Times New Roman 11-point body, one column, 1.15 spacing, one-inch margins, bottom-center page numbers, and Arabic decimal numbering. Includes a 250-word structured abstract, keywords, Introduction, Background and Related Work, Dataset and Preprocessing, Methodology with formal notation, Experiments, Results, Explainability Analysis, Discussion with Threats to Validity, Conclusion and Future Work, Acknowledgments, References, AI disclosure, and Appendices A–C.

Both use 0.5-inch first-line body paragraph indents, no first-line indent for headings/captions/table cells, and hanging reference indents. Main headings are larger and bold. References apply APA author-year conventions and title/publication italics. Technical sections use formal academic prose without personal-name attribution, handoff updates, PR numbers, or approval-status narrative.

## Evidence and limitations

Preparation statistics, model protocols, backend implementation, 13 functional checks, and the real RF API smoke test remain source-attributed. RF training values and selected parameters are traced to the model sidecar and execution record in PR #13, commit 3706260. Cross-validation and out-of-bag scores remain distinct from pending test metrics. The RF validation standard deviation exceeds the specified threshold and is retained as a limitation. TabNet cumulative intermediate means are not treated as independent fold scores.

The expanded background cites the original Random Forest, XGBoost, TabNet, and SHAP papers, NIST SP 800-94, and the official KDD Cup archive. Published methods motivate the comparison; no directly comparable numerical literature baseline or model winner is invented.

## Remaining dependencies

Complete XGBoost artifacts/results; verified TabNet validation statistics; held-out evaluation and explanation figures; runtime and hardware measurements; training acceptance; individual member reflections; full author names, affiliations, corresponding-author contact, professor name, and the original professor cover-page template. The TabNet training/inference scaling discrepancy remains unresolved. Phase 3 stays in progress until final evidence is integrated.

## Verification

Checked font, line spacing, margins, section hierarchy, all 41 feature rows, the abstract word count, captions, and shared numerical claims. The packaged renderer could not locate LibreOffice on this Windows host, so the manuscripts were rendered through Microsoft Word's PDF exporter and rasterized for visual review. Reviewed all 25 Professor pages and 24 Portfolio pages. After final citation/cross-reference edits, pixel comparisons identified three changed Portfolio pages; all three were reinspected, with the remaining pages unchanged.

Only manuscript Word/Markdown copies and this report are committed. QA PDFs, page images, and authoring scripts remain outside the repository. Model binaries are excluded.

## Handoff

Kit can review both versions in PR #14. `paper.md` and `paper-draft.docx` remain the primary professor-format deliverables. The portfolio files are supplemental. Both drafts must be updated from the same verified evaluation artifacts before final submission.
