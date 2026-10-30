"""Command-line entry point for Dependency Visualizer."""

import argparse
import sys

from src.apk import download_index, find_package, parse_index
from src.config import load_config, print_config
from src.graph import build_dependency_graph, recursive_bfs, reachable_reverse
from src.render import render_image, save_dot
from src.test_repository import load_test_repository


def parse_arguments():
    """Create and parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze Alpine APK package dependencies"
    )
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--package", help="Override configured package name")
    parser.add_argument("--direct-only", action="store_true")
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--dot-only", action="store_true")
    return parser.parse_args()


def load_graph(config):
    """Load a test graph or retrieve and parse a remote APK index."""
    if config.test_repository:
        return load_test_repository(config.test_repository_path), None
    index_text = download_index(config.repository_url)
    packages = parse_index(index_text)
    selected = find_package(
        packages, config.package_name, config.package_version
    )
    return build_dependency_graph(packages), selected


def show_direct(package, graph):
    """Print direct dependencies for the selected package."""
    dependencies = graph.get(package, [])
    print(f"Direct dependencies of {package}:")
    if not dependencies:
        print("  (none)")
    for dependency in dependencies:
        print(f"  - {dependency}")


def show_graph(graph):
    """Print adjacency lists for a dependency subgraph."""
    print("Dependency graph:")
    for package, dependencies in graph.items():
        print(f"  {package} -> {', '.join(dependencies) or '(none)'}")


def run_analysis(config, args):
    """Run dependency analysis, reverse analysis, and visualization."""
    package = args.package or config.package_name
    graph, selected = load_graph(config)
    if not config.test_repository:
        if selected is None:
            raise RuntimeError("Selected APK package metadata is unavailable")
        show_direct(package, graph)
    else:
        show_direct(package, graph)
    if args.direct_only:
        return
    if args.reverse:
        result = reachable_reverse(graph, package)
        show_graph(result)
        return
    result = recursive_bfs(graph, package, config.filter_substring)
    show_graph(result)
    dot_path = save_dot(result, config.output_dir)
    print(f"DOT file: {dot_path}")
    if not args.dot_only:
        image_path = render_image(
            dot_path, config.output_dir, config.graph_format
        )
        print(f"Image: {image_path}")


def main():
    """Load configuration and execute the requested CLI operation."""
    args = parse_arguments()
    try:
        config = load_config(args.config)
        print_config(config)
        run_analysis(config, args)
    except (OSError, ValueError, TypeError, RuntimeError, LookupError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
