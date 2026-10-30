"""Reverse dependency analysis helpers."""


def reverse_graph(graph: dict) -> dict:
    """Create adjacency lists where edges point to dependants."""
    reverse = {name: [] for name in graph}
    for package, dependencies in graph.items():
        for dependency in dependencies:
            reverse.setdefault(dependency, []).append(package)
    return reverse


def reachable_reverse(graph: dict, target: str) -> dict:
    """Return all transitive reverse dependencies of one package."""
    from src.graph import recursive_bfs

    reverse = reverse_graph(graph)
    if target not in reverse:
        raise LookupError(f"Package not found: {target}")
    return recursive_bfs(reverse, target)
