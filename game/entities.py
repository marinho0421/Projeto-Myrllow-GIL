import pygame
from .const import *

class Enemy:
    def __init__(s, x, y, x0, x1, sp):
        s.x, s.y, s.x0, s.x1, s.sp, s.dir, s.t = x, y, x0, x1, sp, 1, 0
    def update(s):
        s.x += s.dir * s.sp; s.t += 1
        if s.x > s.x1 or s.x < s.x0: s.dir *= -1
    def rect(s): return pygame.Rect(int(s.x) + 1, int(s.y) + 2, 16, 10)

class Mover:
    W = 72
    def __init__(s, x, y, x0, x1, sp):
        s.x, s.y, s.x0, s.x1, s.sp, s.dir, s.dx = x, y, x0, x1, sp, 1, 0
    def update(s):
        old = s.x; s.x += s.dir * s.sp
        if s.x > s.x1 or s.x < s.x0: s.dir *= -1
        s.dx = s.x - old
    def rect(s): return pygame.Rect(int(s.x), int(s.y), s.W, 8)

class Player:
    def __init__(s, pos):
        s.x, s.y = pos[0], pos[1] - PH       # canto superior esquerdo da hitbox
        s.vx = s.vy = 0.0
        s.ground, s.coyote, s.buf, s.face, s.anim, s.land, s.takeoff = False, 0, 0, 1, 0.0, 0, 0
        s.riding = None
    def rect(s): return pygame.Rect(round(s.x), round(s.y), PW, PH)

    def tiles(s, lv, gate_open, r):
        for c in range(r.left // T, r.right // T + 1):
            for row in range(r.top // T, r.bottom // T + 1):
                k = (c, row)
                if k in lv.solid or k in lv.plat or (k in lv.gate and not gate_open):
                    yield pygame.Rect(c * T, row * T, T, T)

    def update(s, lv, movers, gate_open, keys, jump_pressed):
        d = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        tgt = d * (RUN if run else WALK)
        acc = 0.45 if s.ground else 0.25
        s.vx += max(-acc, min(acc, tgt - s.vx))
        if d: s.face = d
        s.buf = 8 if jump_pressed else max(0, s.buf - 1)
        s.coyote = 6 if s.ground else max(0, s.coyote - 1)
        if s.buf and s.coyote:
            s.vy, s.buf, s.coyote, s.ground, s.takeoff = JUMP, 0, 0, False, 3
            s.jumped = True
        else: s.jumped = False
        if not (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and s.vy < -3: s.vy = -3  # pulo variavel
        if s.takeoff: s.takeoff -= 1
        # carregado por plataforma movel
        if s.riding: s.x += s.riding.dx
        s.x += s.vx
        r = s.rect()
        for t in s.tiles(lv, gate_open, r):
            if r.colliderect(t):
                s.x = t.left - PW if s.vx > 0 or (s.riding and s.riding.dx > 0) else t.right
                s.vx = 0; r = s.rect()
        s.x = max(0, min(lv.width - PW, s.x))
        # vertical
        was = s.ground; prev_bottom = s.rect().bottom
        s.vy = min(MAXFALL, s.vy + GRAV); s.y += s.vy
        s.ground, s.riding = False, None
        r = s.rect()
        for t in s.tiles(lv, gate_open, r):
            if r.colliderect(t):
                if s.vy > 0: s.y = t.top - PH; s.ground = True
                else: s.y = t.bottom
                s.vy = 0; r = s.rect()
        if s.vy >= 0:
            for m in movers:
                mr = m.rect()
                if r.colliderect(mr) and prev_bottom <= mr.top + 3:
                    s.y = mr.top - PH; s.vy = 0; s.ground = True; s.riding = m; r = s.rect()
        if not s.ground and s.vy >= 0:            # sonda 1px abaixo: evita 'piscar' do estado no chao
            probe = s.rect().move(0, 1)
            if any(probe.colliderect(t) for t in s.tiles(lv, gate_open, probe)):
                s.y = round(s.y); s.vy, s.ground = 0, True
            else:
                for m in movers:
                    mr = m.rect()
                    if probe.colliderect(mr) and s.rect().bottom <= mr.top + 1: s.vy, s.ground, s.riding = 0, True, m
        if s.ground and not was: s.land = 6
        elif s.land: s.land -= 1
        s.anim += abs(s.vx) * 0.11

    def frame(s):
        """0 parado, 1-6 corrida, 7 impulso, 8 subindo, 9 apice, 10 caindo, 11 aterrissagem"""
        if not s.ground:
            if s.takeoff > 1: return 7
            return 8 if s.vy < -3 else 9 if s.vy < 1.5 else 10
        if s.land: return 11
        return 1 + int(s.anim) % 6 if abs(s.vx) > 0.3 else 0
