"""Dependency graph construction and traversal operations."""

from collections import deque


def build_dependency_graph(packages: dict) -> dict:
    """Convert APK package metadata into package-name adjacency lists."""
    known_names = set(packages)
    graph = {}
    for name, metadata in packages.items():
        resolved = []
        for expression in metadata["dependencies"]:
            dependency = _resolve_dependency(expression, known_names)
            if dependency and dependency not in resolved:
                resolved.append(dependency)
        graph[name] = resolved
    return graph


def _resolve_dependency(expression: str, known_names: set):
    """Resolve a dependency token to a package present in the index."""
    from src.apk import dependency_name

    token = dependency_name(expression)
    return token if token in known_names else None


def recursive_bfs(graph: dict, start: str, filter_text: str = "") -> dict:
    """Build the reachable dependency subgraph using recursive BFS."""
    if start not in graph:
        raise LookupError(f"Package not found: {start}")
    visited = set()
    result = {}

    def visit_queue(queue: deque) -> None:
        """Process one BFS queue recursively."""
        if not queue:
            return
        current = queue.popleft()
        if current in visited:
            visit_queue(queue)
            return
        visited.add(current)
        dependencies = [
            item for item in graph.get(current, [])
            if filter_text not in item
        ]
        result[current] = dependencies
        queue.extend(item for item in dependencies if item not in visited)
        visit_queue(queue)

    visit_queue(deque([start]))
    return result


