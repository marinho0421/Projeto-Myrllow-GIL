import math, pygame
from .const import *

class Enemy:
    """kind 'walk' patrulha o chao; kind 'fly' voa em onda (amp = amplitude vertical em px)."""
    def __init__(s, x, y, x0, x1, sp, kind="walk", amp=0, phase=0):
        s.x, s.y, s.y0, s.x0, s.x1, s.sp, s.dir, s.t = x, y, y, x0, x1, sp, 1, 0
        s.kind, s.amp, s.phase = kind, amp, phase
    def update(s):
        s.x += s.dir * s.sp; s.t += 1
        if s.x > s.x1 or s.x < s.x0: s.dir *= -1
        if s.kind == "fly": s.y = s.y0 + math.sin(s.t * 0.045 + s.phase) * s.amp
    def rect(s): return pygame.Rect(int(s.x) + 1, int(s.y) + 2, 16, 10)

class Mover:
    """Plataforma movel (horizontal, ou vertical se vert=True). x/y = canto superior esquerdo."""
    def __init__(s, x, y, x0, x1, sp, vert=False, w=72):
        s.x, s.y, s.x0, s.x1, s.sp, s.dir, s.dx, s.dy, s.vert, s.w = x, y, x0, x1, sp, 1, 0, 0, vert, w
        s.kind = "move"
    def update(s):
        ox, oy = s.x, s.y
        if s.vert:
            s.y += s.dir * s.sp
            if s.y > s.x1 or s.y < s.x0: s.dir *= -1
        else:
            s.x += s.dir * s.sp
            if s.x > s.x1 or s.x < s.x0: s.dir *= -1
        s.dx, s.dy = s.x - ox, s.y - oy
    def rect(s): return pygame.Rect(int(s.x), int(s.y), s.w, 8)
    def reset(s): pass

