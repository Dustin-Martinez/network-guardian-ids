# Role 2 Phase 3 Report: Initial Paper Integration

**Owner:** Markie
**Date:** 2026-10-13
**Status:** In progress; initial manuscript ready for review, final evaluation integration pending.
**Branch:** feature/role-2-backend-bridge

## Deliverables

- `docs/reports/paper.md`: readable manuscript text, tables and source figure links.
- `docs/reports/paper-draft.docx`: matching editable Word manuscript, Times New Roman 12, 1.5 spacing, one-inch margins, justified body with 0.5-inch first-line paragraph indents, hanging reference indents and page numbers.

## Completed drafting

Introduction, data understanding, 41-feature dictionary and observed ranges, preparation methods, model architecture and training protocol, metadata, available preparation figures, Discovery Log, Executive Summary, references and AI disclosure. The backend section now documents the implementation, 13 functional checks and real RF API smoke test. The manuscript is 23 pages at the requested formatting.

RF training values and selected parameters are traced to Amber's model sidecar and execution code in open PR #13, commit 3706260. Cross-validation and out-of-bag scores are labeled separately from pending test metrics. Kit's acceptance of the CV standard-deviation threshold miss is not assumed. Dwayne's TabNet handoff is acknowledged, while its running-mean fold export and summary require reconciliation before a complete numerical comparison.

## Formal editorial revision

Rewrote the technical narrative in formal academic language. Removed member-name attribution, handoff updates, pull-request references and approval-status language from the technical sections. Preserved supported measurements and methodological limitations; unavailable evaluation results remain explicitly pending. Headings, captions and table cells have no first-line indent.

## Remaining dependencies

Kenneth's XGBoost artifacts/results; Dwayne's held-out evaluation and explainability figures; explicit training handoff acceptance; measured runtime; final member reflections and cover-page details. No final winner, new held-out score, or invented personal reflection has been supplied. The TabNet training/inference preprocessing question remains documented for Kit.

## Verification

Checked the updated Word font and spacing, all 41 feature rows and the numerical fields against RF metadata. Rendered through Word's PDF exporter after the packaged renderer could not locate LibreOffice on this Windows host. Visually reviewed all 23 pages; checked that tables, figures, captions, page numbers and placeholders are readable. Only the editable manuscript copies are committed; render intermediates remain outside the repository.

## Handoff

Kit can review the Word draft or comment on the Markdown manuscript in PR #14. The phase remains in progress until the confirmed evaluation handoffs are integrated. This draft does not replace the owning members' measurements or approval decisions.
