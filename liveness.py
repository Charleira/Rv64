"""Vivacidade por bloco (ponto fixo) e por instrução."""
from backend_api import REGISTERS, CFG, BasicBlock, InstructionLiveness, Liveness
from ir import defs, uses


def _use_def(cfg, block):
    instrs = cfg.function.instructions
    use, define = set(), set()
    for i in range(block.start, block.stop):
        ins = instrs[i]
        use |= uses(ins) - define      # leituras antes da escrita
        define |= defs(ins)
    return use, define


def solve_liveness(cfg):
    live_in = {b: set() for b in cfg.blocks}
    live_out = {b: set() for b in cfg.blocks}
    summary = {b: _use_def(cfg, blk) for b, blk in cfg.blocks.items()}
    order = sorted(cfg.blocks, reverse=True)

    changed = True
    while changed:
        changed = False
        for b in order:
            out = set()
            for s in cfg.blocks[b].successors:
                out |= live_in[s]
            use, define = summary[b]
            new_in = use | (out - define)
            if out != live_out[b] or new_in != live_in[b]:
                live_out[b] = out
                live_in[b] = new_in
                changed = True
    return Liveness(live_in=live_in, live_out=live_out)


def solve_instruction_liveness(cfg, liveness):
    """Retorne os conjuntos antes e depois de cada instrução."""
    instrs = cfg.function.instructions
    before, after = {}, {}
    for b, blk in cfg.blocks.items():
        cur = set(liveness.live_out[b])
        for i in range(blk.stop - 1, blk.start - 1, -1):
            ins = instrs[i]
            after[i] = set(cur)
            cur = uses(ins) | (cur - defs(ins))
            before[i] = set(cur)
    return InstructionLiveness(before=before, after=after)