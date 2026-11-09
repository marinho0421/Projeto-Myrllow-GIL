"""Niveis montados a mao com um pequeno 'construtor' de segmentos (colinas, fossos, escadas/cipos,
plataformas moveis/que caem, tunel secreto...). Cada nivel e fixo (sempre igual) e foi verificado por um bot
(tools/verify_levels.py). Regras de alcance usadas ao desenhar: degrau de subida <= 2 blocos, vao <= 3 blocos
andando (4 so com corrida, nos niveis finais); subidas maiores exigem escada/cipo/parede escalavel."""
from .const import T, ROWS, GR

# dificuldade exibida na selecao de fases (1 = facil ... 5 = muito dificil)
DIFFICULTY = [1, 2, 2, 2, 3, 4, 3, 4, 5]

class Level:
    def __init__(s, idx):
        s.idx, s.world = idx, idx // 3
        s.solid, s.plat, s.spikes, s.gate = set(), set(), set(), set()
        s.climb = {}                       # (col, linha) -> tipo: vine | rope | ladder | wall
        s.enemies, s.movers, s.fallers, s.orbs = [], [], [], []   # tuplas de construcao
        s.cover = set()
        s.secret = []                      # lista de conjuntos de blocos (passagens escondidas)
        s.cps = []                         # pontos de reaparecimento: (x, y_base)
        s.sign = (0, GR)
        s.gate_col, s.start, s.frag, s.width = 0, (0, 0), (0, 0), 0

