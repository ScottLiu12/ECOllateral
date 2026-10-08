# Export verification and evidence limits

Verified October 7, 2026. All deliverables are local files; no course submission,
GitHub push, external message, access change, or office-hours booking was performed.

## Evidence checks

- `collect_evidence.py` executed the project suite: 51 passed with one upstream
  Starlette/httpx deprecation warning. The captured test log is in `evidence/`.
- All 20 source/result SHA-256 entries in `evidence/manifest.json` matched their files.
  The original implementation is `125aa40`; initial requirements mapping is `4caa821`;
  curated dossier and evidence are committed in `133eade`.
- Selected model values, calibration-selection criteria, held-out row counts, interval
  coverage, and imputation variances agree across the dossier and source tables.
- The biased-donor diagnostic is explicitly a separate simple predictor. Fault
  injection explicitly uses stub predictions. Fictional permits remain marked examples.
- Shaun's coding lead is user-confirmed. Supporting work for Troy/Scott is assigned,
  with confirmation of actual completed contributions still required.

## Artifact checks

- Dossier PDF: 8 letter-size pages. Checkoff PDF: 3 letter-size pages. Every page was
  rendered and visually inspected for tables, diagram labels, page breaks, and footers.
- Presentation: 6 slides at 16:9. All finalized slides rendered; visual review corrected
  wrapping in the system map and arrow direction. The map also exists as SVG/PNG.
- The finalizer passed PPTX structural integrity, slide size/count, heading geometry,
  uniform Arial font declarations, and first-party reimport.
- Three charts remain native/editable, with embedded workbook snapshots and verified
  chart cache/reference ranges. Numeric values use ten significant digits to stay
  within Excel's precision limit. Full-precision source CSVs remain unchanged.
- The slide PDF embeds the reviewed final slide images. PDF slide text is rasterized;
  use the PPTX to edit text, diagrams, or chart data.
- Native PowerPoint/Google Slides opening and native font rendering were not tested.
  Structural and rendered checks are not a guarantee of every application's behavior.
- Both Python authoring/capture scripts pass Ruff checks and formatting. No core
  implementation files were changed for this documentation task.
- The packaging script also passes Ruff. PDF/PPTX/PNG/ZIP files have explicit binary
  Git attributes to preserve their exact bytes across Windows checkouts.

Final editable-deck SHA-256:
`f78087056ef1e120500ca59a07e41345554268c503b24fcadc0fc5121231d7f2`.
Detailed machine receipts stay in `data/processed/a2-build/slides/`.

The bundled Poppler wrapper could not resolve its executable on this host. PDFium
provided page renders instead; ReportLab generated the PDFs. No dependency installation
or user application setting changes were needed.

## Human/course checks still pending

Confirm the assigned October 20/23 presentation day, exact Submitty deadline, actual
completed contributions, class studio links, instructor/TA GitHub access, office hours,
and rehearsal. The ZIP is a prepared handoff bundle; it has not been submitted.
