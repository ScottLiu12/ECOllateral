import argparse
import os
import sys
from pathlib import Path

import nbformat
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the missingness research notebook")
    parser.add_argument(
        "--output", type=Path, default=Path("data/processed/research/missingness.executed.ipynb")
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    runtime = root / "data/processed/notebook-runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    for name, directory in (
        ("IPYTHONDIR", "ipython"),
        ("JUPYTER_RUNTIME_DIR", "jupyter"),
        ("MPLCONFIGDIR", "matplotlib"),
    ):
        os.environ.setdefault(name, str(runtime / directory))
    notebook = nbformat.read(
        root / "notebooks/01_missingness_sensitivity_analysis.ipynb", as_version=4
    )
    client = NotebookClient(
        notebook, timeout=300, kernel_name="python3", resources={"metadata": {"path": str(root)}}
    )
    client.km = client.create_kernel_manager()
    client.km.kernel_spec_manager = KernelSpecManager(
        kernel_dirs=[str(Path(sys.prefix) / "share/jupyter/kernels")]
    )
    client.execute()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, args.output)
    print(f"Executed notebook saved to {args.output}")


if __name__ == "__main__":
    main()