class B:
    def __init__(b, idx):
        b.idx, b.top, b.h, b.L = idx, [], GR, Level(idx)
        b._spk, b._cps, b._carve = [], [], []
        b._sign = b._gate = b._frag = None
    @property
    def x(b): return len(b.top)
    # ----- terreno -----
    def flat(b, n, h=None):
        b.h = b.h if h is None else h; b.top.extend([b.h] * n)
    def gap(b, n): b.top.extend([None] * n)
    def hills(b, seq):
        for n, h in seq: b.flat(n, h)
    def plat(b, c, w, r):
        b.L.plat.update((cc, r) for cc in range(c, c + w))
    def pit(b, w, plats=()):
        a, g = b.x, b.h; b.gap(w)
        for off, pw, dr in plats: b.plat(a + off, pw, g - dr)
    # ----- perigos / objetos -----
    def spike(b, c, n=1, row=None): b._spk.append((c, n, row))
    def spikes_on(b, n, pad=3):
        b.flat(pad); a = b.x; b.flat(n); b.spike(a, n); b.flat(pad)
    def walker(b, c0, c1, row, sp=0.6):
        b.L.enemies.append((c0 * T, row * T - 12, c0 * T, c1 * T, sp, "walk", 0, 0))
    def flyer(b, c0, c1, row, amp=24, sp=0.8, phase=0.0):
        b.L.enemies.append((c0 * T, row * T - 6, c0 * T, c1 * T, sp, "fly", amp, phase))
    def patrol(b, n, sp):
        a = b.x; b.flat(n); b.walker(a + 1, a + n - 1, b.h, sp)
    def mover(b, c0, c1, row, sp=0.8, vert=False, w=72):
        if vert: b.L.movers.append((c0 * T, c1 * T, c0 * T, c1 * T, sp, True, w))   # reescrito em elevator()
        else: b.L.movers.append((c0 * T - 6, row * T, c0 * T - 6, c1 * T - w + 6, sp, False, w))
    def faller(b, c, row, w=2): b.L.fallers.append((c * T, row * T, w * T))
    def orb(b, c, r): b.L.orbs.append((c * T + T // 2, r * T + T // 2))
    def ladder(b, c, r0, r1, kind):
        for r in range(r0, r1 + 1): b.L.climb[(c, r)] = kind
    def cp(b, c): b._cps.append(c)
    def sign(b, c): b._sign = c
    def gate(b, c): b._gate = c
    def frag(b, c): b._frag = c
    def secret(b, c0, r0, c1, r1):
        b._carve.append([(c, r) for c in range(c0, c1 + 1) for r in range(r0, r1 + 1)])
    # ----- segmentos prontos -----
    def climb_up(b, dh, kind, after=5, orbs=0):
        """Chao -> coluna da escada -> patamar dh blocos acima (precisa subir pela escada/cipo)."""
        g, c = b.h, b.x
        b.flat(1, g)
        b.ladder(c, g - dh - 1, g - 1, kind)
        b.flat(after, g - dh)
        return c
    def valley(b, depth, w, chain=True, spikes=0, walker=False, orbs=0):
        """Bifurcacao: vale (caminho de baixo, com perigos e brindes) x corrente de plataformas por cima."""
        g = b.h; a = b.x; fl = g + depth
        b.flat(w, fl)
        for i in range(0, w, 4):                                   # saida do vale em degraus de <= 2 blocos
            pass
        if chain:
            r, i, k = g - 2, 1, 0
            while i + 2 <= w - 1:
                b.plat(a + i, 2, r); r = g - 2 if k % 2 else g - 3; i += 4; k += 1
        if spikes: b.spike(a + w // 2 - spikes // 2, spikes, fl - 1)
        if walker: b.walker(a + 1, a + w - 4, fl, 0.7)
        for j in range(orbs): b.orb(a + 2 + j * 2, fl - 1)
        return a, fl
    def valley_exit(b, fl, g):
        """Sobe do fundo do vale ate g em degraus de 2 blocos."""
        h = fl
        while h > g:
            h = max(g, h - 2); b.flat(2, h)
    def elevator(b, c, row_lo, row_hi, sp=0.7):
        """Plataforma de 2 blocos que sobe/desce entre as linhas row_hi (alto) e row_lo (baixo)."""
        b.L.movers.append((c * T, row_lo * T, row_hi * T, row_lo * T, sp, True, 2 * T))
    def finish(b):
        L, top = b.L, b.top
        for c, n, row in b._spk:
            for cc in range(c, c + n): L.spikes.add((cc, row if row is not None else top[cc] - 1))
        for c, h in enumerate(top):
            if h is not None: L.solid.update((c, r) for r in range(h, ROWS))
        for group in b._carve:                                     # tuneis secretos
            L.solid.difference_update(group); L.secret.append(set(group)); L.cover.update(group)
        L.sign = (b._sign, top[b._sign])
        L.cps = [(c * T + (T - 14) // 2, top[c] * T) for c in b._cps]
        L.gate_col = b._gate
        L.gate = {(b._gate, r) for r in range(0, top[b._gate])}
        L.frag = (b._frag * T + T // 2, top[b._frag] * T - 22)
        L.start = (3 * T, top[3] * T)
        L.width = len(top) * T
        return L

# =================================================================================================
#  MUNDO 1 - FLORESTA (cipos, troncos que caem, vespas)
# =================================================================================================
def forest1(b):          # facil: ritmo calmo, primeiro cipo e primeira bifurcacao
    b.flat(9, 11); b.sign(6)
    b.hills([(3, 10), (3, 9), (3, 10), (4, 11)]); b.flat(3); b.cp(b.x - 2)
    a = b.x; b.pit(2); b.flat(7, 11); b.walker(a + 4, a + 8, 11, 0.6)
    c = b.climb_up(4, "vine", after=7)                       # ledge na linha 7
    b.orb(c + 3, 6); b.orb(c + 5, 6)
    b.pit(8, plats=[(1, 2, 0), (4, 2, 1)]); b.flat(4, 9); b.hills([(3, 10), (4, 11)])
    b.cp(b.x - 2); b.flat(4)
    b.spikes_on(1); b.flat(2)
    a, fl = b.valley(2, 9, chain=True, spikes=1, orbs=2); b.valley_exit(fl, 11); b.flat(3)
    a = b.x; b.flat(9); b.walker(a + 1, a + 7, 11, 0.7)
    b.flat(3); b.cp(b.x - 2); b.flat(3); b.gate(b.x); b.flat(5)
    b.pit(3, plats=[(1, 1, 1)]); b.flat(5)
    b.hills([(3, 10), (3, 9), (5, 10), (3, 11)]); b.pit(2); b.flat(5); b.cp(b.x - 2)
    b.spikes_on(2); b.flat(3); b.frag(b.x + 5); b.flat(14)

def forest2(b):          # logs que caem, tunel secreto, vespa
    b.flat(9, 11); b.sign(6)
    b.hills([(4, 10), (4, 9), (3, 10), (3, 11)]); b.flat(3)
    a = b.x; b.walker(a + 1, a + 6, 11, 0.7); b.flat(8); b.cp(b.x - 2)
    # parede com tunel secreto: escalar (brindes em cima) ou atravessar a passagem escondida
    g, c = 11, b.x
    b.climb_up(4, "vine", after=5); b.flat(6, 11)
    b.secret(c + 1, 9, c + 5, 10)
    b.orb(c + 2, 10); b.orb(c + 3, 10); b.orb(c + 4, 10); b.orb(c + 3, 6)
    b.flat(3); b.cp(b.x - 2)
    a = b.x; b.gap(10)                                          # troncos que caem
    for i in range(3): b.faller(a + 1 + i * 3, 11)
    b.flat(4); b.flyer(b.x - 4, b.x + 6, 9, 14, 0.9); b.flat(6)
    b.spikes_on(2); b.flat(2)
    a, fl = b.valley(3, 11, chain=True, spikes=2, walker=False, orbs=2); b.flyer(a + 1, a + 9, 8, 12, 0.9, 1.5)
    b.valley_exit(fl, 11); b.flat(3); b.cp(b.x - 2); b.flat(2); b.gate(b.x); b.flat(4)
    b.pit(3, plats=[(1, 1, 1)]); b.flat(3)
    c = b.climb_up(5, "vine", after=4); b.orb(c + 2, 5)
    b.pit(7, plats=[(1, 2, 0), (4, 2, 1)]); b.hills([(3, 8), (3, 9), (3, 10), (3, 11)])
    b.cp(b.x - 2); b.patrol(8, 0.8); b.flat(2)
    b.spikes_on(1); b.flat(3); b.frag(b.x + 5); b.flat(14)

def forest3(b):          # copas altas: dois caminhos, cipos longos, elevador de tronco
    b.flat(9, 11); b.sign(6)
    b.hills([(3, 10), (3, 9), (3, 8), (3, 9), (3, 10), (3, 11)]); b.flat(2)
    a = b.x; b.walker(a + 1, a + 5, 11, 0.8); b.flat(6); b.cp(b.x - 2)
    a = b.x; b.gap(9)
    for i in range(3): b.faller(a + 1 + i * 3, 11)
    b.flat(3)
    c = b.climb_up(5, "vine", after=3); b.orb(c + 2, 5)       # sobe para a copa (linha 6)
    a = b.x; b.gap(12)                                          # corrente de plataformas por cima
    for i, (off, r) in enumerate([(1, 6), (4, 5), (7, 6), (10, 5)]): b.plat(a + off, 2, r)
    b.flyer(a + 1, a + 10, 3, 10, 0.9)
    b.flat(4, 6); b.cp(b.x - 2); b.hills([(3, 8), (3, 10), (3, 11)])
    b.spikes_on(2); b.flat(3)
    a = b.x; b.walker(a + 1, a + 6, 11, 0.9); b.flat(8)
    a, fl = b.valley(3, 12, chain=True, spikes=3, walker=False, orbs=2); b.flyer(a + 1, a + 10, 8, 14, 1.0, 0.7)
    b.valley_exit(fl, 11); b.flat(3); b.cp(b.x - 2); b.flat(2); b.gate(b.x); b.flat(3)
    g = 11; b.pit(4, plats=[(1, 1, 1), (3, 1, 2)]); b.flat(3, 9)
    b.elevator(b.x + 1, 9, 5); b.gap(4); b.flat(3, 5)            # tronco-elevador: ledge alto
    b.cp(b.x - 2); b.hills([(3, 7), (3, 9), (3, 11)])
    b.patrol(8, 0.9); b.spikes_on(2); b.flat(2); b.frag(b.x + 5); b.flat(14)

# =================================================================================================
#  MUNDO 2 - DESERTO (escadas, blocos de arenito que caem, escorpioes, urubus)
# =================================================================================================
def desert1(b):
    b.flat(9, 11); b.sign(6)
    b.hills([(3, 10), (4, 9), (3, 10), (4, 11)]); b.flat(2); b.walker(b.x - 5, b.x - 1, 11, 0.8); b.cp(b.x - 2)
    a = b.x; b.gap(9)
    for i in range(3): b.faller(a + 1 + i * 3, 11)
    b.flat(4); c = b.climb_up(4, "ladder", after=6); b.orb(c + 3, 6)
    b.pit(8, plats=[(1, 2, 0), (4, 2, 1)]); b.hills([(5, 9), (3, 10), (3, 11)])
    b.cp(b.x - 2); b.flat(3); b.spikes_on(2); b.flat(2); b.flyer(b.x - 2, b.x + 8, 8, 14, 0.9)
    a, fl = b.valley(3, 12, chain=True, spikes=3, orbs=2); b.valley_exit(fl, 11); b.flat(3)
    a = b.x; b.flat(9); b.walker(a + 1, a + 7, 11, 0.9)
    b.flat(3); b.cp(b.x - 2); b.flat(2); b.gate(b.x); b.flat(4)
    b.pit(3, plats=[(1, 1, 1)]); b.flat(4)
    g, c = 11, b.x                                              # parede com tunel secreto
    b.climb_up(4, "ladder", after=5); b.flat(5, 11); b.secret(c + 1, 9, c + 5, 10)
    b.orb(c + 2, 10); b.orb(c + 3, 10); b.orb(c + 4, 10)
    b.cp(b.x - 2); b.flat(2); b.spikes_on(1); b.flat(2); b.patrol(8, 1.0)
    b.frag(b.x + 5); b.flat(14)

def desert2(b):          # plataformas moveis
    b.flat(9, 11); b.sign(6)
    b.hills([(3, 10), (3, 9), (3, 8), (3, 9), (3, 10), (3, 11)]); b.flat(2); b.cp(b.x - 2)
    a = b.x; b.gap(10); b.mover(a, a + 10, 11, 0.8); b.flat(4)
    b.walker(b.x - 3, b.x, 11, 0.9); b.flat(4)
    c = b.climb_up(5, "rope", after=3); b.orb(c + 2, 5)
    a = b.x; b.gap(11)
    for off, r in [(1, 6), (4, 5), (7, 6)]: b.plat(a + off, 2, r)
    b.flyer(a, a + 10, 3, 10, 1.0)
    b.flat(4, 6); b.cp(b.x - 2); b.hills([(3, 8), (3, 10), (4, 11)])
    b.spikes_on(2); b.flat(2)
    a, fl = b.valley(3, 12, chain=True, spikes=3, walker=True, orbs=2); b.valley_exit(fl, 11); b.flat(3)
    b.cp(b.x - 2); b.flat(2); b.gate(b.x); b.flat(4)
    a = b.x; b.gap(9)
    for i in range(3): b.faller(a + 1 + i * 3, 11)
    b.flat(2)
    a = b.x; b.gap(4); b.elevator(a + 1, 11, 7); b.flat(3, 7); b.hills([(3, 9), (3, 11)])
    b.cp(b.x - 2); b.patrol(8, 1.0); b.spikes_on(2); b.flat(2)
    a = b.x; b.gap(10); b.mover(a, a + 10, 11, 1.0); b.flat(3)
    b.frag(b.x + 5); b.flat(14)

def desert3(b):          # escalada longa + cadeias de blocos + vento de urubus
    b.flat(9, 11); b.sign(6)
    b.hills([(3, 10), (3, 9), (3, 10), (3, 9), (3, 10), (3, 11)]); b.flat(2)
    a = b.x; b.walker(a + 1, a + 6, 11, 1.0); b.flat(7); b.cp(b.x - 2)
    a = b.x; b.gap(12)
    for i in range(4): b.faller(a + 1 + i * 3, 11)
    b.flat(3)
    g, c = 11, b.x
    b.climb_up(5, "ladder", after=6); b.flat(5, 11); b.secret(c + 1, 9, c + 6, 10)
    b.orb(c + 2, 10); b.orb(c + 3, 10); b.orb(c + 5, 10); b.orb(c + 4, 5)
    b.cp(b.x - 2); b.flat(2)
    a = b.x; b.gap(11)
    for off, r in [(1, 10), (4, 9), (7, 10)]: b.plat(a + off, 2, r)
    b.flyer(a, a + 10, 8, 12, 1.1); b.flat(3)
    b.spikes_on(3); b.flat(2)
    a, fl = b.valley(3, 13, chain=True, spikes=3, walker=True, orbs=2)
    b.flyer(a + 1, a + 11, 6, 14, 1.1, 1.2); b.valley_exit(fl, 11); b.flat(3); b.cp(b.x - 2); b.flat(2); b.gate(b.x); b.flat(4)
    a = b.x; b.gap(4); b.flat(3)                                # vao de 4 blocos: corrida
    a = b.x; b.gap(12); b.mover(a, a + 12, 11, 1.1); b.flat(3, 11)
    c = b.climb_up(5, "ladder", after=3); b.cp(b.x - 2)
    a = b.x; b.gap(9)
    for i in range(3): b.faller(a + 1 + i * 3, 6)
    b.flat(3, 6); b.hills([(3, 8), (3, 10), (3, 11)])
    b.patrol(8, 1.1); b.spikes_on(2); b.flat(2); b.frag(b.x + 5); b.flat(14)

# =================================================================================================
#  MUNDO 3 - CIDADE HISTORICA (escadas de ferro, muros escalaveis, elevadores, drones)
# =================================================================================================
def city1(b):
    b.flat(9, 11); b.sign(6)
    b.hills([(3, 10), (3, 9), (3, 8), (3, 9), (3, 10), (3, 11)]); b.flat(2); b.cp(b.x - 2)
    a = b.x; b.walker(a + 1, a + 6, 11, 0.9); b.flat(7)
    g, c = 11, b.x
    b.climb_up(5, "wall", after=6); b.flat(5, 11); b.secret(c + 1, 9, c + 6, 10)
    b.orb(c + 2, 10); b.orb(c + 4, 10); b.orb(c + 4, 5)
    b.cp(b.x - 2); b.flat(2)
    a = b.x; b.gap(10); b.mover(a, a + 10, 11, 0.9); b.flat(3)
    b.spikes_on(2); b.flat(2); b.flyer(b.x - 3, b.x + 7, 8, 14, 1.0)
    a, fl = b.valley(3, 12, chain=True, spikes=3, orbs=2); b.valley_exit(fl, 11); b.flat(3)
    b.cp(b.x - 2); b.flat(2); b.gate(b.x); b.flat(4)
    a = b.x; b.gap(9)
    for i in range(3): b.faller(a + 1 + i * 3, 11)
    b.flat(2); c = b.climb_up(4, "ladder", after=4); b.orb(c + 2, 6)
    b.pit(7, plats=[(1, 2, 0), (4, 2, 1)]); b.hills([(3, 9), (3, 10), (3, 11)])
    b.cp(b.x - 2); b.patrol(8, 1.0); b.spikes_on(2); b.flat(2)
    b.frag(b.x + 5); b.flat(14)

def city2(b):            # elevadores e telhados
    b.flat(9, 11); b.sign(6)
    b.hills([(3, 10), (3, 9), (3, 10), (3, 9), (3, 10), (3, 11)]); b.flat(2)
    a = b.x; b.walker(a + 1, a + 6, 11, 1.0); b.flat(7); b.cp(b.x - 2)
    a = b.x; b.gap(4); b.elevator(a + 1, 11, 6); b.flat(4, 6)    # elevador ate o telhado
    a = b.x; b.gap(12)
    for off, r in [(1, 6), (4, 5), (7, 6), (10, 5)]: b.plat(a + off, 2, r)
    b.flyer(a, a + 11, 3, 10, 1.1)
    b.flat(3, 7); b.cp(b.x - 2); b.hills([(3, 8), (3, 10), (3, 11)]); b.flat(2)
    b.spikes_on(3); b.flat(2)
    a = b.x; b.gap(10); b.mover(a, a + 10, 11, 1.1); b.flat(4)
    g, c = 11, b.x
    b.climb_up(5, "wall", after=6); b.flat(5, 11); b.secret(c + 1, 9, c + 6, 10)
    b.orb(c + 2, 10); b.orb(c + 3, 10); b.orb(c + 5, 10); b.orb(c + 4, 5)
    b.cp(b.x - 2); b.flat(2)
    a, fl = b.valley(3, 13, chain=True, spikes=3, walker=True, orbs=2)
    b.flyer(a + 1, a + 11, 6, 14, 1.1, 1.0); b.valley_exit(fl, 11); b.flat(3); b.cp(b.x - 2); b.flat(2); b.gate(b.x); b.flat(4)
    a = b.x; b.gap(12)
    for i in range(4): b.faller(a + 1 + i * 3, 11)
    b.flat(3); a = b.x; b.gap(4); b.elevator(a + 1, 11, 6); b.flat(3, 6)
    b.hills([(3, 8), (3, 10), (3, 11)]); b.cp(b.x - 2)
    b.patrol(8, 1.1); b.spikes_on(3); b.flat(2); b.frag(b.x + 5); b.flat(14)

def city3(b):            # final: tudo junto, ritmo mais rapido
    b.flat(9, 11); b.sign(6)
    b.hills([(3, 10), (3, 9), (3, 8), (3, 9), (3, 10), (3, 11)]); b.flat(2)
    a = b.x; b.walker(a + 1, a + 6, 11, 1.1); b.flat(6); b.cp(b.x - 2)
    a = b.x; b.gap(12)
    for i in range(4): b.faller(a + 1 + i * 3, 11)
    b.flat(3)
    g, c = 11, b.x
    b.climb_up(5, "wall", after=6); b.flat(5, 11); b.secret(c + 1, 9, c + 6, 10)
    b.orb(c + 2, 10); b.orb(c + 3, 10); b.orb(c + 5, 10); b.orb(c + 4, 5)
    b.cp(b.x - 2); b.flat(2)
    a = b.x; b.gap(4); b.flat(3)                                # vao de 4: corrida
    a = b.x; b.gap(12); b.mover(a, a + 12, 11, 1.2); b.flat(3)
    b.spikes_on(3); b.flat(2)
    a, fl = b.valley(3, 13, chain=True, spikes=3, walker=True, orbs=2)
    b.flyer(a + 1, a + 11, 6, 16, 1.2, 0.5); b.valley_exit(fl, 11); b.flat(3); b.cp(b.x - 2); b.flat(2); b.gate(b.x); b.flat(4)
    a = b.x; b.gap(4); b.elevator(a + 1, 11, 6); b.flat(3, 6)
    a = b.x; b.gap(12)
    for off, r in [(1, 6), (4, 5), (7, 6), (10, 5)]: b.plat(a + off, 2, r)
    b.flyer(a, a + 11, 3, 12, 1.2, 0.3)
    b.flat(3, 6); b.cp(b.x - 2)
    a = b.x; b.gap(9)
    for i in range(3): b.faller(a + 1 + i * 3, 6)
    b.flat(3, 6); b.hills([(3, 8), (3, 10), (3, 11)]); b.cp(b.x - 2)
    b.patrol(8, 1.2); b.spikes_on(3); b.flat(2)
    a = b.x; b.gap(10); b.mover(a, a + 10, 11, 1.2); b.flat(3)
    b.frag(b.x + 5); b.flat(14)

BUILDERS = [forest1, forest2, forest3, desert1, desert2, desert3, city1, city2, city3]

def build(idx):
    b = B(idx); BUILDERS[idx](b); return b.finish()
