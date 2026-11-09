"""Gerador de niveis: sequencias de segmentos com dificuldade crescente (indice 0..8)."""
import random
from .const import T, ROWS, GR

class Level:
    def __init__(s, idx):
        s.idx, s.world = idx, idx // 3
        s.solid, s.plat, s.spikes, s.gate = set(), set(), set(), set()
        s.enemies, s.movers = [], []          # (x, y, x0, x1, speed) / (x, y, x0, x1, speed)
        s.cp = s.sign = s.gate_col = None
        s.start = s.frag = (0, 0)
        s.width = 0

def build(idx):
    rng, d = random.Random(777 + idx * 31), idx
    top, L = [], Level(idx)
    marks = {}

    def flat(n, h=GR): top.extend([h] * n)
    def gap(n): top.extend([None] * n)
    def pos(): return len(top)

    def hazard():
        kinds = ["gap", "spikes", "enemy", "tower", "float"]
        if d >= 3: kinds += ["moving", "enemy"]
        if d >= 5: kinds += ["combo"]
        k = rng.choice(kinds)
        flat(3)
        if k == "gap":
            gap(rng.randint(2, 3)); flat(3)
        elif k == "spikes":
            a = pos(); flat(1); n = rng.randint(1, 2); flat(n); L.spikes.update((c, "s") for c in range(a + 1, a + 1 + n)); flat(3)
        elif k == "enemy":
            a, n = pos(), 1 + (d >= 5); flat(4 + 7 * n)
            for j in range(n):
                x0 = (a + 2 + j * 7) * T
                L.enemies.append((x0 + T, GR * T - 12, x0, x0 + 5 * T, 0.6 + 0.08 * d))
        elif k == "tower":
            h = rng.randint(1, 2); flat(1, GR - 1 if h == 2 else GR - 1); flat(rng.randint(3, 5), GR - h); flat(1, GR - 1); flat(2)
        elif k == "float":
            m = rng.randint(2, 3); w = 3 - (d >= 6)
            a = pos(); gap(2)
            for j in range(m):
                r = GR - 1 - rng.randint(0, 1)
                c0 = pos(); gap(w); L.plat.update((c, r) for c in range(c0, c0 + w)); gap(2)
            flat(3)
        elif k == "moving":
            a = pos(); gap(10); L.movers.append((a * T + 4, GR * T, a * T, (a + 7) * T, 0.8 + 0.1 * d)); flat(3)
        elif k == "combo":
            flat(1); L.spikes.add((pos(), "s")); flat(1); flat(3); gap(2); flat(3)

    flat(10); L.start = (3 * T, GR * T)
    gap(2) if idx else None; flat(3 if idx else 0)
    flat(3); marks["sign"] = pos() + 2; flat(7)
    for _ in range(2 + d // 2): hazard()
    flat(3); marks["cp"] = pos() + 2; flat(6)
    for _ in range(2 + d // 2): hazard()
    flat(4); marks["gate"] = pos() + 4; flat(8)
    for _ in range(1 + d // 3): hazard()
    flat(4); marks["frag"] = pos() + 6; flat(12)

    for c, h in enumerate(top):
        if h is not None:
            L.solid.update((c, r) for r in range(h, ROWS))
    L.spikes = {(c, top[c] - 1) for c, _ in L.spikes}
    L.sign, L.cp, L.gate_col = marks["sign"], marks["cp"], marks["gate"]
    L.gate = {(L.gate_col, r) for r in range(0, GR)}
    L.frag = (marks["frag"] * T + T // 2, GR * T - 20)
    L.width = len(top) * T
    return L
