"""Coloração de grafos: simplify/select."""
from backend_api import REGISTERS, CFG, BasicBlock, Liveness


def allocate(graph, registers=REGISTERS, *, trace=None):
    K = len(registers)
    nodes = list(graph)
    adj = {n: [m for m in graph[n] if m in graph] for n in nodes}
    degree = {n: len(adj[n]) for n in nodes}
    remaining = dict.fromkeys(nodes)
    stack = []

    # Simplify (trabalha só sobre graus residuais; o grafo original não muda)
    while remaining:
        node = next((n for n in remaining if degree[n] < K), None)
        potential = node is None
        if potential:
            node = max(remaining, key=lambda n: degree[n])
        del remaining[node]
        stack.append(node)
        if trace is not None:
            trace.append((node, potential))
        for m in adj[node]:
            if m in remaining:
                degree[m] -= 1

    # Select
    color = {}
    for node in reversed(stack):
        used = {color[m] for m in adj[node] if m in color and color[m] is not None}
        free = [r for r in registers if r not in used]
        color[node] = free[0] if free else None
    return {n: color[n] for n in nodes}