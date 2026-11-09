"""Gera assets/sprites/emilia.png (12 quadros 29x54, mesma ordem/geometria da folha do Joao)
a partir da unica pose da textura `maria-4x.png`. Nao usa nenhum pixel do Joao: so a *geometria*
(altura do corpo e dos pes de cada quadro) para que corrida/pulo tenham o mesmo ritmo.
Quadros: 0 parado, 1-6 corrida, 7 impulso, 8 subindo, 9 apice, 10 caindo, 11 aterrissagem."""
import os, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "textures", "maria-4x.png")
OUT = os.path.join(ROOT, "assets", "sprites", "emilia.png")
FW, FH = 29, 54
im4 = Image.open(SRC).convert("RGBA")
base = im4.resize((im4.width // 4, im4.height // 4), Image.NEAREST)       # 240x240 -> 60x60 (pixel real)
bb = base.getbbox()                                                       # figura: 18 x 41
fig = base.crop(bb)                                                       # coluna 0 = x 21
FWID, FHGT = fig.size
HIP = 31                                                                  # primeira linha com as pernas separadas
X0 = 6 - 0                                                                # alinha o centro ao do Joao (col 5..24)

def px(img, x, y): return img.getpixel((x, y))

def leg_strip(x0, x1):
    return fig.crop((x0, HIP, x1 + 1, FHGT))                              # pernas + sapato (10 linhas)

LEFT, RIGHT = leg_strip(0, 9), leg_strip(10, FWID - 1)
LX, RX = 0, 10
SHOE = 4                                                                  # linhas do sapato preservadas

def resample_rows(strip, n):
    """Ajusta a altura da perna para n linhas, esticando/encolhendo so a coxa/canela (o sapato fica intacto)."""
    h = strip.height; top = h - SHOE; out = Image.new("RGBA", (strip.width, n))
    ntop = max(0, n - SHOE)
    for y in range(n):
        sy = (y * top // max(1, ntop)) if y < ntop else top + (y - ntop)
        out.paste(strip.crop((0, min(sy, h - 1), strip.width, min(sy, h - 1) + 1)), (0, y))
    return out

def shear(strip, dx):
    """Inclina a perna: topo fixo no quadril, base deslocada dx pixels."""
    out = Image.new("RGBA", (strip.width + 8, strip.height)); h = strip.height
    for y in range(h):
        out.paste(strip.crop((0, y, strip.width, y + 1)), (4 + round(dx * (y + 1) / h), y))
    return out


import math
SK, SH, OUTL = (238, 188, 154, 255), (191, 157, 133, 255), (0, 0, 0, 255)
SLV, CUFF = (230, 226, 226, 255), (22, 9, 134, 255)

def draw_arm(f, side, ang, top, length=11):
    """Desenha um braco levantado (manga branca, punho azul, pele, contorno preto) com as cores da Emilia."""
    px0 = X0 + (4 if side < 0 else 13)                  # ombro (colunas do contorno do tronco)
    py0 = top + 19
    a = math.radians(ang)
    d = (-math.sin(a), math.cos(a)) if side < 0 else (math.sin(a), math.cos(a))
    cells = {}
    for i in range(length * 4 + 1):
        t = i / 4
        cx, cy = px0 + d[0] * t, py0 + d[1] * t
        col = SLV if t < 3 else CUFF if t < 4 else SK
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                x, y = round(cx) + ox, round(cy) + oy
                if math.hypot(x - cx, y - cy) <= 1.25: cells[(x, y)] = col
    # sombra de pele no lado de baixo
    for (x, y), c in list(cells.items()):
        if c == SK and (x, y + 1) not in cells: cells[(x, y)] = SH
    for (x, y) in list(cells):
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in cells: cells[(nx, ny)] = OUTL
    for (x, y), c in cells.items():
        if 0 <= x < FW and 0 <= y < FH and (c != OUTL or f.getpixel((x, y))[3] == 0): f.putpixel((x, y), c)

def compose(dy, lift, dxl, dxr, arms=None):
    f = Image.new("RGBA", (FW, FH)); top = 13 + dy
    body = fig.crop((0, 0, FWID, HIP)).copy()
    if arms:                                                             # remove os bracos pendurados
        for y in range(21, 29):
            for x in list(range(0, 4)) + list(range(14, 17)):
                if x < FWID: body.putpixel((x, y), (0, 0, 0, 0))
    ground = FH - 1 - lift; ltop = 44 + dy
    n = max(SHOE + 1, ground - ltop + 1)
    for strip, sx, dx in ((LEFT, LX, dxl), (RIGHT, RX, dxr)):
        s = shear(resample_rows(strip, n), dx)
        f.alpha_composite(s, (X0 + sx - 4, ltop))
    f.alpha_composite(body, (X0, top))
    if arms:
        for side in (-1, 1): draw_arm(f, side, arms, top)
    return f

RUN = [(+3, 0, -3, 0), (+2, 0, -2, 1), (0, 0, +1, 3), (-3, 0, +3, 0), (-2, 1, +2, 0), (+1, 3, 0, 0)]
BOB = [1, 0, -1, 1, 0, -1]
frames = [compose(0, 0, 0, 0)]
for (a, b, c, d), bob in zip(RUN, BOB):
    # perna da frente/de tras: (dx, lift) para cada perna
    f = compose(bob, 0, a, c)
    if b or d:
        f = compose(bob, max(b, d) if b == d else 0, a, c)
    frames.append(f)
frames.append(compose(+4, 0, -1, +1))                                    # 7 impulso (agachada)
frames.append(compose(-4, 3, -1, +2, arms=150))                          # 8 subindo
frames.append(compose(-9, 8, -3, +3, arms=135))                          # 9 apice
frames.append(compose(-5, 3, -2, +3, arms=105))                          # 10 caindo
frames.append(compose(+2, 0, -1, +1))                                    # 11 aterrissagem
sheet = Image.new("RGBA", (FW * len(frames), FH))
for i, f in enumerate(frames): sheet.alpha_composite(f, (i * FW, 0))
os.makedirs(os.path.dirname(OUT), exist_ok=True); sheet.save(OUT)
print("ok", OUT, sheet.size)
