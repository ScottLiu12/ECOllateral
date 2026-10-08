"""Create a local handoff ZIP from the current stable documents and evidence."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    required = [
        "dossier.pdf",
        "project-checkoff.pdf",
        "review-slides-simplified.pptx",
        "review-slides.pdf",
        "semantic-system-map.svg",
        "semantic-system-map.png",
        "evidence-summary.csv",
        "presentation-script.md",
        "team-contributions.md",
        "verification-notes.md",
    ]
    missing = [name for name in required if not (here / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Finish these deliverables first: {missing}")
    target = here / "submission-package.zip"
    files = [
        path
        for path in sorted(here.rglob("*"))
        if path.is_file()
        and path.suffix != ".zip"
        # Preserve the user's open older deck locally, but package only the current one.
        and path.name != "review-slides.pptx"
        and not path.name.startswith("~$")
        and "__pycache__" not in path.parts
    ]
    files.extend(
        root / "docs" / name
        for name in (
            "implementation-notes.md",
            "data-contracts.md",
            "validation-results.md",
            "project-scope.md",
        )
    )
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, str(path.relative_to(root)).replace("\\", "/"))
    with ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP integrity check failed")
    print(f"Packaged {len(files)} files in {target}; no external submission performed")


if __name__ == "__main__":
    main()
