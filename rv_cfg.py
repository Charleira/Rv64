"""Construção do CFG sobre instruções pseudoRV64."""

import ir as I
from backend_api import CFG, BasicBlock

BRANCHES = (I.Beq, I.Bne, I.Blt, I.Bge, I.Beqz, I.Bnez)


def build_cfg(function):
    instrs = function.instructions
    n = len(instrs)
    if n == 0:
        return CFG(function, {}, None)

    # Líderes: primeira instrução, cada label e a instrução após desvio/retorno.
    leaders = {0}
    label_index = {}
    for i, ins in enumerate(instrs):
        if isinstance(ins, I.LabelInstr):
            leaders.add(i)
            label_index[ins.label] = i
        if isinstance(ins, BRANCHES + (I.Jump, I.Return)) and i + 1 < n:
            leaders.add(i + 1)

    starts = sorted(leaders)
    blocks = {}
    for k, start in enumerate(starts):
        stop = starts[k + 1] if k + 1 < len(starts) else n
        blocks[start] = BasicBlock(start=start, stop=stop)

    for k, start in enumerate(starts):
        block = blocks[start]
        last = instrs[block.stop - 1]
        nxt = starts[k + 1] if k + 1 < len(starts) else None

        if isinstance(last, I.Return):
            succ = []
        elif isinstance(last, I.Jump):
            succ = [label_index[last.target]]
        elif isinstance(last, BRANCHES):
            succ = [label_index[last.target]]
            if nxt is not None:
                succ.append(nxt)
        else:
            succ = [nxt] if nxt is not None else []

        for target in succ:
            block.successors.add(target)
            blocks[target].predecessors.add(start)

    return CFG(function, blocks, 0)