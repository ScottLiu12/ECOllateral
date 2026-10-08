# CSCI 4150 A2: ECOllateral evidence review

Prepared against the supplied Fall 2026 project checkoff and A2 brief. This package
explains ECOllateral's regional ecosystem goal, the components we tested, and the limits
of made-up test data. The cooling model is one development-pressure example, not the
project's overall purpose. `../project-scope.md` records the goal and remaining work.
Presentation day is pending: October 20 or October 23, 2026.
The exact Submitty deadline is not supplied in the brief.

## Deliverables

- `explain-it-simply.md`: start here for the short explanation, five system steps,
  experiment takeaways, glossary, and numbers to remember.
- `dossier.md` and `dossier.pdf`: full problem, system/information map, experiments,
  limits, decisions, next question, and team roles in plain English.
- `project-checkoff.md` and `project-checkoff.pdf`: every project checklist item, its
  evidence, and remaining human/course actions.
- `semantic-system-map.svg` and `.png`: how the number and permit paths work together.
- `evidence-summary.csv`: what we tested, what happened, and what we keep/change.
- `review-slides.pptx` and `review-slides.pdf`: six-slide evidence review with the
  requested editorial design: Georgia headings, Arial body text, an off-white canvas,
  charcoal text, thin rules, and open spacing. Circular gradients and the decorative
  sphere were removed at the user's request; comparison bars retain muted colors.
- `presentation-script.md`: four-minute script, slide timing, team handoffs, and Q&A.
  Everyday wording comes first in the deck's notes, followed by full details for questions.
- `team-contributions.md`: Shaun, Troy, and Scott's responsibilities and accountability.
- `data-governance.md`: public sources, where evidence came from, permissions, and limits.
- `requirements-map.md`: A2 requirements and grading criteria mapped to the package.
- `slide-coverage.md`: item-by-item A2 slide/rubric coverage and the remaining human checks.
- `evidence/`: portable benchmark tables, forecast output, failure cases, research charts,
  test output, source metadata, and checksums. No serialized model is included.
- `verification-notes.md`: export checks, visual review, and practical validation limits.
- `submission-package.zip`: deliverables and editable sources plus the four project
  reference documents. Review course logistics before uploading it.

Read `explain-it-simply.md` first, then open `dossier.pdf` for full evidence or
`review-slides.pptx` to edit the presentation. The speaker notes include the spoken script.
The Markdown and CSV files remain editable. `build_materials.py` and `build_slides.mjs`
record how the exports were made; `collect_evidence.py` refreshes inspectable evidence.

## Rebuilding the exports

Refresh evidence using the project virtual environment (see `evidence/README.md`).
Export PDFs using the Codex bundled Python, which includes ReportLab and PDFium.
Export the editable deck using the bundled Node/Artifact Tool and presentation skill.
The current bundled dependency version is 26.904.11930. Adjust the runtime/skill paths
if the app replaces that bundle. Run from the repository root:

```powershell
$taskRuntime = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies'
$env:RUNTIME_PYTHON = Join-Path $taskRuntime 'python/python.exe'
$env:RUNTIME_NODE = Join-Path $taskRuntime 'node/bin/node.exe'
$env:RUNTIME_NODE_MODULES = Join-Path $taskRuntime 'node/node_modules'
$env:SKILL_DIR = Join-Path $env:USERPROFILE '.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations'
$env:WORKSPACE_DIR = (Get-Location).Path
$env:TMP_DIR = Join-Path $env:WORKSPACE_DIR 'data/processed/a2-build/slides'
# Choose an unused output name; the finalizer preserves existing exports.
$env:FINAL_NAME = 'review-slides-rebuilt.pptx'
New-Item -ItemType Directory -Force -Path $env:TMP_DIR | Out-Null
if (-not (Test-Path (Join-Path $env:TMP_DIR 'node_modules'))) {
    New-Item -ItemType Junction -Path (Join-Path $env:TMP_DIR 'node_modules') -Target $env:RUNTIME_NODE_MODULES | Out-Null
}
Copy-Item docs/a2/build_slides.mjs (Join-Path $env:TMP_DIR 'build.mjs')
& $env:RUNTIME_NODE (Join-Path $env:TMP_DIR 'build.mjs')
& $env:RUNTIME_PYTHON docs/a2/build_materials.py
```

The deck builder validates the native charts and renders its finalized output before
the PDF builder embeds those slide renders. The PDF builder exports the two Markdown
documents and the system SVG/PNG. Chart workbooks intentionally round to ten significant
digits; the CSV evidence retains full precision. Reconcile textual figures after new
experiments and visually inspect rebuilt materials. Validation receipts and previews
stay in the ignored build directory. ZIP packaging is a separate handoff operation.
After reviewing a rebuilt deck, promote the checked revision to the stable
`review-slides.pptx` filename. Rebuild PDFs and run the bundled Python on
`docs/a2/package_materials.py` to refresh the ZIP. Keep verification notes and quoted
figures consistent with the new snapshot.

## Scope of the evidence

Model accuracy and missing-data results use made-up facility water use and river data.
The real public-data download checks connectivity, parsing, and units. Made-up permits
test document search, not compliance. Tested approaches include symbolic engineering
rules, tree-based models, time/nearby-station gap filling, and TF-IDF/FAISS word search.
Neural and generative LLM summaries have not been tested. The class studio list was
not supplied and still needs confirmation. Simplified wording keeps all original
results, evidence references, limits, decisions, and checklist requirements.

## Before submitting

- Confirm the presentation day and Submitty deadline with the course.
- Verify instructor/TA GitHub access; the configured remote alone does not prove access.
- Schedule office hours and rehearse questions with all three team members.
- Review assigned responsibilities and record actual completed contributions.
- Confirm studio-specific references and any intended future scraping or survey work.

The attached documents provide assignment requirements. They do not authorize course
submission, external messages, repository permission changes, or invented team activity.
