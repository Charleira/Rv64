"""Grafo de interferência entre LRs."""
from itertools import combinations

from backend_api import REGISTERS, CFG, BasicBlock, Liveness
from ir import Move, defs, uses


def build_interference(cfg, points, ranges):
    instrs = cfg.function.instructions
    graph = {lr: set() for lr in ranges.values()}

    def edge(a, b):
        if a != b:
            graph[a].add(b)
            graph[b].add(a)

    # Clique na entrada da função.
    if cfg.entry is not None:
        first = cfg.blocks[cfg.entry].start
        entry_lrs = {ranges[(first, "before", v)] for v in points.before[first]}
        for a, b in combinations(entry_lrs, 2):
            edge(a, b)

    # Interferência por definição (com exceção para cópias).
    for i, ins in enumerate(instrs):
        for d in defs(ins):
            lr_d = ranges[(i, "after", d)]
            skip = None
            if isinstance(ins, Move):
                (src,) = uses(ins)
                skip = ranges[(i, "before", src)]
            for v in points.after[i]:
                lr_v = ranges[(i, "after", v)]
                if lr_v == lr_d or lr_v == skip:
                    continue
                edge(lr_d, lr_v)
    return graph