# Checks on the exported files and evidence

The evidence was captured on October 7, 2026. The plain-English revision was checked
against the original package at commit `ba3839a`. All files are local; the package
has not been submitted, pushed to GitHub, or sent to anyone. Access settings and
office-hours bookings were not changed.

## Evidence checks

- `collect_evidence.py` executed the project suite: 51 passed with one upstream
  Starlette/httpx deprecation warning. The captured test log is in `evidence/`.
- All 20 source/result SHA-256 entries in `evidence/manifest.json` matched their files.
  The original implementation is `125aa40`; initial requirements mapping is `4caa821`;
  curated dossier and evidence are committed in `133eade`.
- Model results, the rule for choosing a model, test-row counts, prediction-range
  coverage, and variation from filling missing data agree with the source tables.
- The biased-neighbor test uses a separate simple formula. Deliberately wrong
  predictions come from test substitutes. Fictional permits are marked as examples.
- Shaun's coding lead is user-confirmed. Supporting work for Troy/Scott is assigned,
  with confirmation of actual completed contributions still required.

## File and layout checks

- Dossier PDF: 8 letter-size pages. Checkoff PDF: 3 letter-size pages. Every page was
  rendered and visually inspected for tables, diagram labels, page breaks, and footers.
- Presentation: 6 slides at 16:9. Every final slide was rendered and reviewed.
  Diagram labels, text wrapping, spacing, and arrow direction were checked. The
  standalone map also exists as SVG/PNG.
- The presentation export passed checks on PPTX structure, slide size/count, heading
  placement, Arial font declarations, and reopening through the authoring tool.
- Three charts remain editable, with embedded workbooks. Their stored values and
  workbook references passed checks. Chart numbers use ten significant digits to
  stay within Excel's precision limit; source CSVs keep their original precision.
- All six slide-PDF images match the reviewed final slide renders pixel for pixel.
  That PDF contains pictures of slides; use the PPTX to edit text, diagrams, or charts.
- Opening in PowerPoint or Google Slides was not tested. The export checks do not
  guarantee identical appearance in every application.
- Both Python authoring/capture scripts pass Ruff checks and formatting. The wording
  revision changes documentation and exports; core implementation files are unchanged.
- The packaging script also passes Ruff. PDF/PPTX/PNG/ZIP files have explicit binary
  Git attributes to preserve their exact bytes across Windows checkouts.

Final editable-deck SHA-256 fingerprint:
`42c9fca3141627dedf24b4a1f77a71872e4a9b06857c48752e34dc5dad4c8dfe`.
Detailed export receipts stay in `data/processed/a2-build/slides/`.

The bundled Poppler wrapper could not find its executable. PDFium rendered the
pages and ReportLab generated the PDFs. No installation or application-setting
changes were needed.

## Checks that the simpler wording keeps the content

- All 15 raw evidence files match the original Git contents. Text comparisons
  account for Git's LF line endings and the Windows checkout's CRLF line endings;
  all 20 recorded SHA-256 fingerprints still match the actual files byte for byte.
- All 21 course checklist items and all seven evidence-table IDs, decisions, and
  evidence paths are preserved.
- All nine numeric dossier-table rows, 33 code/evidence references, and 13 numbers
  in the three editable charts are unchanged.
- Command and schema code blocks in the project README, data contracts, and review
  README are unchanged.
- The plain-English guide adds a short explanation, step-by-step walkthrough,
  experiment summaries, handoffs, and a glossary. The presentation script contains
  552 spoken words over 240 seconds, about 138 words per minute. Technical evidence
  notes and the simpler script are both included in the editable deck's speaker notes.
- The existing 51-test capture is preserved. The core suite was not rerun solely
  for this wording revision. A local comparison receipt is saved as
  `data/processed/a2-build/simplification-verification.json`.

## Human/course checks still pending

Confirm the assigned October 20/23 presentation day, exact Submitty deadline, actual
completed contributions, class studio links, instructor/TA GitHub access, office hours,
and rehearsal. The ZIP is a prepared handoff bundle; it has not been submitted.
