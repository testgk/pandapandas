from __future__ import annotations

import importlib.util
from pathlib import Path


EXAMPLES = [
    "01_create_geodataframe.py",
    "02_reproject_crs.py",
    "03_buffer_and_area.py",
    "04_spatial_join.py",
    "05_plot_example.py",
]


def _run_script(path: Path) -> None:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "run"):
        module.run()
    else:
        raise AttributeError(f"File {path.name} does not define run()")


def main() -> None:
    base = Path(__file__).parent / "examples"
    for script_name in EXAMPLES:
        script_path = base / script_name
        print(f"\n--- Running {script_name} ---")
        _run_script(script_path)

    print("\nAll examples completed.")


if __name__ == "__main__":
    main()

