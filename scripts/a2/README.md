# Rebuild the A2 documents

Run from the repository root. These scripts support the files in `docs/a2/`.

Refresh evidence using the project virtual environment (see `../../docs/a2/evidence/README.md`).
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
Copy-Item scripts/a2/build_slides.mjs (Join-Path $env:TMP_DIR 'build.mjs')
& $env:RUNTIME_NODE (Join-Path $env:TMP_DIR 'build.mjs')
& $env:RUNTIME_PYTHON scripts/a2/build_materials.py
```

The deck builder validates the native charts and renders its finalized output before
the PDF builder embeds those slide renders. The PDF builder exports the two Markdown
documents and the system SVG/PNG. Chart workbooks intentionally round to ten significant
digits; the CSV evidence retains full precision. Reconcile textual figures after new
experiments and visually inspect rebuilt materials. Validation receipts and previews
stay in the ignored build directory. The reviewed files in docs/a2 are the handoff. No ZIP copy is generated.

After inspection, copy the finalized deck to `docs/a2/review-slides-simplified.pptx`.
Keep the current notes in `docs/a2/source/verification-notes.md` consistent with the export.
