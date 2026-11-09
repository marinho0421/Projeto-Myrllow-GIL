"""Loop principal, maquina de estados, telas e desenho. Estados: load title story settings intro play pause clear jewel exam end"""
import math, sys, pygame
from .const import *
TILE = T
from . import lang, save, assets
from .audio import Audio
from .lang import T
from .level import build
from .entities import Player, Enemy, Mover

EXAM_Q = [2, 5, 8]

def run(selftest=False):
    Game(selftest).loop()

class Game:
    def __init__(s, selftest=False):
        pygame.init(); pygame.display.set_caption("Joia do Conhecimento")
        s.win = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        s.scr, s.clock = pygame.Surface((W, H)), pygame.time.Clock()
        s.sv = save.load(); lang.cur = s.sv["lang"] if s.sv["lang"] in lang.LANGS else "pt"
        s.audio = Audio(); s.audio.on = s.sv["sound"]; s.A = assets.Assets(s.audio); s.steps = s.A.steps(); s.nstep = len(s.steps)
        s.fs, s.fm, s.fb = pygame.font.Font(None, 18), pygame.font.Font(None, 26), pygame.font.Font(None, 44)
        s.state, s.t, s.sel, s.rects, s.done, s.page = "load", 0, 0, [], s.sv["done"], 0
        s.jump_pressed, s.cam, s.quiz, s.world_anim = False, 0.0, False, 0
        s.dest, s.selftest = (0, 0, 1, 1), selftest

    # ---------- utilidades ----------
    def txt(s, text, pos, col=WHITE, font=None, center=False, sh=True):
        font = font or s.fs; img = font.render(text, False, col)
        x, y = pos; x = x - img.get_width() // 2 if center else x
        if sh: s.scr.blit(font.render(text, False, BLACK), (x + 1, y + 1))
        s.scr.blit(img, (x, y)); return img.get_height()

    def para(s, text, x, y, w, col=WHITE, font=None, center=False, lh=14):
        font, line = font or s.fs, ""
        for word in text.split():
            if font.size(line + " " + word)[0] > w and line:
                s.txt(line.strip(), (x + w // 2 if center else x, y), col, font, center); y += lh; line = ""
            line += " " + word
        s.txt(line.strip(), (x + w // 2 if center else x, y), col, font, center); return y + lh

    def panel(s, r, alpha=200):
        p = pygame.Surface((r[2], r[3]), pygame.SRCALPHA); p.fill((10, 12, 30, alpha)); s.scr.blit(p, r[:2])
        pygame.draw.rect(s.scr, GOLD, r, 2)

    def sfx(s, n): s.audio.play(n)

    def set_state(s, st): s.state, s.t, s.sel = st, 0, 0

    def mouse(s):
        mx, my = pygame.mouse.get_pos(); x, y, w, h = s.dest
        return (mx - x) * W / max(1, w), (my - y) * H / max(1, h)

    # ---------- menus ----------
    def items(s):
        L = s.state
        if L == "title":
            it = [(T("play"), s.new_game)]
            if s.sv["done"] > 0: it.append((T("cont"), s.continue_game))
            return it + [(T("settings"), s.open_settings), (T("quit"), s.quit)]
        if L == "settings":
            return [(f"{T('lang')}: {lang.LANG_NAMES[lang.cur]}", s.cycle_lang),
                    (f"{T('sound')}: {T('on') if s.audio.on else T('off')}", s.toggle_sound), (T("back"), s.close_settings)]
        if L == "pause":
            return [(T("resume"), lambda: s.set_state("play")), (T("restart"), s.restart_level),
                    (T("settings"), s.open_settings), (T("menu"), lambda: s.set_state("title"))]
        return []

    def draw_menu(s, y0):
        s.rects = []; mx, my = s.mouse()
        for i, (label, _) in enumerate(s.items()):
            r = pygame.Rect(W // 2 - 110, y0 + i * 32, 220, 26); s.rects.append(r)
            if r.collidepoint(mx, my) and pygame.mouse.get_rel() != (0, 0): s.sel = i
            if i == s.sel:
                pygame.draw.rect(s.scr, (60, 50, 120), r); pygame.draw.rect(s.scr, GOLD, r, 2)
            s.txt(label, (W // 2, y0 + i * 32 + 6), GOLD if i == s.sel else WHITE, s.fm, True)

    def activate(s, i):
        its = s.items()
        if 0 <= i < len(its): s.sfx("click"); its[i][1]()

    # ---------- acoes ----------
    def quit(s): pygame.quit(); sys.exit()
    def persist(s): save.write({"done": s.done, "lang": lang.cur, "sound": s.audio.on})
    def open_settings(s): s.back_to = s.state; s.set_state("settings")
    def close_settings(s): s.persist(); s.sv = save.load(); s.set_state(s.back_to)
    def cycle_lang(s): lang.cur = lang.LANGS[(lang.LANGS.index(lang.cur) + 1) % 3]; s.persist()
    def toggle_sound(s): s.audio.on = not s.audio.on; s.persist(); s.sfx("click")
    def new_game(s): s.done, s.page = 0, 0; s.set_state("story")
    def continue_game(s):
        s.done = s.sv["done"]
        s.begin_exam() if s.done >= 9 else s.start_level(s.done)

    def start_level(s, i):
        s.idx, s.lv = i, build(i); s.gate_open, s.quiz, s.qcool, s.qmsg, s.cam = False, False, 0, "", 0.0
        s.enemies = [Enemy(*e) for e in s.lv.enemies]; s.movers = [Mover(*m) for m in s.lv.movers]
        s.spawn = s.lv.start; s.reached_cp, s.player, s.dead = False, Player(s.lv.start), 0
        s.set_state("intro")

    def restart_level(s):
        s.start_level(s.idx); s.set_state("play")

    def respawn(s):
        s.player = Player(s.spawn); s.enemies = [Enemy(*e) for e in s.lv.enemies]; s.qcool = 60

    def die(s): s.dead = 50; s.sfx("die")

    # ---------- eventos ----------
    def handle(s, e):
        if e.type == pygame.QUIT: s.quit()
        if e.type == pygame.VIDEORESIZE: return
        if e.type == pygame.KEYDOWN and e.key == pygame.K_F11: pygame.display.toggle_fullscreen(); return
        st = s.state
        if st in ("title", "settings", "pause"):
            n = len(s.items())
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w): s.sel = (s.sel - 1) % n
                elif e.key in (pygame.K_DOWN, pygame.K_s): s.sel = (s.sel + 1) % n
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE): s.activate(s.sel)
                elif st == "settings" and s.sel == 0 and e.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d): s.cycle_lang()
                elif e.key == pygame.K_ESCAPE and st == "pause": s.set_state("play")
                elif e.key == pygame.K_ESCAPE and st == "settings": s.close_settings()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, r in enumerate(s.rects):
                    if r.collidepoint(s.mouse()): s.activate(i)
        elif e.type == pygame.KEYDOWN:
            ok = e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
            if st == "story" and ok:
                s.page += 1; s.sfx("click")
                if s.page > 2: s.start_level(0)
            elif st == "intro" and ok: s.set_state("play")
            elif st == "clear" and ok and s.t > 100:
                s.start_level(s.idx + 1) if s.idx < 8 else s.set_state("jewel")
            elif st == "jewel" and ok and s.t > 240: s.begin_exam()
            elif st == "end" and ok: s.set_state("title"); s.sv = save.load()
            elif st == "play":
                if s.quiz: s.quiz_key(e.key)
                elif e.key == pygame.K_ESCAPE: s.set_state("pause")
                elif e.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w): s.jump_pressed = True
            elif st == "exam": s.exam_key(e.key)

    def answer(s, i, ans):
        right = i == ans; s.sfx("ok" if right else "bad"); return right

    def quiz_key(s, k):
        c = lang.content(s.idx)
        if k == pygame.K_ESCAPE:
            s.quiz, s.qcool = False, 120; s.player.x -= 40; s.player.vx = 0; return
        if k in (pygame.K_UP, pygame.K_w): s.qsel = (s.qsel - 1) % 3
        elif k in (pygame.K_DOWN, pygame.K_s): s.qsel = (s.qsel + 1) % 3
        pick = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}.get(k, s.qsel if k in (pygame.K_RETURN, pygame.K_KP_ENTER) else None)
        if pick is not None:
            s.qsel = pick
            if s.answer(pick, c["ans"]): s.gate_open, s.quiz, s.qmsg = True, False, T("right"); s.qmsg_t = 120
            else: s.qmsg = T("wrong")

    # ---------- prova final ----------
    def begin_exam(s): s.ex = dict(i=0, ok=0, sel=0, fb=0, last=None); s.set_state("exam")

    def exam_key(s, k):
        ex = s.ex
        if ex["i"] >= 3:
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                if ex["ok"] >= 2: s.done = 9; s.persist(); s.set_state("end")
                else: s.begin_exam()
            return
        if ex["fb"]: return
        if k in (pygame.K_UP, pygame.K_w): ex["sel"] = (ex["sel"] - 1) % 3
        elif k in (pygame.K_DOWN, pygame.K_s): ex["sel"] = (ex["sel"] + 1) % 3
        pick = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}.get(k, ex["sel"] if k in (pygame.K_RETURN, pygame.K_KP_ENTER) else None)
        if pick is not None:
            ok = s.answer(pick, lang.content(EXAM_Q[ex["i"]])["ans"]); ex["ok"] += ok; ex["fb"] = 50; ex["last"] = ok

    # ---------- atualizacao ----------
    def update(s):
        s.t += 1
        if s.state == "load":
            if s.steps: s.steps.pop(0)()
            else: s.set_state("title")
        elif s.state == "play": s.update_play()
        elif s.state == "clear" and s.t == 1: s.sfx("portal")
        elif s.state == "exam" and s.ex["fb"]:
            s.ex["fb"] -= 1
            if not s.ex["fb"]: s.ex["i"] += 1; s.ex["sel"] = 0

    def update_play(s):
        lv, p = s.lv, s.player
        s.qcool = max(0, s.qcool - 1); s.qmsg_t = max(0, getattr(s, "qmsg_t", 0) - 1)
        if s.dead:
            s.dead -= 1
            if not s.dead: s.respawn()
            return
        if s.quiz: return
        for m in s.movers: m.update()
        for e in s.enemies: e.update()
        p.update(lv, s.movers, s.gate_open, pygame.key.get_pressed(), s.jump_pressed); s.jump_pressed = False
        if p.jumped: s.sfx("jump")
        r = p.rect()
        s.cam += (max(0, min(lv.width - W, p.x + PW / 2 - W / 2)) - s.cam) * 0.12
        if p.y > H + 40 or any(r.colliderect(e.rect()) for e in s.enemies) or \
           any(r.colliderect(pygame.Rect(c * TILE + 4, rr * TILE + 14, TILE - 8, 10)) for c, rr in lv.spikes if abs(c * TILE - r.x) < 60):
            return s.die()
        if not s.reached_cp and p.x > lv.cp * TILE:
            s.reached_cp, s.spawn = True, (lv.cp * TILE, GR * TILE); s.sfx("check")
        if not s.gate_open and s.qcool == 0 and abs(r.centerx - (lv.gate_col * TILE + TILE / 2)) < 44:
            s.quiz, s.qsel, s.qmsg, p.vx = True, 0, "", 0
        if r.colliderect(pygame.Rect(lv.frag[0] - 12, lv.frag[1] - 12, 28, 40)):
            s.done = max(s.done, s.idx + 1); s.persist(); s.sv = save.load(); s.sfx("item"); s.set_state("clear")

    # ---------- desenho ----------
    def draw_bg(s, w, cam):
        sky, l1, l2 = s.A.bg[w]; s.scr.blit(sky, (0, 0))
        for layer, f in ((l1, .2), (l2, .45)):
            x = -int(cam * f) % W; s.scr.blit(layer, (x - W, 0)); s.scr.blit(layer, (x, 0))

    def draw_world(s):
        lv, P, cam = s.lv, WORLDS[s.lv.world], int(s.cam)
        s.draw_bg(lv.world, cam); tick = pygame.time.get_ticks()
        for c in range(cam // TILE, (cam + W) // TILE + 2):
            for r in range(ROWS):
                k, x, y = (c, r), c * TILE - cam, r * TILE
                if k in lv.solid:
                    pygame.draw.rect(s.scr, P["tile"], (x, y, TILE, TILE))
                    if (c * 7 + r * 13) % 5 == 0: pygame.draw.rect(s.scr, tuple(v * 3 // 4 for v in P["tile"]), (x + 6, y + 8, 4, 4))
                    if (c, r - 1) not in lv.solid: pygame.draw.rect(s.scr, P["top"], (x, y, TILE, 7)); pygame.draw.rect(s.scr, BLACK, (x, y + 7, TILE, 1))
                elif k in lv.plat:
                    pygame.draw.rect(s.scr, P["plat"], (x, y, TILE, 10)); pygame.draw.rect(s.scr, BLACK, (x, y, TILE, 10), 1)
                    pygame.draw.rect(s.scr, WHITE, (x + 2, y + 2, TILE - 4, 2))
                if k in lv.spikes:
                    for o in (0, 12): pygame.draw.polygon(s.scr, (210, 210, 220), [(x + o, y + TILE), (x + o + 6, y + 10), (x + o + 12, y + TILE)]); pygame.draw.polygon(s.scr, BLACK, [(x + o, y + TILE), (x + o + 6, y + 10), (x + o + 12, y + TILE)], 1)
                if k in lv.gate and not s.gate_open:
                    pygame.draw.rect(s.scr, (150 + 60 * ((c + r + tick // 120) % 2), 60, 220), (x + 6, y, TILE - 12, TILE))
        # sinal, checkpoint, fragmento
        sx = lv.sign * TILE - cam; pygame.draw.rect(s.scr, (90, 60, 30), (sx + 10, GR * TILE - 20, 4, 20)); pygame.draw.rect(s.scr, (240, 220, 140), (sx + 2, GR * TILE - 34, 20, 16)); s.txt("i", (sx + 12, GR * TILE - 33), BLACK, s.fm, True, False)
        cx = lv.cp * TILE - cam; pygame.draw.rect(s.scr, (230, 230, 230), (cx, GR * TILE - 48, 3, 48)); pygame.draw.rect(s.scr, (60, 200, 80) if s.reached_cp else (200, 60, 60), (cx + 3, GR * TILE - 48, 16, 10))
        fx, fy = lv.frag[0] - cam, lv.frag[1] + int(math.sin(tick / 250) * 3)
        s.scr.blit(pygame.transform.scale(s.A.gems[lv.world], (24, 24)), (fx - 12, fy - 12))
        for m in s.movers: pygame.draw.rect(s.scr, (170, 120, 70), (int(m.x) - cam, int(m.y), m.W, 8)); pygame.draw.rect(s.scr, BLACK, (int(m.x) - cam, int(m.y), m.W, 8), 1)
        for e in s.enemies:
            im = s.A.enemy[lv.world][(e.t // 12) % 2]; s.scr.blit(im if e.dir > 0 else pygame.transform.flip(im, True, False), (int(e.x) - cam, int(e.y)))
        p = s.player
        if not (s.dead and s.dead % 6 < 3):
            im = (s.A.frames if p.face > 0 else s.A.frames_l)[p.frame()]
            s.scr.blit(im, (int(p.x + PW / 2 - (15 if p.face > 0 else 14)) - cam, int(p.y + PH - 53)))

    def draw_hud(s):
        for i in range(9):
            g = s.A.gems[i // 3] if i < s.done else None
            if g: s.scr.blit(g, (8 + i * 14, 6))
            else: pygame.draw.rect(s.scr, (40, 40, 60), (11 + i * 14, 9, 6, 6))
        s.txt(f"{T('w%d' % (s.lv.world + 1))} - {T('level')} {s.idx % 3 + 1}/3", (W - 8 - s.fs.size(f"{T('w%d' % (s.lv.world + 1))} - {T('level')} {s.idx % 3 + 1}/3")[0], 8))

    def draw_quiz(s, c, sel, msg, y=60):
        s.panel((60, y, 520, 220)); s.txt(T("quiz"), (W // 2, y + 10), GOLD, s.fm, True)
        yy = s.para(c["q"], 80, y + 40, 480, WHITE, s.fm, True, 18)
        for i, o in enumerate(c["opts"]):
            r = pygame.Rect(100, yy + 8 + i * 32, 440, 26)
            pygame.draw.rect(s.scr, (60, 50, 120) if i == sel else (30, 30, 60), r); pygame.draw.rect(s.scr, GOLD if i == sel else (90, 90, 140), r, 2)
            s.txt(f"{i + 1}. {o}", (r.x + 10, r.y + 6), GOLD if i == sel else WHITE)
        s.txt(msg or T("quizhint"), (W // 2, y + 196), (255, 120, 120) if msg else (200, 200, 220), s.fs, True)

    def draw(s):
        st, S = s.state, s.scr
        if st == "load":
            S.fill((12, 14, 30)); s.txt(T("loading"), (W // 2, 150), WHITE, s.fm, True)
            pygame.draw.rect(S, GOLD, (170, 190, 300, 14), 2); pygame.draw.rect(S, GOLD, (173, 193, int(294 * (1 - len(s.steps) / s.nstep)), 8))
            return
        if st in ("title", "settings", "story", "jewel", "end", "exam", "intro"):
            s.draw_bg(1 if st in ("jewel", "end") else 0 if st != "exam" else 2, s.t * 0.6)
        if st == "title":
            s.txt(T("title"), (W // 2, 44), GOLD, s.fb, True); s.para(T("sub"), 120, 92, 400, WHITE, s.fs, True)
            s.draw_menu(150); s.txt(f"{T('progress')}: {s.sv['done']}/9", (W // 2, 330), WHITE, s.fs, True)
            S.blit(s.A.frames[0 if s.t % 60 < 30 else 1 + s.t // 6 % 6], (20, 256))
        elif st == "settings": s.panel((130, 70, 380, 220)); s.txt(T("settings"), (W // 2, 90), GOLD, s.fm, True); s.draw_menu(140)
        elif st == "story":
            s.panel((50, 60, 540, 240)); s.para(T(f"story{s.page + 1}"), 80, 110, 480, WHITE, s.fm, True, 22)
            S.blit(pygame.transform.scale(s.A.frames[0], (58, 108)), (W // 2 - 29, 175)); s.txt(T("enter"), (W // 2, 308), GOLD, s.fs, True)
        elif st == "intro":
            s.panel((70, 70, 500, 220)); w = s.lv.world
            s.txt(T(f"w{w + 1}"), (W // 2, 90), GOLD, s.fm, True); s.txt(f"{T('level')} {s.idx % 3 + 1}/3", (W // 2, 120), WHITE, s.fm, True)
            y = s.para(T("goal"), 90, 155, 460, WHITE, s.fs, True)
            if w == 2: y = s.para(T("fic"), 90, y + 6, 460, (180, 220, 255), s.fs, True)
            if s.idx == 0: s.para(T("controls"), 90, y + 6, 460, (255, 230, 150), s.fs, True)
            s.txt(T("enter"), (W // 2, 262), GOLD, s.fs, True)
        elif st in ("play", "pause", "clear"):
            s.draw_world(); s.draw_hud(); lv = s.lv; p = s.player
            if st == "play" and not s.quiz:
                if abs(p.rect().centerx - (lv.sign * TILE + TILE // 2)) < 70:
                    s.panel((40, 34, 560, 60), 215); s.txt(T("know"), (50, 38), GOLD); s.para(lang.content(s.idx)["fact"], 50, 54, 540, WHITE, s.fs, False, 14)
                if s.idx == 0 and s.cam < 500: s.para(T("controls"), 20, H - 30, 600, (255, 240, 170), s.fs, True)
                if s.qmsg_t: s.txt(s.qmsg, (W // 2, 110), (120, 255, 140), s.fm, True)
            if s.dead: ov = pygame.Surface((W, H), pygame.SRCALPHA); ov.fill((200, 0, 0, 60)); S.blit(ov, (0, 0))
            if s.quiz: s.draw_quiz(lang.content(s.idx), s.qsel, s.qmsg)
            if st == "pause":
                s.panel((100, 24, 440, 312), 235); s.txt(T("paused"), (W // 2, 34), GOLD, s.fm, True); s.draw_menu(66)
                s.para(T("controls"), 110, 206, 420, (255, 240, 170), s.fs, True); s.txt(T("progress"), (W // 2, 248), WHITE, s.fs, True)
                for i in range(9): S.blit(s.A.gems[i // 3] if i < s.done else pygame.Surface((12, 12)), (W // 2 - 70 + i * 16, 268))
                s.txt(f"{s.done}/9", (W // 2, 292), GOLD, s.fs, True)
            if st == "clear":
                fx, fy = s.lv.frag[0] - int(s.cam), s.lv.frag[1]
                for k in range(8): pygame.draw.circle(S, tuple(int(v) for v in (WORLDS[s.lv.world]["gem"])), (int(fx + math.cos(s.t * .2 + k) * (50 - s.t % 50 * .8)), int(fy + math.sin(s.t * .2 + k) * (50 - s.t % 50 * .8))), 3)
                if s.t > 100:
                    s.panel((90, 100, 460, 120)); s.para(T("clear"), 110, 125, 420, WHITE, s.fm, True, 22); s.txt(T("enter"), (W // 2, 190), GOLD, s.fs, True)
        elif st == "jewel":
            n = min(9, s.t // 20 + 1); cx, cy = W // 2, 150; k = min(1, max(0, (s.t - 180) / 60))
            for i in range(n):
                a = s.t * 0.03 + i * 2 * math.pi / 9; rad = 90 * (1 - k)
                S.blit(s.A.gems[i // 3], (int(cx + math.cos(a) * rad) - 6, int(cy + math.sin(a) * rad) - 6))
            if k >= 1: S.blit(pygame.transform.scale(assets.gem(GOLD, 12), (72, 72)), (cx - 36, cy - 36))
            s.para(T("jewel"), 100, 250, 440, WHITE, s.fm, True, 22)
            if s.t > 240: s.txt(T("enter"), (W // 2, 320), GOLD, s.fs, True)
        elif st == "exam":
            ex = s.ex; s.txt(f"{T('exam')}  {min(ex['i'] + 1, 3)}/3", (W // 2, 20), GOLD, s.fm, True)
            if ex["i"] < 3:
                s.draw_quiz(lang.content(EXAM_Q[ex["i"]]), ex["sel"], "", 50)
                if ex["fb"]: s.txt(T("right") if ex["last"] else T("wrong"), (W // 2, 300), (120, 255, 140) if ex["last"] else (255, 120, 120), s.fm, True)
            else:
                s.panel((100, 100, 440, 140)); s.txt(f"{T('score')}: {ex['ok']}/3", (W // 2, 120), GOLD, s.fm, True)
                s.para(T("exam_ok") if ex["ok"] >= 2 else T("exam_bad"), 120, 160, 400, WHITE, s.fm, True, 22); s.txt(T("enter"), (W // 2, 214), GOLD, s.fs, True)
        elif st == "end":
            S.blit(pygame.transform.scale(assets.gem(GOLD, 12), (72, 72)), (W // 2 - 36, 40)); s.txt(T("end"), (W // 2, 130), GOLD, s.fb, True)
            s.para(T("end_text"), 120, 180, 400, WHITE, s.fm, True, 22); S.blit(s.A.frames[0], (W // 2 - 14, 240)); s.txt(T("enter"), (W // 2, 330), GOLD, s.fs, True)

    def present(s):
        ww, wh = s.win.get_size(); sc = min(ww / W, wh / H); sc = int(sc) if sc >= 1 else sc
        w, h = max(1, int(W * sc)), max(1, int(H * sc)); s.dest = ((ww - w) // 2, (wh - h) // 2, w, h)
        s.win.fill(BLACK); s.win.blit(pygame.transform.scale(s.scr, (w, h)), s.dest[:2]); pygame.display.flip()   # sem suavizacao

    def loop(s):
        n = 0
        while True:
            for e in pygame.event.get(): s.handle(e)
            s.update(); s.draw(); s.present(); s.clock.tick(FPS); n += 1
            if s.selftest and n > s.selftest: return
