"""Carregamento (em etapas, para a tela de carregamento) de sprites, fundos e efeitos."""
import os, random, pygame
from .const import *
from . import audio as au

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FW, FH = 29, 54       # tamanho de cada frame da spritesheet (Joao e Emilia usam o mesmo layout de 12 quadros)
SHEETS = {"joao": "protagonista.png", "emilia": "emilia.png"}
# texturas enviadas (copiadas para assets/textures; os originais do pacote nao sao alterados)
TEX_GEMS = ["joiaverde-4x.png", "joiamarela-4x.png", "joiaroxa-4x.png"]   # fragmentos: floresta, deserto, cidade (ultimo bioma)
TEX_LOGO = "schoolrushr-4x.png"
FOREST_TEX = dict(sky="soceu-4x.png", trees="soarvore-4x.png", ground="sograma-4x.png")  # SOMENTE na floresta
TREE_Y = 60            # topo da camada de arvores na tela

def tex(name):
    return pygame.image.load(os.path.join(ROOT, "assets", "textures", name)).convert_alpha()

def native(img, box=None):
    """Texturas *-4x sao pixel art ampliada 4x: volta ao tamanho real por vizinho mais proximo (sem suavizar)."""
    if box: img = img.subsurface(box).copy()
    return pygame.transform.scale(img, (img.get_width() // 4, img.get_height() // 4))

def scaled(img, k):
    return pygame.transform.scale(img, (int(img.get_width() * k), int(img.get_height() * k)))

def mirrored(img):
    """Imagem + espelho: repeticao horizontal sem emenda visivel."""
    w, h = img.get_size(); out = pygame.Surface((w * 2, h), pygame.SRCALPHA)
    out.blit(img, (0, 0)); out.blit(pygame.transform.flip(img, True, False), (w, 0)); return out

def fly_surf(w, f):
    s = pygame.Surface((18, 12), pygame.SRCALPHA)
    body = [(230, 190, 40), (120, 80, 50), (110, 110, 130)][w]; wing = [(230, 240, 255), (200, 170, 130), (90, 90, 110)][w]
    pygame.draw.ellipse(s, BLACK, (4, 4, 11, 7)); pygame.draw.ellipse(s, body, (5, 5, 9, 5))
    pygame.draw.rect(s, BLACK, (6, 6, 1, 3)); pygame.draw.rect(s, BLACK, (10, 6, 1, 3))
    wy = 0 if f == 0 else 3
    pygame.draw.polygon(s, BLACK, [(5, 5), (9, wy), (11, 5)]); pygame.draw.polygon(s, wing, [(6, 5), (9, wy + 1), (10, 5)])
    pygame.draw.rect(s, (230, 40, 40) if w == 2 else WHITE, (13, 6, 2, 2)); return s

def orb_surf(f):
    s = pygame.Surface((12, 12), pygame.SRCALPHA); c = (255, 235, 120) if f == 0 else (255, 255, 200)
    pygame.draw.polygon(s, (190, 120, 20), [(6, 0), (8, 4), (12, 6), (8, 8), (6, 12), (4, 8), (0, 6), (4, 4)])
    pygame.draw.polygon(s, c, [(6, 2), (7, 5), (10, 6), (7, 7), (6, 10), (5, 7), (2, 6), (5, 5)]); return s

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
        s.chars, s.fly, s.orb, s.logo, s.gem_sil, s.forest = {}, [], [], None, [], {}

    def set_char(s, name):
        """Escolhe o conjunto de sprites do personagem (so muda a aparencia; fisica e hitbox sao identicas)."""
        s.frames, s.frames_l = s.chars.get(name, s.chars.get("joao", ([], [])))

    def steps(s):
        def sheet():
            for name, fn in SHEETS.items():
                im = pygame.image.load(os.path.join(ROOT, "assets", "sprites", fn)).convert_alpha()
                fr = [im.subsurface((i * FW, 0, FW, FH)).copy() for i in range(im.get_width() // FW)]
                s.chars[name] = (fr, [pygame.transform.flip(f, True, False) for f in fr])
            s.set_char("joao")
        def enemies(): s.enemy = [[enemy_surf(w, f) for f in (0, 1)] for w in range(3)]
        def gems():
            # fragmentos: texturas enviadas, recortadas e voltando ao tamanho real (nearest) -> pixels nitidos
            s.gems = []
            for fn in TEX_GEMS:
                im = tex(fn); bb = im.get_bounding_rect()
                s.gems.append(native(im, bb))
            s.gem_sil = []
            for g in s.gems:
                m = pygame.mask.from_surface(g).to_surface(setcolor=(40, 40, 70, 255), unsetcolor=(0, 0, 0, 0)); s.gem_sil.append(m)
            s.orb = [orb_surf(0), orb_surf(1)]
        def logo():
            im = tex(TEX_LOGO); s.logo = native(im, im.get_bounding_rect())         # 76x45 reais
        def forest():
            sky, trees, grd = (tex(FOREST_TEX[k]) for k in ("sky", "trees", "ground"))
            sk, tr = scaled(native(sky), 2), scaled(native(trees), 2)             # fundo: pixels 2x2
            s.forest = dict(sky=mirrored(sk), trees=mirrored(tr), sky_col=sk.get_at((0, 0))[:3], dark=tr.get_at((5, tr.get_height() - 1))[:3])
            g = native(grd, grd.get_bounding_rect()); gw, gh = g.get_size()        # chao: pixels reais (1x)
            strip = mirrored(g); wrap = pygame.Surface((strip.get_width() + T, gh), pygame.SRCALPHA)
            wrap.blit(strip, (0, 0)); wrap.blit(strip, (strip.get_width(), 0), (0, 0, T, gh))
            s.forest.update(ground=wrap, gw=strip.get_width(), top_y=0)
            # linha onde a grama comeca (primeira linha opaca) -> topo do bloco
            for y in range(gh):
                if any(wrap.get_at((x, y))[3] for x in range(0, 200, 5)): s.forest["top_y"] = y; break
        def flies(): s.fly = [[fly_surf(w, f) for f in (0, 1)] for w in range(3)]
        st = [sheet, enemies, flies, gems, logo, forest]
        st += [(lambda w=w: s.bg.append(bg_layers(w))) for w in range(3)]
        st += [(lambda n=n: s.audio.build(n)) for n in au.SFX]
        return st
