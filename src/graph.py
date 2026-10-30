"""Dependency graph construction and traversal operations."""

from collections import deque


def build_dependency_graph(packages: dict) -> dict:
    """Convert APK package metadata into package-name adjacency lists."""
    graph = {}
    for name, metadata in packages.items():
        resolved = []
        for expression in metadata["dependencies"]:
            dependency = _resolve_dependency(expression, packages)
            if dependency and dependency not in resolved:
                resolved.append(dependency)
        graph[name] = resolved
    return graph


def _resolve_dependency(expression: str, packages: dict):
    """Resolve a package name or virtual provide to an indexed package."""
    from src.apk import dependency_name

    token = dependency_name(expression)
    if token in packages:
        return token
    for package, metadata in packages.items():
        if any(_provide_matches(item, token)
               for item in metadata.get("provides", [])):
            return package
    return None


def _provide_matches(provide: str, token: str) -> bool:
    """Compare a provided APK capability with a dependency token."""
    return provide.split("=", maxsplit=1)[0] == token


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
            if not filter_text or filter_text not in item
        ]
        result[current] = dependencies
        queue.extend(item for item in dependencies if item not in visited)
        visit_queue(queue)

    visit_queue(deque([start]))
    return result


