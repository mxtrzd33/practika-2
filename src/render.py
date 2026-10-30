"""Graphviz DOT generation and optional image rendering."""

from pathlib import Path
import shutil
import subprocess


def to_dot(graph: dict) -> str:
    """Convert an adjacency mapping into a Graphviz directed graph."""
    lines = ["digraph dependencies {", "  rankdir=LR;"]
    for package, dependencies in sorted(graph.items()):
        if not dependencies:
            lines.append(f'  "{_escape(package)}";')
        for dependency in sorted(dependencies):
            left = _escape(package)
            right = _escape(dependency)
            lines.append(f'  "{left}" -> "{right}";')
    lines.append("}")
    return "\n".join(lines) + "\n"


def _escape(value: str) -> str:
    """Escape a label for a quoted DOT identifier."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def save_dot(graph: dict, output_dir: str) -> Path:
    """Write DOT source to the output directory."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / "dependencies.dot"
    destination.write_text(to_dot(graph), encoding="utf-8")
    return destination


def render_image(dot_path: Path, output_dir: str, image_format: str) -> Path:
    """Render DOT to an image using the Graphviz dot executable."""
    executable = shutil.which("dot")
    if executable is None:
        raise RuntimeError(
            "Graphviz 'dot' was not found; install Graphviz to render images"
        )
    image_path = Path(output_dir) / f"dependencies.{image_format}"
    command = [executable, f"-T{image_format}", str(dot_path),
               "-o", str(image_path)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    return image_path
