"""Bot verificador: busca (best-first) um caminho do inicio ate o fragmento usando a fisica real do jogo.
Plataformas moveis entram como plataformas fixas nos dois extremos do percurso; inimigos sao ignorados;
espinhos e buracos matam. Tambem confere se cada checkpoint e o fragmento/orbes sao alcancaveis.
Uso: python tools/verify_levels.py [indices...]"""
import os, sys, heapq
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pygame
from game.const import *
from game.level import build
from game.entities import Player, Mover, Faller

class Keys(dict):
    def __missing__(s, k): return 0
def K(left=0, right=0, run=0, up=0, down=0, space=0):
    k = Keys(); k[pygame.K_LEFT] = left; k[pygame.K_RIGHT] = right; k[pygame.K_LSHIFT] = run
    k[pygame.K_UP] = up; k[pygame.K_DOWN] = down; k[pygame.K_SPACE] = space; return k

def static_platforms(lv):
    ms = []
    for (x, y, x0, x1, sp, vert, w) in lv.movers:
        if vert:
            for yy in (x0, x1, (x0 + x1) // 2): ms.append(Mover(x, yy, 0, 0, 0, False, w))
        else:
            for xx in (x0, x1, (x0 + x1) // 2): ms.append(Mover(xx, y, 0, 0, 0, False, w))
    for (x, y, w) in lv.fallers: ms.append(Mover(x, y, 0, 0, 0, False, w))
    return ms

def hit(lv, p):
    r = p.rect()
    if p.y > H + 40: return True
    for c, rr in lv.spikes:
        if abs(c * T - r.x) < 60 and r.colliderect(pygame.Rect(c * T + 4, rr * T + 14, T - 8, 10)): return True
    return False

def run_macro(lv, ms, st, plan):
    """plan: lista de (frames, keys, jump_event). Retorna Player final (em solo) ou None."""
    p = Player((0, 0)); p.x, p.y, p.vx, p.vy, p.ground = st; p.climbing = False
    p.update(lv, ms, True, K(), False)    # assenta
    p.x, p.y = st[0], st[1]; p.vx = p.vy = 0.0; p.ground = True
    for frames, keys, jmp in plan:
        for f in range(frames):
            p.update(lv, ms, True, keys, jmp and f == 0, pygame.K_SPACE if jmp else None)
            if hit(lv, p): return None
    # termina: segue o movimento da ultima etapa (sem pular) ate pousar
    keys = plan[-1][1]
    for f in range(140):
        if p.ground and not p.climbing: break
        if p.climbing: break
        p.update(lv, ms, True, keys, False)
        if hit(lv, p): return None
    return p

def plans():
    out = []
    for d in (1, -1):
        for run in (0, 1):
            for pre in (0, 10, 24):
                for hold in (8, 60):
                    kk = K(left=d < 0, right=d > 0, run=run, space=0)
                    jk = K(left=d < 0, right=d > 0, run=run, space=1)
                    holdk = jk
                    seq = []
                    if pre: seq.append((pre, kk, False))
                    seq.append((hold, holdk, True))
                    seq.append((0, kk, False))
                    out.append(seq)
        for run in (0, 1):
            out.append([(70, K(left=d < 0, right=d > 0, run=run), False)])
    # escalada: anda ate a escada, sobe, depois sai para o lado
    for d in (1, -1):
        for pre in (0, 6, 14, 26):
            for up in (60, 110, 160):
                out.append([(pre, K(left=d < 0, right=d > 0), False), (up, K(up=1), False), (40, K(left=d < 0, right=d > 0, up=0), False)])
            for dn in (60, 110):
                out.append([(pre, K(left=d < 0, right=d > 0), False), (dn, K(down=1), False), (40, K(left=d < 0, right=d > 0), False)])
    return out

QUICK = os.environ.get('QUICK') == '1'

def verify(idx, verbose=True):
    lv = build(idx); ms = static_platforms(lv); P = plans()
    start = (lv.start[0], lv.start[1] - PH, 0, 0, True)
    seen, heap, reach = {}, [], []
    def key(st): return (int(st[0]) // 6, int(st[1]) // 3)
    heapq.heappush(heap, (0, 0, start)); seen[key(start)] = start; n = 0
    fx = lv.frag[0]
    while heap and n < 2500:
        _, _, st = heapq.heappop(heap); n += 1; reach.append(st)
        if QUICK and st[0] > fx - 10: break
        for plan in P:
            q = run_macro(lv, ms, st, plan)
            if q is None or not (q.ground or q.climbing): continue
            ns = (q.x, q.y, 0, 0, True)
            if q.climbing: ns = (q.x, q.y, 0, 0, False)
            if q.climbing: continue
            k = key(ns)
            if k in seen: continue
            seen[k] = ns; heapq.heappush(heap, (-ns[0], n, ns))
    maxx = max(r[0] for r in reach)
    ok = maxx > fx - 10
    # checkpoints / orbes: algum estado alcancado perto?
    def near(x, y, rx=40, ry=60): return any(abs(s[0] - x) < rx and abs(s[1] + PH - y) < ry for s in seen.values())
    cpmiss = [c for c in lv.cps if not near(c[0], c[1])]
    orbmiss = [o for o in lv.orbs if not any(abs(s[0] - o[0]) < 60 and abs((s[1] + PH / 2) - o[1]) < 40 for s in seen.values())]
    if verbose:
        print(f"nivel {idx + 1}: {'OK' if ok else 'FALHOU'}  (alcancou x={int(maxx)} de {fx}; {len(seen)} estados; cps fora: {len(cpmiss)}; brindes fora: {len(orbmiss)})")
        if not ok:
            print("   ultimo estado alcancado:", [int(v) for v in max(reach, key=lambda r: r[0])[:2]], "col", int(maxx // T))
    return ok, cpmiss, orbmiss

if __name__ == "__main__":
    pygame.init()
    idxs = [int(a) - 1 for a in sys.argv[1:]] or list(range(9))
    bad = 0
    for i in idxs:
        ok, cm, om = verify(i); bad += (not ok)
    sys.exit(1 if bad else 0)
