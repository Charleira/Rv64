"""Construa os LRs globais da função. Consulte ENUNCIADO.pdf."""
from ir import VReg, defs


def build_live_ranges(cfg, points):
    function = cfg.function
    instrs = function.instructions

    parent = {}
    order = []

    def add(p):
        if p not in parent:
            parent[p] = p
            order.append(p)

    def find(p):
        root = p
        while parent[root] != root:
            root = parent[root]
        while parent[p] != root:
            parent[p], p = root, parent[p]
        return root

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Pontos vivos + definições mortas (ponto "after" do destino).
    for i, ins in enumerate(instrs):
        for v in points.before[i]:
            add((i, "before", v))
        for v in points.after[i]:
            add((i, "after", v))
        for d in defs(ins):
            add((i, "after", d))

    # Mesma instrução: vivo dos dois lados e não redefinido.
    for i, ins in enumerate(instrs):
        for v in (points.before[i] & points.after[i]) - defs(ins):
            union((i, "before", v), (i, "after", v))

    # Instrução -> próxima, dentro do bloco e nas arestas do CFG.
    for blk in cfg.blocks.values():
        for i in range(blk.start, blk.stop - 1):
            for v in points.after[i] & points.before[i + 1]:
                union((i, "after", v), (i + 1, "before", v))
        last = blk.stop - 1
        for s in blk.successors:
            first = cfg.blocks[s].start
            for v in points.after[last] & points.before[first]:
                union((last, "after", v), (first, "before", v))

    lr_of_root = {}
    result = {}
    for p in order:
        root = find(p)
        if root not in lr_of_root:
            lr_of_root[root] = VReg(function.function, len(lr_of_root))
        result[p] = lr_of_root[root]
    return result