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
  placement, Georgia/Arial font declarations, and reopening through the authoring tool.
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
`4ba13652d80b698ce942fd51dfa68a8e1b3fe251ca8b1e93111a98d7afe9fd54`.
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
  572 spoken words over 240 seconds, about 143 words per minute. Technical evidence
  notes and the simpler script are both included in the editable deck's speaker notes.
- The existing 51-test capture is preserved. The core suite was not rerun solely
  for this wording revision. A local comparison receipt is saved as
  `data/processed/a2-build/simplification-verification.json`.

## Checks on the requested editorial slide design

- The October 8 design and scope revisions keep six 16:9 slides, three editable charts,
  original component-method notes, and the current region-focused spoken script.
- The canvas is #F9FAFB, primary text #111827, and metadata #6B7280. At the user's
  latest request, all purple circular glows, the shaded sphere, and its orbit were
  removed. Chart bars retain muted lavender #B8ADF3 and gray #D1D5DB. Rules use
  #E5E7EB and title bars are 1.5px. The final slides have no gradient-fill shapes.
- Headings use uppercase Georgia. Body, metadata, chart axes, and legends use Arial.
  Both families were verified in the installed font inventory and final package.
- The slides use a title layout, large stat callouts, open chart/text splits, and an
  unboxed editable process diagram. The final decision slide keeps open whitespace.
- A conservative layout check counts complete text, chart, and illustration bounding
  rectangles as occupied. It excludes diffuse background glows and invisible connector
  anchors. Remaining space is 42.92%, 44.69%, 41.67%, 41.62%, 40.12%, and 54.54% for
  slides 1-6, meeting the requested minimum of 40% on every slide.
- All six final slide layouts were visually reviewed. Repairs removed a glow/chart
  boundary clash and a team-role/question overlap. All six images in the matching
  slide PDF agree pixel for pixel with the reviewed final slide renders.
- Raw evidence, fingerprints, chart numbers, component-method notes, and course
  checklist items are preserved. Purpose, narrative, and next steps were corrected
  to match the user's regional context. The latest comparison receipt is stored in
  `data/processed/a2-build/regional-verification.json`.
- The ZIP excludes temporary Office owner files. An open PowerPoint's owner file
  was preserved locally and ignored in Git. Native PowerPoint/Google Slides opening
  remains outside these export checks.

## Checks on the regional purpose correction

- README, project scope, dossier, slides, script/Q&A, map, checkoff, governance,
  requirements, team duties, evidence descriptions, contracts, validation introduction,
  and package metadata now describe regional ecosystem impacts as the project goal.
- The current cooling model is explicitly a development-pressure component. No
  regional balance, ecosystem score, recharge forecast, or zero-shot LLM benchmark
  is presented as implemented or validated. Groundwater depth and recharge remain distinct.
- All seven evidence-result descriptions retain their original numbers. Existing
  commands, schemas, metric tables, raw evidence, and component-method notes are preserved.
- The package includes `docs/project-scope.md` as its fourth project reference.
  The package metadata change affects only the description; dependencies, version,
  and software behavior are unchanged. Core tests were not rerun for this scope/prose revision.
- Updated team assignments remain duties rather than certified completed work. The
  exact presentation day, deadline, instructor access, and course studio links remain pending.

## Checks against the A2 assignment and section labels

- `slide-coverage.md` maps all seven required presentation topics, all six rubric
  categories, and all five submission components to slides and supporting files.
- Visible headings explicitly identify Problem & Users (1), Semantic Map (2),
  Experiment E1/E2/E5 (3/4/5), and Decisions & Next Question (6). The FAILURE and
  RELIABILITY ISSUE labels appear on slides 4/5; Evidence footers appear on slides 2-5.
- Slide 2 explains the feature/target/rule/vector/document/metadata representations
  and their connections. Concrete fault-injection and location outcomes remain visible.
- Slide 6 separates Adopt, Modify, Reject, and Defer, with evidence IDs and reasons.
  Its next question concerns seasonal reserve/watershed impacts in an unseen area.
- The timing plan totals 240 seconds: 60 for problem/map, 120 for experiments/failures,
  and 60 for decisions/next question. The prepared Q&A supports the two-minute question
  period. Rehearsal is required to verify actual timing and all members' understanding.
- All 15 raw evidence files, 20 fingerprints, 13 chart values, six original component
  notes, and 21 checkoff items passed retention checks. No new experiment or completed
  teammate contribution was fabricated to satisfy the assignment.

## Human/course checks still pending

Confirm the assigned October 20/23 presentation day, exact Submitty deadline, actual
completed contributions, class studio links, instructor/TA GitHub access, office hours,
and rehearsal. The ZIP is a prepared handoff bundle; it has not been submitted.
