"""Carregamento (em etapas, para a tela de carregamento) de sprites, fundos e efeitos."""
import os, random, pygame
from .const import *
from . import audio as au

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FW, FH = 29, 54       # tamanho de cada frame da spritesheet do protagonista

def enemy_surf(w, f):
    s = pygame.Surface((18, 12), pygame.SRCALPHA)
    col = [(60, 150, 60), (200, 120, 40), (150, 60, 160)][w]
    pygame.draw.rect(s, BLACK, (1, 1, 16, 9)); pygame.draw.rect(s, col, (2, 2, 14, 7))
    for x in (4, 11): pygame.draw.rect(s, WHITE, (x, 3, 3, 3)); pygame.draw.rect(s, BLACK, (x + 1, 4, 1, 2))
    pygame.draw.rect(s, (200, 40, 40), (2, 7, 14, 1))                       # faixa de aviso
    for i in range(4): pygame.draw.rect(s, BLACK, (2 + i * 4, 9 + (f + i) % 2, 2, 2 - (f + i) % 2 + 1))
    if w == 1: pygame.draw.rect(s, BLACK, (15, 0, 2, 3))                      # ferrao
    return s

def gem(c, size=12):
    s = pygame.Surface((size, size), pygame.SRCALPHA); h = size // 2
    pts = [(h, 0), (size - 1, h), (h, size - 1), (0, h)]
    pygame.draw.polygon(s, c, pts); pygame.draw.polygon(s, WHITE, pts, 1)
    pygame.draw.rect(s, WHITE, (h - 1, 2, 2, 2)); return s

def bg_layers(w):
    rng = random.Random(5 + w); P = WORLDS[w]
    sky = pygame.Surface((W, H)); a, b = P["sky"]
    for y in range(H):
        t = y / H; pygame.draw.line(sky, tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)), (0, y), (W, y))
    L1, L2 = pygame.Surface((W, H), pygame.SRCALPHA), pygame.Surface((W, H), pygame.SRCALPHA)
    if w == 0:
        for x in range(0, W, 40): pygame.draw.circle(L1, (50, 120, 80), (x + 20, 250 + rng.randint(-10, 10)), 60)
        for x in range(10, W, 70):
            h = rng.randint(120, 190); pygame.draw.rect(L2, (70, 48, 30), (x, 264 - h, 12, h))
            pygame.draw.circle(L2, (34, 110, 44), (x + 6, 264 - h), 34); pygame.draw.circle(L2, (46, 134, 56), (x - 8, 264 - h + 14), 22)
    elif w == 1:
        pygame.draw.circle(sky, (255, 240, 180), (500, 80), 36)
        for x in range(0, W, 120): pygame.draw.ellipse(L1, (220, 160, 90), (x - 40, 230, 220, 120))
        for x, h in ((90, 90), (380, 130)): pygame.draw.polygon(L2, (190, 130, 70), [(x - h, 270), (x, 270 - h), (x + h, 270)])
    else:
        for x in range(0, W, 36):
            h = rng.randint(70, 150); pygame.draw.rect(L1, (70, 66, 100), (x, 270 - h, 34, h))
            for wy in range(270 - h + 8, 262, 16): pygame.draw.rect(L1, (255, 220, 120), (x + 8, wy, 4, 6))
        pygame.draw.rect(L2, (92, 88, 100), (260, 110, 90, 160))                        # torre estilo fortaleza
        for x in range(260, 350, 18): pygame.draw.rect(L2, (92, 88, 100), (x, 98, 10, 14))
        pygame.draw.rect(L2, (20, 20, 20), (295, 200, 20, 70))
        pygame.draw.rect(L2, (40, 70, 200), (430, 90, 8, 24)); pygame.draw.rect(L2, WHITE, (438, 90, 8, 24)); pygame.draw.rect(L2, (200, 40, 40), (446, 90, 8, 24))
        pygame.draw.rect(L2, (60, 50, 40), (428, 90, 2, 180))
    return sky, L1, L2

class Assets:
    def __init__(s, audio):
        s.audio, s.frames, s.frames_l, s.enemy, s.gems, s.bg = audio, [], [], [], [], []

    def steps(s):
        def sheet():
            im = pygame.image.load(os.path.join(ROOT, "assets", "sprites", "protagonista.png")).convert_alpha()
            s.frames = [im.subsurface((i * FW, 0, FW, FH)).copy() for i in range(im.get_width() // FW)]
            s.frames_l = [pygame.transform.flip(f, True, False) for f in s.frames]
        def enemies(): s.enemy = [[enemy_surf(w, f) for f in (0, 1)] for w in range(3)]
        def gems(): s.gems = [gem(WORLDS[w]["gem"]) for w in range(3)]
        st = [sheet, enemies, gems]
        st += [(lambda w=w: s.bg.append(bg_layers(w))) for w in range(3)]
        st += [(lambda n=n: s.audio.build(n)) for n in au.SFX]
        return st
