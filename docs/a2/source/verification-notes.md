# Export and evidence checks

Evidence snapshot: October 7, 2026. Refactor and report revision: October 14, 2026.
The original development/export log is available with
`git show dbb9cf9:docs/implementation-notes.md`.

- Original raw experiment files and manifest are retained in `../evidence/`.
  Their source hashes refer to implementation `125aa40`, not the refactored source.
- All four dossier result/decision tables, the timed talk, and the 21 course checkoff
  items are retained. Current source references point to consolidated modules.
- The dossier is four letter-size pages; checkoff three. Both use black-and-white
  formatting and standard fonts. Every exported page was rendered and visually reviewed.
  Editable map labels and connectors remain; its SVG/PNG use neutral colors.
- The existing six-slide deck, three editable charts, speaker notes, and slide PDF
  remain unchanged. Original method notes describe the October 7 implementation;
  code mentioned there can be read at that commit. Native PowerPoint opening was not tested.
- Current verification: 52 tests pass, Ruff lint/format checks pass, TypeScript checking
  passes, and the research notebook executes. A separate evidence-capture run succeeds
  in the ignored `data/processed/refactor-check/evidence/` folder.
- Report rebuilding exports dossier/checkoff and the map. Edit/export slides directly
  in PowerPoint; the builder no longer stitches potentially stale cached slide images.
- Generated training/research values remain software checks, not field validation.
  Supporting team duties, course dates/deadlines, instructor access, and rehearsal
  still need human confirmation. No submission or external messages were sent.
