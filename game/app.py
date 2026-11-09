"""Loop principal, maquina de estados, telas e desenho.
Estados: load title charsel levelsel story settings intro play pause clear jewel exam end"""
import math, sys, pygame
from .const import *
TILE = T
from . import lang, save, assets
from .audio import Audio
from .lang import T
from .level import build, DIFFICULTY
from .entities import Player, Enemy, Mover, Faller

EXAM_Q = [2, 5, 8]
FWc, FHc, TREE_Y = assets.FW, assets.FH, assets.TREE_Y

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
        s.char, s.chosen, s.csel, s.after_char = s.sv["char"], s.sv["chosen"], CHARS.index(s.sv["char"]), None
        s.demo, s.lsel, s.thumbs, s.last_mouse, s.logo3 = False, 0, {}, (0, 0), None
        s.orbs_taken, s.secret_a, s.cp_msg_t, s.jump_key, s.back_to = set(), {}, 0, None, "title"

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
            return it + [(T("levels"), s.open_levels), (T("settings"), s.open_settings), (T("quit"), s.quit)]
        if L == "settings":
            return [(f"{T('lang')}: {lang.LANG_NAMES[lang.cur]}", s.cycle_lang),
                    (f"{T('sound')}: {T('on') if s.audio.on else T('off')}", s.toggle_sound),
                    (f"{T('char')}: {T(s.char)}", s.cycle_char), (T("back"), s.close_settings)]
        if L == "pause":
            it = [(T("resume"), lambda: s.set_state("play")), (T("restart"), s.restart_level)]
            if s.demo: it.append((T("levels"), s.open_levels))
            return it + [(T("settings"), s.open_settings), (T("menu"), s.to_title)]
        return []

    def moved(s):
        m = pygame.mouse.get_pos(); mv = m != s.last_mouse; s.last_mouse = m; return mv

    def draw_menu(s, y0, step=32, h=26):
        s.rects = []; mx, my = s.mouse(); mv = s.moved()
        for i, (label, _) in enumerate(s.items()):
            r = pygame.Rect(W // 2 - 110, y0 + i * step, 220, h); s.rects.append(r)
            if r.collidepoint(mx, my) and mv: s.sel = i
            if i == s.sel:
                pygame.draw.rect(s.scr, (60, 50, 120), r); pygame.draw.rect(s.scr, GOLD, r, 2)
            s.txt(label, (W // 2, y0 + i * step + (h - 16) // 2), GOLD if i == s.sel else WHITE, s.fm, True)

    def activate(s, i):
        its = s.items()
        if 0 <= i < len(its): s.sfx("click"); its[i][1]()

    # ---------- acoes ----------
    def quit(s): pygame.quit(); sys.exit()
    def persist(s): save.write({"done": s.done, "lang": lang.cur, "sound": s.audio.on, "char": s.char, "chosen": s.chosen})
    def to_title(s): s.demo = False; s.sv = save.load(); s.set_state("title")
    def cycle_char(s):
        s.char = CHARS[(CHARS.index(s.char) + 1) % len(CHARS)]; s.chosen = True; s.A.set_char(s.char); s.persist(); s.sfx("click")
    def ask_char(s, then):
        s.after_char, s.csel = then, CHARS.index(s.char); s.set_state("charsel")
    def confirm_char(s):
        s.char, s.chosen = CHARS[s.csel], True; s.A.set_char(s.char); s.persist(); s.sfx("ok")
        then, s.after_char = s.after_char, None
        (then or (lambda: s.set_state("title")))()
    def open_levels(s): s.demo = True; s.set_state("levelsel")
    def start_demo(s, i):
        s.demo = True
        s.ask_char(lambda: s.start_level(i)) if not s.chosen else s.start_level(i)
    def open_settings(s): s.back_to = s.state; s.set_state("settings")
    def close_settings(s): s.persist(); s.sv = save.load(); s.set_state(s.back_to)
    def cycle_lang(s): lang.cur = lang.LANGS[(lang.LANGS.index(lang.cur) + 1) % 3]; s.persist()
    def toggle_sound(s): s.audio.on = not s.audio.on; s.persist(); s.sfx("click")
    def new_game(s):
        s.done, s.page, s.demo = 0, 0, False
        s.ask_char(lambda: s.set_state("story"))
    def continue_game(s):
        s.done, s.demo = s.sv["done"], False
        go = (lambda: s.begin_exam()) if s.done >= 9 else (lambda: s.start_level(s.done))
        s.ask_char(go) if not s.chosen else go()

    def start_level(s, i):
        s.idx, s.lv = i, build(i); s.gate_open, s.quiz, s.qcool, s.qmsg, s.cam = False, False, 0, "", 0.0
        s.reset_actors(); s.spawn, s.cp_hit, s.player, s.dead = s.lv.start, set(), Player(s.lv.start), 0
        s.orbs_taken, s.secret_a, s.cp_msg_t = set(), {}, 0
        s.set_state("intro")

    def reset_actors(s):
        lv = s.lv
        s.enemies = [Enemy(*e) for e in lv.enemies]
        s.movers = [Mover(*m) for m in lv.movers] + [Faller(*f) for f in lv.fallers]

    def restart_level(s):
        s.start_level(s.idx); s.set_state("play")

    def respawn(s):
        s.player = Player(s.spawn); s.reset_actors(); s.qcool = 60

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
                elif st == "settings" and s.sel == 2 and e.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d): s.cycle_char()
                elif e.key == pygame.K_ESCAPE and st == "title": pass
                elif e.key == pygame.K_ESCAPE and st == "pause": s.set_state("play")
                elif e.key == pygame.K_ESCAPE and st == "settings": s.close_settings()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, r in enumerate(s.rects):
                    if r.collidepoint(s.mouse()): s.activate(i)
        elif st == "charsel": s.charsel_event(e)
        elif st == "levelsel": s.levelsel_event(e)
        elif e.type == pygame.KEYDOWN:
            ok = e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
            if e.key == pygame.K_ESCAPE and s.demo and st in ("intro", "clear"): return s.set_state("levelsel")
            if st == "story" and ok:
                s.page += 1; s.sfx("click")
                if s.page > 2: s.start_level(0)
            elif st == "intro" and ok: s.set_state("play")
            elif st == "clear" and ok and s.t > 100:
                if s.demo: s.set_state("levelsel")                       # demonstracao: nada e salvo; volta a selecao
                else: s.start_level(s.idx + 1) if s.idx < 8 else s.set_state("jewel")
            elif st == "jewel" and ok and s.t > 240: s.begin_exam()
            elif st == "end" and ok: s.set_state("title"); s.sv = save.load()
            elif st == "play":
                if s.quiz: s.quiz_key(e.key)
                elif e.key == pygame.K_ESCAPE: s.set_state("pause")
                elif e.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w): s.jump_pressed, s.jump_key = True, e.key
            elif st == "exam": s.exam_key(e.key)

    # ---------- escolha de personagem ----------
    CARD = [pygame.Rect(96, 46, 200, 244), pygame.Rect(344, 46, 200, 244)]
    BACK = pygame.Rect(270, 318, 100, 26)

    def charsel_event(s, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_LEFT, pygame.K_a): s.csel = 0; s.sfx("click")
            elif e.key in (pygame.K_RIGHT, pygame.K_d): s.csel = 1; s.sfx("click")
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE): s.confirm_char()
            elif e.key == pygame.K_ESCAPE: s.after_char = None; s.set_state("levelsel" if s.demo else "title")
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            m = s.mouse()
            if s.BACK.collidepoint(m): s.after_char = None; s.sfx("click"); s.set_state("levelsel" if s.demo else "title")
            for i, r in enumerate(s.CARD):
                if r.collidepoint(m): s.csel = i; s.confirm_char()

    # ---------- selecao de fases (demonstracao) ----------
    def lcard(s, i):
        w, l = divmod(i, 3); return pygame.Rect(14 + w * 208, 46 + l * 90, 204, 84)
    LBACK = pygame.Rect(W - 104, 330, 94, 24)

    def levelsel_event(s, e):
        if e.type == pygame.KEYDOWN:
            k, i = e.key, s.lsel
            if k in (pygame.K_LEFT, pygame.K_a): s.lsel = (i - 3) % 9; s.sfx("click")
            elif k in (pygame.K_RIGHT, pygame.K_d): s.lsel = (i + 3) % 9; s.sfx("click")
            elif k in (pygame.K_UP, pygame.K_w): s.lsel = i // 3 * 3 + (i % 3 - 1) % 3; s.sfx("click")
            elif k in (pygame.K_DOWN, pygame.K_s): s.lsel = i // 3 * 3 + (i % 3 + 1) % 3; s.sfx("click")
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE): s.sfx("click"); s.start_demo(s.lsel)
            elif k == pygame.K_ESCAPE: s.sfx("click"); s.to_title()
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            m = s.mouse()
            if s.LBACK.collidepoint(m): s.sfx("click"); s.to_title()
            for i in range(9):
                if s.lcard(i).collidepoint(m): s.lsel = i; s.sfx("click"); s.start_demo(i)

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
            else: s.A.set_char(s.char); s.set_state("title")
        elif s.state == "play": s.update_play()
        elif s.state == "clear" and s.t == 1: s.sfx("portal")
        elif s.state == "exam" and s.ex["fb"]:
            s.ex["fb"] -= 1
            if not s.ex["fb"]: s.ex["i"] += 1; s.ex["sel"] = 0

    def update_play(s):
        lv, p = s.lv, s.player
        s.qcool = max(0, s.qcool - 1); s.qmsg_t = max(0, getattr(s, "qmsg_t", 0) - 1); s.cp_msg_t = max(0, s.cp_msg_t - 1)
        if s.dead:
            s.dead -= 1
            if not s.dead: s.respawn()
            return
        if s.quiz: return
        for m in s.movers: m.update()
        for e in s.enemies: e.update()
        p.update(lv, s.movers, s.gate_open, pygame.key.get_pressed(), s.jump_pressed, s.jump_key); s.jump_pressed = False
        if p.jumped: s.sfx("jump")
        if p.riding is not None and getattr(p.riding, "kind", "") == "fall": p.riding.touch()
        r = p.rect()
        s.cam += (max(0, min(lv.width - W, p.x + PW / 2 - W / 2)) - s.cam) * 0.12
        if p.y > H + 40 or any(r.colliderect(e.rect()) for e in s.enemies) or \
           any(r.colliderect(pygame.Rect(c * TILE + 4, rr * TILE + 14, TILE - 8, 10)) for c, rr in lv.spikes if abs(c * TILE - r.x) < 60):
            return s.die()
        for i, (cx, cy) in enumerate(lv.cps):                       # checkpoints (varios por fase)
            if i not in s.cp_hit and abs(r.centerx - (cx + 7)) < 26 and abs(r.bottom - cy) < 80:
                s.cp_hit.add(i)
                if cx > s.spawn[0]: s.spawn = (cx, cy); s.sfx("check"); s.cp_msg_t = 90
        for i, (ox, oy) in enumerate(lv.orbs):                      # brindes opcionais
            if i not in s.orbs_taken and r.colliderect(pygame.Rect(ox - 8, oy - 8, 16, 16)): s.orbs_taken.add(i); s.sfx("item")
        for i, g in enumerate(lv.secret):                           # passagens escondidas: revela ao entrar
            if i not in s.secret_a and any(r.colliderect(pygame.Rect(c * TILE, rr * TILE, TILE, TILE)) for c, rr in g): s.secret_a[i] = 255
        for i in s.secret_a: s.secret_a[i] = max(0, s.secret_a[i] - 6)
        if not s.gate_open and s.qcool == 0 and abs(r.centerx - (lv.gate_col * TILE + TILE / 2)) < 44:
            s.quiz, s.qsel, s.qmsg, p.vx = True, 0, "", 0
        if r.colliderect(pygame.Rect(lv.frag[0] - 12, lv.frag[1] - 14, 24, 40)):
            if not s.demo:                                          # demonstracao nao salva nem concede fragmento
                s.done = max(s.done, s.idx + 1); s.persist(); s.sv = save.load()
            s.sfx("item"); s.set_state("clear")

    # ---------- desenho ----------
    def draw_bg(s, w, cam):
        sky, l1, l2 = s.A.bg[w]; s.scr.blit(sky, (0, 0))
        for layer, f in ((l1, .2), (l2, .45)):
            x = -int(cam * f) % W; s.scr.blit(layer, (x - W, 0)); s.scr.blit(layer, (x, 0))

    def draw_forest_bg(s, cam):
        """Ceu, arvores (texturas enviadas): usados SOMENTE nas fases da floresta."""
        F = s.A.forest; S = s.scr; S.fill(F["sky_col"])
        x = -int(cam * 0.05) % F["sky"].get_width(); S.blit(F["sky"], (x - F["sky"].get_width(), 0)); S.blit(F["sky"], (x, 0))
        th = F["trees"].get_height(); S.fill(F["dark"], (0, TREE_Y + th - 1, W, H))
        x = -int(cam * 0.3) % F["trees"].get_width(); S.blit(F["trees"], (x - F["trees"].get_width(), TREE_Y)); S.blit(F["trees"], (x, TREE_Y))

    def forest_tile(s, lv, c, r, x, y):
        F = s.A.forest; g, gw = F["ground"], F["gw"]; sx = (c * TILE) % gw
        if (c, r - 1) not in lv.solid and (c, r - 1) not in lv.cover: s.scr.blit(g, (x, y), (sx, 0, TILE, TILE)); return
        d = 1
        while (c, r - d) in lv.solid and d < 4: d += 1
        if d == 2: s.scr.blit(g, (x, y), (sx, 13, TILE, TILE))
        else:
            s.scr.blit(g, (x, y), (sx, 16, TILE, 12)); s.scr.blit(g, (x, y + 12), (sx, 16, TILE, 12))
            ov = pygame.Surface((TILE, TILE), pygame.SRCALPHA); ov.fill((0, 0, 0, 22 * (d - 2))); s.scr.blit(ov, (x, y))

    def draw_climb(s, kind, x, y, r):
        S, cx, w = s.scr, x + TILE // 2, s.lv.world
        if kind == "vine":
            pygame.draw.rect(S, (22, 64, 30), (cx - 2, y, 4, TILE)); pygame.draw.rect(S, (60, 150, 60), (cx - 1, y, 2, TILE))
            lx = cx + 2 if r % 2 else cx - 8
            pygame.draw.rect(S, (22, 64, 30), (lx - 1, y + 7, 8, 5)); pygame.draw.rect(S, (90, 190, 70), (lx, y + 8, 6, 3))
        elif kind == "rope":
            pygame.draw.rect(S, (90, 60, 30), (cx - 2, y, 4, TILE)); pygame.draw.rect(S, (214, 176, 100), (cx - 1, y, 2, TILE))
            for k in (3, 11, 19): pygame.draw.rect(S, (90, 60, 30), (cx - 3, y + k, 6, 2))
        elif kind == "ladder":
            rail, rung = ((130, 90, 50), (190, 140, 80)) if w == 1 else ((70, 72, 90), (150, 154, 176))
            for rx in (cx - 8, cx + 6): pygame.draw.rect(S, BLACK, (rx - 1, y, 4, TILE)); pygame.draw.rect(S, rail, (rx, y, 2, TILE))
            for k in (4, 12, 20): pygame.draw.rect(S, BLACK, (cx - 8, y + k - 1, 16, 4)); pygame.draw.rect(S, rung, (cx - 8, y + k, 16, 2))
        else:                                                      # wall: muro de tijolos escalavel com apoios
            pygame.draw.rect(S, (70, 52, 62), (x + 2, y, TILE - 4, TILE)); pygame.draw.rect(S, BLACK, (x + 2, y, TILE - 4, TILE), 1)
            for k in (5, 13, 21): pygame.draw.rect(S, (96, 74, 84), (x + 4, y + k - 3, TILE - 8, 1))
            for k, o in ((6, 6), (16, 14)): pygame.draw.rect(S, (240, 210, 120), (x + o, y + k, 5, 3)); pygame.draw.rect(S, BLACK, (x + o, y + k + 3, 5, 1))

    def draw_world(s):
        lv, P, cam, S = s.lv, WORLDS[s.lv.world], int(s.cam), s.scr
        forest = lv.world == 0
        s.draw_forest_bg(cam) if forest else s.draw_bg(lv.world, cam)
        tick = pygame.time.get_ticks()
        for g in lv.secret:                                    # interior escuro dos tuneis
            for c, r in g: pygame.draw.rect(S, (30, 22, 20), (c * TILE - cam, r * TILE, TILE, TILE))
        for c in range(cam // TILE, (cam + W) // TILE + 2):
            for r in range(ROWS):
                k, x, y = (c, r), c * TILE - cam, r * TILE
                if k in lv.climb: s.draw_climb(lv.climb[k], x, y, r)
                if k in lv.solid:
                    if forest: s.forest_tile(lv, c, r, x, y)
                    else:
                        pygame.draw.rect(S, P["tile"], (x, y, TILE, TILE))
                        if (c * 7 + r * 13) % 5 == 0: pygame.draw.rect(S, tuple(v * 3 // 4 for v in P["tile"]), (x + 6, y + 8, 4, 4))
                        if (c, r - 1) not in lv.solid and (c, r - 1) not in lv.cover: pygame.draw.rect(S, P["top"], (x, y, TILE, 7)); pygame.draw.rect(S, BLACK, (x, y + 7, TILE, 1))
                elif k in lv.plat:
                    if forest: S.blit(s.A.forest["ground"], (x, y), ((c * TILE) % s.A.forest["gw"], 0, TILE, 10))
                    else:
                        pygame.draw.rect(S, P["plat"], (x, y, TILE, 10)); pygame.draw.rect(S, BLACK, (x, y, TILE, 10), 1)
                        pygame.draw.rect(S, WHITE, (x + 2, y + 2, TILE - 4, 2))
                if k in lv.spikes:
                    for o in (0, 12): pygame.draw.polygon(S, (210, 210, 220), [(x + o, y + TILE), (x + o + 6, y + 10), (x + o + 12, y + TILE)]); pygame.draw.polygon(S, BLACK, [(x + o, y + TILE), (x + o + 6, y + 10), (x + o + 12, y + TILE)], 1)
                if k in lv.gate and not s.gate_open:
                    pygame.draw.rect(S, (150 + 60 * ((c + r + tick // 120) % 2), 60, 220), (x + 6, y, TILE - 12, TILE))
        # sinal, checkpoints, brindes, fragmento
        sc, sr = lv.sign; sx, sy = sc * TILE - cam, sr * TILE
        pygame.draw.rect(S, (90, 60, 30), (sx + 10, sy - 20, 4, 20)); pygame.draw.rect(S, (240, 220, 140), (sx + 2, sy - 34, 20, 16)); s.txt("i", (sx + 12, sy - 33), BLACK, s.fm, True, False)
        for i, (cx0, cy) in enumerate(lv.cps):
            cx = cx0 + 6 - cam; pygame.draw.rect(S, (230, 230, 230), (cx, cy - 48, 3, 48)); pygame.draw.rect(S, (60, 200, 80) if i in s.cp_hit else (200, 60, 60), (cx + 3, cy - 48, 16, 10))
        for i, (ox, oy) in enumerate(lv.orbs):
            if i not in s.orbs_taken: S.blit(s.A.orb[(tick // 300 + i) % 2], (ox - 6 - cam, oy - 6 + int(math.sin(tick / 300 + i) * 2)))
        fx, fy = lv.frag[0] - cam, lv.frag[1] + int(math.sin(tick / 250) * 3)
        gm = s.A.gems[lv.world]; gl = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(gl, (*WORLDS[lv.world]["gem"], 60 + int(30 * math.sin(tick / 200))), (22, 22), 20); S.blit(gl, (fx - 22, fy - 22))
        S.blit(gm, (fx - gm.get_width() // 2, fy - gm.get_height() // 2))
        for m in s.movers:
            mx, my = int(m.x) - cam, int(m.y)
            if getattr(m, "kind", "") == "fall":
                if m.state == 3: continue
                mx += m.shake(); base = ((120, 80, 45), (214, 170, 100), (110, 106, 122))[lv.world]
                pygame.draw.rect(S, base, (mx, my, m.w, 10)); pygame.draw.rect(S, BLACK, (mx, my, m.w, 10), 1)
                pygame.draw.rect(S, tuple(min(255, v + 40) for v in base), (mx + 2, my + 2, m.w - 4, 2))
                if m.state: 
                    for q in range(mx + 6, mx + m.w - 4, 12): pygame.draw.line(S, BLACK, (q, my + 1), (q + 3, my + 8))
            else:
                pygame.draw.rect(S, (170, 120, 70), (mx, my, m.w, 8)); pygame.draw.rect(S, BLACK, (mx, my, m.w, 8), 1); pygame.draw.rect(S, (230, 190, 130), (mx + 2, my + 2, m.w - 4, 2))
        for e in s.enemies:
            im = (s.A.fly if e.kind == "fly" else s.A.enemy)[lv.world][(e.t // 8 if e.kind == "fly" else e.t // 12) % 2]
            S.blit(im if e.dir > 0 else pygame.transform.flip(im, True, False), (int(e.x) - cam, int(e.y)))
        p = s.player
        if not (s.dead and s.dead % 6 < 3):
            im = (s.A.frames if p.face > 0 else s.A.frames_l)[p.frame()]
            S.blit(im, (int(p.x + PW / 2 - (15 if p.face > 0 else 14)) - cam, int(p.y + PH - 53)))
        for i, g in enumerate(lv.secret):                      # tampa das passagens secretas (some ao entrar)
            a = s.secret_a.get(i, 255)
            if a <= 0: continue
            for c, r in g:
                x, y = c * TILE - cam, r * TILE
                if x < -TILE or x > W: continue
                t = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                if forest:
                    gg = s.A.forest["ground"]; t.blit(gg, (0, 0), (((c * TILE) % s.A.forest["gw"]), 16, TILE, 12)); t.blit(gg, (0, 12), (((c * TILE) % s.A.forest["gw"]), 16, TILE, 12))
                else:
                    t.fill(P["tile"]); pygame.draw.rect(t, tuple(v * 3 // 4 for v in P["tile"]), (6, 8, 4, 4))
                if (c + r) % 4 == 0 and (tick // 700) % 3 == 0: pygame.draw.rect(t, (255, 255, 255), (11, 9, 2, 2))   # brilho discreto: pista
                t.set_alpha(a); S.blit(t, (x, y))

    def draw_hud(s):
        for i in range(9):
            if i < s.done: s.scr.blit(s.A.gems[i // 3], (8 + i * 19, 2))
            else: s.scr.blit(s.A.gem_sil[i // 3], (8 + i * 19, 2))
        s.txt(f"{T('orbs')}: {len(s.orbs_taken)}/{len(s.lv.orbs)}", (8, 30))
        lab = f"{T('w%d' % (s.lv.world + 1))} - {T('level')} {s.idx % 3 + 1}/3"
        s.txt(lab, (W - 8 - s.fs.size(lab)[0], 8))
        if s.demo: s.txt(T("demo_tag"), (W - 8 - s.fs.size(T("demo_tag"))[0], 24), (255, 160, 120))

    def thumb(s, i):
        """Previa do mapa da fase (1 pixel horizontal = ~1 bloco)."""
        if i in s.thumbs: return s.thumbs[i]
        lv = build(i); P = WORLDS[lv.world]; cols = lv.width // TILE; TW, TH = 188, 45
        im = pygame.Surface((TW, TH)); a, b = P["sky"]
        for y in range(TH): t = y / TH; pygame.draw.line(im, tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3)), (0, y), (TW, y))
        for x in range(TW):
            c0 = x * cols // TW; c1 = max(c0, (x + 1) * cols // TW - 1)
            for r in range(ROWS):
                col = None
                for c in range(c0, c1 + 1):
                    k = (c, r)
                    if k in lv.spikes: col = (230, 60, 60)
                    elif k in lv.climb: col = (120, 240, 120)
                    elif k in lv.solid: col = P["top"] if (c, r - 1) not in lv.solid else P["tile"]
                    elif k in lv.plat: col = P["plat"]
                    if col: break
                if col: pygame.draw.rect(im, col, (x, r * 3, 1, 3))
        for (mx, my, *_r) in lv.movers: pygame.draw.rect(im, (255, 170, 60), (int(mx) // TILE * TW // cols, int(my) // TILE * 3, 3, 2))
        for (fx, fy, fw) in lv.fallers: pygame.draw.rect(im, (255, 170, 60), (fx // TILE * TW // cols, fy // TILE * 3, 2, 2))
        for e in lv.enemies: pygame.draw.rect(im, (255, 40, 40), (int(e[0]) // TILE * TW // cols, int(e[1]) // TILE * 3, 2, 2))
        gc = lv.gate_col * TW // cols; pygame.draw.rect(im, (190, 80, 230), (gc, 0, 1, TH))
        for (cx, cy) in lv.cps: pygame.draw.rect(im, WHITE, (cx // TILE * TW // cols, cy // 24 * 3 - 5, 1, 5))
        pygame.draw.rect(im, WORLDS[lv.world]["gem"], (lv.frag[0] // TILE * TW // cols - 1, lv.frag[1] // 24 * 3 - 2, 3, 4))
        pygame.draw.rect(im, BLACK, im.get_rect(), 1); s.thumbs[i] = im; return im

    def star(s, x, y, on):
        pts = [(x + 4 + 4 * math.sin(k * 2 * math.pi / 10) * (1 if k % 2 == 0 else .45), y + 4 - 4 * math.cos(k * 2 * math.pi / 10) * (1 if k % 2 == 0 else .45)) for k in range(10)]
        pygame.draw.polygon(s.scr, GOLD if on else (60, 60, 90), pts)

    def draw_charsel(s):
        S = s.scr; mx, my = s.mouse(); mv = s.moved()
        s.txt(T("choose"), (W // 2, 14), GOLD, s.fm, True)
        for i, r in enumerate(s.CARD):
            if mv and r.collidepoint(mx, my): s.csel = i
            on = i == s.csel; s.panel(tuple(r), 215 if on else 150)
            if not on: pygame.draw.rect(S, (70, 70, 100), r, 2)
            if on: pygame.draw.rect(S, WHITE, r.inflate(-6, -6), 1)
            fr = (s.A.chars[CHARS[i]][0])
            f = fr[1 + s.t // 6 % 6] if on else fr[0]
            im = pygame.transform.scale(f, (FWc * 3, FHc * 3))
            pygame.draw.ellipse(S, (0, 0, 0), (r.centerx - 34, r.y + 186, 68, 12))
            S.blit(im, (r.centerx - im.get_width() // 2, r.y + 30))
            s.txt(T(CHARS[i]), (r.centerx, r.y + 208), GOLD if on else WHITE, s.fm, True)
            s.txt(T("pick") + " (Enter)" if on else "", (r.centerx, r.y + 8), (200, 230, 255), s.fs, True)
        s.txt(T("choose_hint"), (W // 2, 298), (255, 240, 170), s.fs, True)
        pygame.draw.rect(S, (60, 50, 120) if s.BACK.collidepoint(mx, my) else (30, 30, 60), s.BACK); pygame.draw.rect(S, GOLD, s.BACK, 2)
        s.txt(T("back"), (s.BACK.centerx, s.BACK.y + 5), WHITE, s.fm, True)

    def draw_levelsel(s):
        S = s.scr; S.fill((14, 16, 34)); mx, my = s.mouse(); mv = s.moved()
        s.txt(T("levels"), (W // 2, 4), GOLD, s.fm, True)
        for w in range(3): s.txt(T("w%d" % (w + 1)), (14 + w * 208 + 102, 28), WORLDS[w]["gem"], s.fs, True)
        for i in range(9):
            r = s.lcard(i)
            if mv and r.collidepoint(mx, my): s.lsel = i
            on = i == s.lsel
            pygame.draw.rect(S, (60, 50, 120) if on else (26, 28, 56), r); pygame.draw.rect(S, GOLD if on else (90, 90, 140), r, 2)
            S.blit(s.thumb(i), (r.x + 8, r.y + 6))
            s.txt(f"{T('stage')} {i % 3 + 1}", (r.x + 8, r.y + 54), WHITE if on else (200, 200, 220))
            d = DIFFICULTY[i]
            for k in range(5): s.star(r.right - 8 - 5 * 11 + k * 11, r.y + 52, k < d)
            s.txt(T("d%d" % d) + ("  ✓" if False else ""), (r.x + 8, r.y + 68), (255, 220, 150) if on else (170, 170, 200))
            if s.sv["done"] > i: s.txt("* " + T("done_mark"), (r.right - 8 - s.fs.size("* " + T("done_mark"))[0], r.y + 68), (120, 255, 140))
        s.txt(T("sel_hint"), (W // 2, 318), (255, 240, 170), s.fs, True)
        s.txt(T("demo"), (14, 338), (255, 160, 120))
        pygame.draw.rect(S, (60, 50, 120) if s.LBACK.collidepoint(mx, my) else (30, 30, 60), s.LBACK); pygame.draw.rect(S, GOLD, s.LBACK, 2)
        s.txt(T("back"), (s.LBACK.centerx, s.LBACK.y + 5), WHITE, s.fm, True)

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
        if st == "levelsel": return s.draw_levelsel()
        if st in ("title", "settings", "story", "jewel", "end", "exam", "intro", "charsel"):
            s.draw_bg(1 if st in ("jewel", "end") else 0 if st != "exam" else 2, s.t * 0.6)
        if st == "title":
            if s.logo3 is None: s.logo3 = pygame.transform.scale(s.A.logo, (s.A.logo.get_width() * 3, s.A.logo.get_height() * 3))   # 3x inteiro, sem suavizar
            S.blit(s.logo3, (W // 2 - s.logo3.get_width() // 2, 4 + int(math.sin(s.t / 40) * 2)))
            s.txt(T("title"), (W // 2, 142), GOLD, s.fm, True); s.txt(T("sub"), (W // 2, 160), WHITE, s.fs, True)
            s.draw_menu(180, 26, 22); s.txt(f"{T('progress')}: {s.sv['done']}/9", (W // 2, 336), WHITE, s.fs, True)
            S.blit(s.A.frames[0 if s.t % 60 < 30 else 1 + s.t // 6 % 6], (20, 256))
        elif st == "charsel": s.draw_charsel()
        elif st == "settings":
            s.panel((130, 70, 380, 220)); s.txt(T("settings"), (W // 2, 90), GOLD, s.fm, True); s.draw_menu(120)
            S.blit(pygame.transform.scale(s.A.frames[0], (FWc * 2, FHc * 2)), (440, 150))
        elif st == "story":
            s.panel((50, 60, 540, 240)); s.para(T(f"story{s.page + 1}"), 80, 110, 480, WHITE, s.fm, True, 22)
            S.blit(pygame.transform.scale(s.A.frames[0], (58, 108)), (W // 2 - 29, 175)); s.txt(T("enter"), (W // 2, 308), GOLD, s.fs, True)
        elif st == "intro":
            s.panel((70, 70, 500, 220)); w = s.lv.world
            s.txt(T(f"w{w + 1}"), (W // 2, 90), GOLD, s.fm, True); s.txt(f"{T('level')} {s.idx % 3 + 1}/3", (W // 2, 120), WHITE, s.fm, True)
            y = s.para(T("goal"), 90, 155, 460, WHITE, s.fs, True)
            if w == 2: y = s.para(T("fic"), 90, y + 6, 460, (180, 220, 255), s.fs, True)
            if s.idx == 0:
                y = s.para(T("controls"), 90, y + 6, 460, (255, 230, 150), s.fs, True); s.para(T("climb"), 90, y, 460, (255, 230, 150), s.fs, True)
            s.txt(T("enter"), (W // 2, 262), GOLD, s.fs, True)
        elif st in ("play", "pause", "clear"):
            s.draw_world(); s.draw_hud(); lv = s.lv; p = s.player
            if st == "play" and not s.quiz:
                if abs(p.rect().centerx - (lv.sign[0] * TILE + TILE // 2)) < 70:
                    s.panel((40, 34, 560, 60), 215); s.txt(T("know"), (50, 38), GOLD); s.para(lang.content(s.idx)["fact"], 50, 54, 540, WHITE, s.fs, False, 14)
                if s.idx == 0 and s.cam < 500: s.para(T("controls"), 20, H - 30, 600, (255, 240, 170), s.fs, True)
                elif s.idx < 3 and any(abs(c * TILE + 12 - p.rect().centerx) < 90 for (c, rr) in lv.climb): s.para(T("climb"), 20, H - 30, 600, (255, 240, 170), s.fs, True)
                if s.cp_msg_t: s.txt(T("cp"), (W // 2, 80), (140, 255, 160), s.fm, True)
                if s.demo and s.idx == 0 and False: pass
                if s.qmsg_t: s.txt(s.qmsg, (W // 2, 110), (120, 255, 140), s.fm, True)
            if s.dead: ov = pygame.Surface((W, H), pygame.SRCALPHA); ov.fill((200, 0, 0, 60)); S.blit(ov, (0, 0))
            if s.quiz: s.draw_quiz(lang.content(s.idx), s.qsel, s.qmsg)
            if st == "pause":
                s.panel((100, 12, 440, 336), 235); s.txt(T("paused"), (W // 2, 20), GOLD, s.fm, True); s.draw_menu(46, 28, 24)
                y = s.para(T("controls"), 110, 196, 420, (255, 240, 170), s.fs, True); y = s.para(T("climb"), 110, y, 420, (255, 240, 170), s.fs, True)
                s.txt(T("progress"), (W // 2, y + 4), WHITE, s.fs, True)
                for i in range(9): S.blit(s.A.gems[i // 3] if i < s.done else s.A.gem_sil[i // 3], (W // 2 - 85 + i * 19, y + 20))
                s.txt(f"{s.done}/9", (W // 2, y + 48), GOLD, s.fs, True)
            if st == "clear":
                fx, fy = s.lv.frag[0] - int(s.cam), s.lv.frag[1]
                for k in range(8): pygame.draw.circle(S, tuple(int(v) for v in (WORLDS[s.lv.world]["gem"])), (int(fx + math.cos(s.t * .2 + k) * (50 - s.t % 50 * .8)), int(fy + math.sin(s.t * .2 + k) * (50 - s.t % 50 * .8))), 3)
                if s.t > 100:
                    s.panel((90, 100, 460, 120)); s.para(T("demo_clear") if s.demo else T("clear"), 110, 125, 420, WHITE, s.fm, True, 22)
                    s.txt(T("to_levels") + " (Enter)" if s.demo else T("enter"), (W // 2, 190), GOLD, s.fs, True)
        elif st == "jewel":
            n = min(9, s.t // 20 + 1); cx, cy = W // 2, 150; k = min(1, max(0, (s.t - 180) / 60))
            for i in range(n):
                a = s.t * 0.03 + i * 2 * math.pi / 9; rad = 90 * (1 - k)
                g = s.A.gems[i // 3]; S.blit(g, (int(cx + math.cos(a) * rad) - g.get_width() // 2, int(cy + math.sin(a) * rad) - g.get_height() // 2))
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
