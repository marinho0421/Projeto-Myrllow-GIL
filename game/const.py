"""Constantes globais. Resolucao logica 640x360, ampliada com nearest-neighbor."""
W, H, T, FPS = 640, 360, 24, 60
ROWS, GR = 15, 11            # linhas do mapa / linha do chao padrao
GRAV, MAXFALL = 0.4, 9.0
WALK, RUN, JUMP = 1.7, 2.7, -7.8
PW, PH = 14, 38              # hitbox do protagonista

# paleta por mundo: ceu (topo, base), bloco, topo do bloco, plataforma, cor do fragmento
WORLDS = [
    dict(sky=((88, 160, 110), (190, 230, 170)), tile=(96, 66, 42), top=(58, 150, 50), plat=(150, 104, 60), gem=(80, 230, 120)),
    dict(sky=((235, 160, 90), (255, 228, 160)), tile=(196, 146, 80), top=(236, 196, 116), plat=(150, 100, 60), gem=(255, 200, 60)),
    dict(sky=((60, 70, 130), (240, 160, 130)), tile=(120, 70, 66), top=(140, 134, 146), plat=(96, 92, 110), gem=(90, 160, 255)),
]
WHITE, BLACK, GOLD = (255, 255, 255), (0, 0, 0), (255, 207, 0)