class Faller:
    """Plataforma que treme e cai depois que o jogador pisa; volta ao lugar depois de um tempo."""
    def __init__(s, x, y, w=48):
        s.x0 = s.x = x; s.y0 = s.y = y; s.w, s.dx, s.dy, s.state, s.t, s.vy, s.kind = w, 0, 0, 0, 0, 0.0, "fall"
    def touch(s):
        if s.state == 0: s.state, s.t = 1, 0
    def update(s):
        s.dx = 0; oy = s.y
        if s.state == 1:
            s.t += 1
            if s.t > 28: s.state, s.t = 2, 0
        elif s.state == 2:
            s.t += 1; s.vy = min(8.0, s.vy + 0.35); s.y += s.vy
            if s.t > 90: s.state, s.t, s.vy, s.y = 3, 0, 0.0, s.y0
        elif s.state == 3:
            s.t += 1
            if s.t > 60: s.state, s.t = 0, 0
        s.dy = s.y - oy if s.state == 2 else 0
    def rect(s):
        return pygame.Rect(int(s.x), int(s.y), s.w, 8) if s.state in (0, 1, 2) else pygame.Rect(-999, -999, 1, 1)
    def shake(s): return (s.t // 2 % 2) * 2 - 1 if s.state == 1 else 0

class Player:
    def __init__(s, pos):
        s.x, s.y = pos[0], pos[1] - PH       # canto superior esquerdo da hitbox
        s.vx = s.vy = 0.0
        s.ground, s.coyote, s.buf, s.face, s.anim, s.land, s.takeoff = False, 0, 0, 1, 0.0, 0, 0
        s.riding, s.jumped, s.climbing, s.gcool, s.canim = None, False, False, 0, 0.0
    def rect(s): return pygame.Rect(round(s.x), round(s.y), PW, PH)

    def blocks(s, lv, gate_open, r):
        """(retangulo, so_por_cima) dos blocos que tocam r. Plataformas finas sao so_por_cima (de baixo se atravessa)."""
        for c in range(r.left // T, r.right // T + 1):
            for row in range(r.top // T, r.bottom // T + 1):
                k = (c, row)
                if k in lv.solid or (k in lv.gate and not gate_open): yield pygame.Rect(c * T, row * T, T, T), False
                elif k in lv.plat: yield pygame.Rect(c * T, row * T, T, 8), True

    # --- escalada -------------------------------------------------------------
    def climb_col(s, lv):
        r = s.rect(); c = (r.centerx) // T
        for row in range(r.top // T, (r.bottom - 1) // T + 1):
            if (c, row) in lv.climb: return c
        return None

    def _hmove(s, lv, gate_open, movers_dx=0.0):
        s.x += s.vx; r = s.rect()
        for t, one in s.blocks(lv, gate_open, r):
            if not one and r.colliderect(t):
                s.x = t.left - PW if s.vx > 0 or movers_dx > 0 else t.right
                s.vx = 0; r = s.rect()
        s.x = max(0, min(lv.width - PW, s.x))

    def _climb(s, lv, gate_open, keys, d, up, down, jump_pressed):
        if jump_pressed:                                   # pular da escada/cipo
            s.climbing, s.gcool, s.vy, s.vx, s.jumped, s.takeoff = False, 14, JUMP * 0.92, d * WALK, True, 3
            s.y += s.vy; return
        s.vy, s.vx = (down - up) * CLIMB, d * 1.0
        if d: s.face = d
        s._hmove(lv, gate_open)
        c = s.climb_col(lv)
        s.y += s.vy
        if c is not None:
            top = min(r for (cc, r) in lv.climb if cc == c)
            s.y = max(s.y, (top + 1) * T - PH)             # nao sobe alem da borda do topo
        r = s.rect()
        for t, one in s.blocks(lv, gate_open, r):
            if one and not (s.vy > 0 and r.bottom - s.vy <= t.top + 1): continue
            if r.colliderect(t):
                if s.vy > 0: s.y = t.top - PH; s.ground = True; s.climbing = False; s.land = 0
                else: s.y = t.bottom
                r = s.rect()
        s.canim += (abs(s.vy) + abs(s.vx)) * 0.09
        if s.climb_col(lv) is None: s.climbing, s.gcool = False, 6

    def update(s, lv, movers, gate_open, keys, jump_pressed, jump_key=None):
        d = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        up = 1 if (keys[pygame.K_UP] or keys[pygame.K_w]) else 0
        down = 1 if (keys[pygame.K_DOWN] or keys[pygame.K_s]) else 0
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        s.gcool = max(0, s.gcool - 1); s.jumped = False
        near = s.climb_col(lv) if s.gcool == 0 else None
        if near is not None and jump_pressed and jump_key in (pygame.K_UP, pygame.K_w): jump_pressed = False   # cima agarra
        if not s.climbing and near is not None and (up or down):
            s.climbing, s.riding, s.vx, s.vy, s.ground = True, None, 0.0, 0.0, False
            s.x = near * T + (T - PW) / 2
        if s.climbing:
            s._climb(lv, gate_open, keys, d, up, down, jump_pressed); return
        tgt = d * (RUN if run else WALK)
        acc = 0.45 if s.ground else 0.25
        s.vx += max(-acc, min(acc, tgt - s.vx))
        if d: s.face = d
        s.buf = 8 if jump_pressed else max(0, s.buf - 1)
        s.coyote = 6 if s.ground else max(0, s.coyote - 1)
        if s.buf and s.coyote:
            s.vy, s.buf, s.coyote, s.ground, s.takeoff = JUMP, 0, 0, False, 3
            s.jumped = True
        if not (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and s.vy < -3: s.vy = -3  # pulo variavel
        if s.takeoff: s.takeoff -= 1
        # carregado por plataforma movel
        rdx = 0.0
        if s.riding: rdx = s.riding.dx; s.x += rdx; s.y += s.riding.dy
        s._hmove(lv, gate_open, rdx)
        # vertical
        was = s.ground; prev_bottom = s.rect().bottom
        s.vy = min(MAXFALL, s.vy + GRAV); s.y += s.vy
        s.ground, s.riding = False, None
        r = s.rect()
        for t, one in s.blocks(lv, gate_open, r):
            if one and not (s.vy > 0 and prev_bottom <= t.top + 1): continue
            if r.colliderect(t):
                if s.vy > 0: s.y = t.top - PH; s.ground = True
                else: s.y = t.bottom
                s.vy = 0; r = s.rect()
        if s.vy >= 0:
            for m in movers:
                mr = m.rect()
                if r.colliderect(mr) and prev_bottom <= mr.top + 3 + max(0, m.dy):
                    s.y = mr.top - PH; s.vy = 0; s.ground = True; s.riding = m; r = s.rect()
        if not s.ground and s.vy >= 0:            # sonda 1px abaixo: evita 'piscar' do estado no chao
            probe = s.rect().move(0, 1)
            if any(probe.colliderect(t) and (not one or s.rect().bottom <= t.top + 1) for t, one in s.blocks(lv, gate_open, probe)):
                s.y = round(s.y); s.vy, s.ground = 0, True
            else:
                for m in movers:
                    mr = m.rect()
                    if probe.colliderect(mr) and s.rect().bottom <= mr.top + 1: s.vy, s.ground, s.riding = 0, True, m
        if s.ground and not was: s.land = 6
        elif s.land: s.land -= 1
        s.anim += abs(s.vx) * 0.11

    def frame(s):
        """0 parado, 1-6 corrida, 7 impulso, 8 subindo, 9 apice, 10 caindo, 11 aterrissagem.
        Escalada reaproveita 8/9 (bracos para cima) - identico para todos os personagens."""
        if s.climbing:
            return 8 if abs(s.vy) + abs(s.vx) < 0.1 or int(s.canim) % 2 == 0 else 9
        if not s.ground:
            if s.takeoff > 1: return 7
            return 8 if s.vy < -3 else 9 if s.vy < 1.5 else 10
        if s.land: return 11
        return 1 + int(s.anim) % 6 if abs(s.vx) > 0.3 else 0
