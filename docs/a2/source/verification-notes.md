# Current export and evidence checks

Evidence snapshot: October 7, 2026. Document revision: October 8, 2026.
The detailed development history is in `../../implementation-notes.md`.

## Current files and sources

- Main A2 folder: 11 files. Start with `../README.md` for the file index.
- Editable presentation: `../review-slides-simplified.pptx`; matching preview:
  `../review-slides.pdf`. The older deck and duplicate ZIP are removed.
- Editable dossier/checkoff and data-source notes are in this source folder.
  Evidence and document scripts are in `../../../scripts/a2/`.
- The talk, Q&A, simple project guide, and glossary share one presentation script.
  Assignment requirements and slide locations share one coverage guide.
- The presentation itself remains the editable source for slide changes. Current
  validation summaries and reviewed previews are in the ignored build directory.

## What the data support

Current water-use targets and research river data are generated examples for
software checks. The finished model needs measured inputs and outcomes, training
on historical measurements, and testing on separate records and areas. Public
weather and river readings alone do not supply the correct training target.
No measured-target retraining, regional water balance, river-needs assessment,
or ecosystem-health validation is claimed.

The biased-neighbor diagnostic uses a separate simple formula, forced wrong
predictions use test substitutes, and permit examples are fictional. Shaun leads
coding; Troy and Scott's supporting responsibilities still require confirmation
of actual completed contributions. Course timing, access, and rehearsal remain
human checks.

## Content checks

- All 15 raw evidence files match the original version. Text comparisons account
  for Windows/Git line endings; all 20 manifest fingerprints match actual bytes.
- All 21 course checklist items and seven evidence IDs, decisions, and paths remain.
- All nine numeric dossier rows and 13 numbers in three native charts are unchanged.
  All 32 active code/evidence references remain after deleting one obsolete builder reference.
- Command/schema blocks in the project README and data contracts are unchanged.
  The document rebuild command now uses the portable script path.
- All six original component-method notes remain, with updated dossier paths.
  Every slide's notes begin with the current simple talk, then full question details.
- Spoken word counts: 79 / 69 / 108 / 101 / 89 / 158, total 604. Four minutes implies
  about 151 words per minute; rehearse to establish actual timing.
- Problem & Users, Semantic Map, Experiment E1/E2/E5, and Decisions & Next Question
  are visible headings. Evidence labels appear on slides 2-5; failure/reliability
  labels appear on slides 4/5; all four decision categories appear on slide 6.
- Nine map connectors exactly match the previously aligned deck. Their earlier
  adjustment of 8px left and 10px down is preserved.
- All 18 local Markdown links checked resolve to existing files.

## Export and layout checks

- Six 16:9 slides retain native text, nine editable map arrows, three editable charts,
  and embedded workbooks. Structural, size/count, heading-fit, font, chart-data,
  workbook-reference, and file-reimport checks pass.
- Canvas #F9FAFB, text #111827, metadata #6B7280, Georgia headings, and Arial body.
  No gradient shapes remain. Chart bars retain muted lavender/gray.
- Conservative remaining-space estimates are 42.92 / 44.70 / 41.67 / 41.62 / 40.12 /
  54.54 percent. Whole text/chart rectangles count as occupied.
- Final document properties use the project title/team and neutral theme names.
  All presentation XML and three embedded workbooks were inspected.
- Every final slide was rendered and visually inspected. All six images in the
  slide PDF match final renders pixel for pixel.
- Dossier PDF: 8 letter-size pages; checkoff PDF: 3; slide PDF: 6 landscape pages.
  Every page was rendered and checked for labels, table wrapping, breaks, and footers.
- Both retained Python scripts pass Ruff lint and formatting checks.
- The prior 51-test capture remains unchanged. The core suite was not rerun for
  documentation, file organization, and metadata changes; application code is unchanged.
- Opening in native PowerPoint/Google Slides was not tested. Structural/render checks
  do not guarantee identical appearance in every application.

Final editable-deck SHA-256:
`c5b5d7d4b89c92a21632ed1ea3fb5b06ef235c63101ba4bbe099b8f16a8c433b`.

## Cleanup

The main folder went from 23 files to 11. Merged guides retain their full content;
source documents moved rather than disappeared. Removed 147 obsolete build/cache
files (13,574,564 bytes), including draft decks, old chart snapshots, repeated previews,
and pytest/Ruff caches. Required dependencies, source code, notebooks, tests, current
previews, model/data artifacts, and raw evidence remain. Existing Git history is retained.
