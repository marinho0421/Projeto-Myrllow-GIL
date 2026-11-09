"""Efeitos sonoros gerados por codigo (sem arquivos externos)."""
import array, math, pygame

RATE = 22050
SFX = {  # lista de (frequencia, duracao)
    "jump": [(330, .05), (520, .08)], "die": [(300, .08), (200, .08), (120, .18)],
    "item": [(660, .06), (880, .06), (1180, .12)], "check": [(440, .07), (660, .1)],
    "ok": [(523, .08), (784, .14)], "bad": [(180, .16)], "click": [(500, .03)],
    "land": [(150, .04)], "portal": [(300, .1), (400, .1), (600, .1), (900, .2)],
}

def make(seq, vol=.25):
    buf = array.array("h")
    for f, d in seq:
        n = int(RATE * d)
        for i in range(n):
            env = 1 - i / n
            v = 1 if math.sin(2 * math.pi * f * i / RATE) >= 0 else -1
            buf.append(int(v * vol * env * 32767))
    return pygame.mixer.Sound(buffer=buf.tobytes())

class Audio:
    def __init__(self):
        self.on, self.snd, self.ok = True, {}, True
        try:
            pygame.mixer.init(RATE, -16, 1)
        except Exception:
            self.ok = False

    def build(self, name):
        if self.ok:
            self.snd[name] = make(SFX[name])

    def play(self, name):
        if self.on and name in self.snd:
            self.snd[name].play()
