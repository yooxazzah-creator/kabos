import os
import sys
import random
import pygame

import numpy as np

try:
    import cv2
except Exception:
    cv2 = None


WINDOW_W = 1000
WINDOW_H = 650
FPS = 60

INTRO_VIDEO = "game_Intro.mp4"
EXIT_IMAGE = "game_exit.png"

BACKGROUND_IMAGES = [
    "bg_1.jpg",
    "bg_2.jpg",
    "bg_3.jpg",
    "bg_4.jpg",
    "bg_5.jpg",
    "bg_6.jpg",
    "bg_7.jpg",
    "bg_8.jpg",
    "bg_9.jpg",
]

STAGES = ["Easy", "Medium", "Hard"]
QUESTIONS_PER_STAGE = 3
ATTEMPTS_PER_QUESTION = 2
CHOICES_PER_QUESTION = 4

MSG_WIN = "Finally you are out. You can exit from the school."
MSG_LOSE = "Game Over"


def file_exists(path: str) -> bool:
    try:
        return os.path.isfile(path)
    except Exception:
        return False


def draw_text_left(surface, text, font, color, x, y):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_text_center(surface, text, font, color, cx, cy):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(cx, cy))
    surface.blit(img, rect)


def wrap_lines(text: str, font, max_width: int) -> list[str]:
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if cur == "" else (cur + " " + w)
        if font.size(trial)[0] <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def play_video_in_window(
    screen,
    clock,
    video_path: str,
    skip_button_rect: pygame.Rect,
    font_small,
    bg,
    stroke,
    fg,
    muted,
) -> bool:
    if cv2 is None:
        return False
    if not file_exists(video_path):
        return False

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps is None or fps <= 1:
        fps = 25.0
    frame_delay_ms = int(1000.0 / float(fps))

    last_tick = pygame.time.get_ticks()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit(0)

            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    cap.release()
                    return True

            if e.type == pygame.MOUSEBUTTONDOWN:
                if skip_button_rect.collidepoint(e.pos):
                    cap.release()
                    return True

        now_tick = pygame.time.get_ticks()
        if now_tick - last_tick < frame_delay_ms:
            clock.tick(FPS)
            continue
        last_tick = now_tick

        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]

        surf = pygame.surfarray.make_surface(np.transpose(frame, (1, 0, 2)))

        scale = min(WINDOW_W / float(w), WINDOW_H / float(h))
        new_w = int(w * scale)
        new_h = int(h * scale)
        surf = pygame.transform.smoothscale(surf, (new_w, new_h))

        screen.fill(bg)
        x = (WINDOW_W - new_w) // 2
        y = (WINDOW_H - new_h) // 2
        screen.blit(surf, (x, y))

        pygame.draw.rect(screen, (30, 34, 44), skip_button_rect, border_radius=12)
        pygame.draw.rect(screen, stroke, skip_button_rect, width=2, border_radius=12)
        label = font_small.render("Skip", True, fg)
        lr = label.get_rect(center=skip_button_rect.center)
        screen.blit(label, lr)

        hint = "Press Esc, Space, or Enter to skip"
        draw_text_left(screen, hint, font_small, muted, 14, WINDOW_H - 28)

        pygame.display.flip()
        clock.tick(FPS)

    cap.release()
    return True


def rand_int(a: int, b: int) -> int:
    return random.randint(a, b)


def shuffle_list(xs):
    random.shuffle(xs)
    return xs


def unique_choices(correct: int) -> list[int]:
    vals = {correct}
    while len(vals) < CHOICES_PER_QUESTION:
        delta = rand_int(-8, 8)
        if delta == 0:
            continue
        cand = correct + delta
        if cand < 0:
            continue
        vals.add(cand)
    out = list(vals)
    shuffle_list(out)
    return out


def build_question(stage: str, prompt: str, correct: int) -> dict:
    return {
        "stage": stage,
        "prompt": prompt,
        "correct": int(correct),
        "choices": unique_choices(int(correct)),
        "attempts_left": ATTEMPTS_PER_QUESTION,
    }


def make_easy() -> dict:
    a = rand_int(1, 20)
    b = rand_int(1, 20)
    add = rand_int(0, 1) == 0
    if (not add) and (b > a):
        a, b = b, a
    correct = a + b if add else a - b
    prompt = f"{a} + {b} = ?" if add else f"{a} - {b} = ?"
    return build_question("Easy", prompt, correct)


def make_medium() -> dict:
    mult = rand_int(0, 1) == 0
    if mult:
        a = rand_int(2, 12)
        b = rand_int(2, 12)
        correct = a * b
        prompt = f"{a} × {b} = ?"
        return build_question("Medium", prompt, correct)

    d = rand_int(2, 12)
    q = rand_int(2, 12)
    dividend = d * q
    correct = q
    prompt = f"{dividend} ÷ {d} = ?"
    return build_question("Medium", prompt, correct)


def make_hard() -> dict:
    t = rand_int(1, 3)

    if t == 1:
        c = rand_int(2, 9)
        val = rand_int(30, 120)
        target = val - (val % c)
        a = rand_int(5, max(6, target - 5))
        b = target - a
        correct = target // c
        prompt = f"({a} + {b}) ÷ {c} = ?"
        return build_question("Hard", prompt, correct)

    if t == 2:
        a = rand_int(5, 16)
        b = rand_int(10, 28)
        c = rand_int(2, 10)
        if c >= b:
            c = 2
        correct = a * (b - c)
        prompt = f"{a} × ({b} - {c}) = ?"
        return build_question("Hard", prompt, correct)

    x = rand_int(5, 50)
    y = rand_int(2, 12)
    z = rand_int(2, 12)
    correct = x + (y * z)
    prompt = f"{x} + {y} × {z} = ?"
    return build_question("Hard", prompt, correct)


def next_question(stage: str) -> dict:
    if stage == "Easy":
        return make_easy()
    if stage == "Medium":
        return make_medium()
    return make_hard()


class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.enabled = True

    def hit(self, pos) -> bool:
        return self.enabled and self.rect.collidepoint(pos)

    def draw(self, surface, font, fill, stroke, text_color):
        r = self.rect
        fill2 = fill if self.enabled else (55, 55, 55)
        pygame.draw.rect(surface, fill2, r, border_radius=14)
        pygame.draw.rect(surface, stroke, r, width=2, border_radius=14)
        img = font.render(self.label, True, text_color)
        ir = img.get_rect(center=r.center)
        surface.blit(img, ir)


def draw_background(screen, bg_fallback, backgrounds, question_index, font_mid, badc):
    if backgrounds:
        bg_img = backgrounds[(question_index - 1) % len(backgrounds)]
        iw, ih = bg_img.get_size()
        scale = max(WINDOW_W / iw, WINDOW_H / ih)
        nw = int(iw * scale)
        nh = int(ih * scale)
        bg_scaled = pygame.transform.smoothscale(bg_img, (nw, nh))
        screen.blit(bg_scaled, ((WINDOW_W - nw) // 2, (WINDOW_H - nh) // 2))
    else:
        screen.fill(bg_fallback)
        draw_text_center(screen, "No background images loaded", font_mid, badc, WINDOW_W // 2, WINDOW_H // 2)


def main():
    pygame.init()
    pygame.display.set_caption("Kabos")
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont(None, 52)
    font_mid = pygame.font.SysFont(None, 32)
    font_small = pygame.font.SysFont(None, 22)

    bg = (11, 15, 22)
    panel = (18, 26, 38)
    stroke = (70, 90, 115)
    fg = (232, 238, 247)
    muted = (166, 179, 197)
    accent = (78, 161, 255)
    okc = (97, 212, 122)
    badc = (255, 92, 92)

    exit_img = None
    if file_exists(EXIT_IMAGE):
        try:
            exit_img = pygame.image.load(EXIT_IMAGE).convert()
        except Exception:
            exit_img = None

    backgrounds = []
    for name in BACKGROUND_IMAGES:
        if file_exists(name):
            try:
                backgrounds.append(pygame.image.load(name).convert())
            except Exception:
                pass

    screen_name = "intro"

    stage_index = 0
    solved = 0
    question = None
    question_index = 0

    toast_text = ""
    toast_color = fg
    toast_until = 0.0

    intro_played = False

    btn_skip_intro = Button((WINDOW_W - 170, 18, 140, 44), "Skip")
    btn_start = Button((WINDOW_W // 2 - 140, 500, 280, 62), "Start")
    btn_start_room = Button((WINDOW_W // 2 - 160, 500, 320, 62), "Start room")
    btn_try_again = Button((WINDOW_W // 2 - 160, 520, 320, 62), "Start again")

    choice_buttons = []
    y0 = 280
    for i in range(4):
        choice_buttons.append(Button((WINDOW_W // 2 - 260, y0 + i * 70, 520, 56), ""))

    running = True
    while running:
        now = pygame.time.get_ticks() / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

            if e.type == pygame.MOUSEBUTTONDOWN:
                pos = e.pos

                if screen_name == "intro":
                    if btn_skip_intro.hit(pos):
                        screen_name = "instructions"
                        intro_played = True

                elif screen_name == "instructions":
                    if btn_start.hit(pos):
                        screen_name = "hub"

                elif screen_name == "hub":
                    if btn_start_room.hit(pos):
                        stage = STAGES[stage_index]
                        question = next_question(stage)
                        question_index += 1
                        screen_name = "question"

                elif screen_name == "question":
                    if question is not None:
                        for i, b in enumerate(choice_buttons):
                            if b.hit(pos):
                                chosen = question["choices"][i]
                                if chosen == question["correct"]:
                                    toast_text = "Correct"
                                    toast_color = okc
                                    toast_until = now + 0.7
                                    solved += 1

                                    if solved >= QUESTIONS_PER_STAGE:
                                        stage_index += 1
                                        solved = 0
                                        question = None
                                        if stage_index >= len(STAGES):
                                            screen_name = "end_win"
                                        else:
                                            screen_name = "hub"
                                    else:
                                        stage = STAGES[stage_index]
                                        question = next_question(stage)
                                        question_index += 1
                                else:
                                    question["attempts_left"] -= 1
                                    if question["attempts_left"] > 0:
                                        toast_text = "Wrong. Try again"
                                        toast_color = badc
                                        toast_until = now + 0.9
                                    else:
                                        screen_name = "end_lose"
                                break

                elif screen_name in ("end_win", "end_lose"):
                    if btn_try_again.hit(pos):
                        stage_index = 0
                        solved = 0
                        question = None
                        question_index = 0
                        toast_text = ""
                        intro_played = False
                        screen_name = "intro"

        if screen_name != "question":
            screen.fill(bg)

        if screen_name == "intro":
            if (not intro_played) and file_exists(INTRO_VIDEO) and (cv2 is not None):
                play_video_in_window(screen, clock, INTRO_VIDEO, btn_skip_intro.rect, font_small, bg, stroke, fg, muted)
                intro_played = True
                screen_name = "instructions"
                continue

            draw_text_center(screen, "Kabos", font_big, fg, WINDOW_W // 2, 110)

            panel_rect = pygame.Rect(WINDOW_W // 2 - 420, 170, 840, 240)
            pygame.draw.rect(screen, panel, panel_rect, border_radius=18)
            pygame.draw.rect(screen, stroke, panel_rect, width=2, border_radius=18)

            draw_text_left(screen, "Intro video", font_mid, fg, panel_rect.x + 22, panel_rect.y + 22)

            if not file_exists(INTRO_VIDEO):
                draw_text_left(screen, "Intro file missing", font_mid, badc, panel_rect.x + 22, panel_rect.y + 75)
                draw_text_left(screen, f"Add: {INTRO_VIDEO}", font_small, muted, panel_rect.x + 22, panel_rect.y + 112)
            elif cv2 is None:
                draw_text_left(screen, "OpenCV missing", font_mid, badc, panel_rect.x + 22, panel_rect.y + 75)
                draw_text_left(screen, "Install: pip install opencv-python-headless numpy", font_small, muted, panel_rect.x + 22, panel_rect.y + 112)
            else:
                draw_text_left(screen, "Video should start automatically", font_small, muted, panel_rect.x + 22, panel_rect.y + 78)

            draw_text_left(screen, "Press Skip to continue", font_small, muted, panel_rect.x + 22, panel_rect.y + 160)
            btn_skip_intro.draw(screen, font_small, (30, 34, 44), stroke, fg)

        elif screen_name == "instructions":
            draw_text_center(screen, "Instructions", font_big, fg, WINDOW_W // 2, 90)

            panel_rect = pygame.Rect(WINDOW_W // 2 - 420, 150, 840, 300)
            pygame.draw.rect(screen, panel, panel_rect, border_radius=18)
            pygame.draw.rect(screen, stroke, panel_rect, width=2, border_radius=18)

            lines = [
                "Escape three rooms: Easy, Medium, Hard.",
                "Each room has three math questions.",
                "Each question has two attempts.",
                "Answers are multiple choice.",
                "Three correct answers unlock next room.",
                "Finish Hard room to exit the school.",
            ]

            y = panel_rect.y + 26
            for s in lines:
                draw_text_left(screen, s, font_mid, fg, panel_rect.x + 24, y)
                y += 42

            btn_start.draw(screen, font_mid, (25, 45, 75), accent, fg)

        elif screen_name == "hub":
            stage = STAGES[stage_index]
            draw_text_center(screen, "Room", font_big, fg, WINDOW_W // 2, 90)

            panel_rect = pygame.Rect(WINDOW_W // 2 - 420, 160, 840, 260)
            pygame.draw.rect(screen, panel, panel_rect, border_radius=18)
            pygame.draw.rect(screen, stroke, panel_rect, width=2, border_radius=18)

            draw_text_left(screen, f"Stage: {stage}", font_mid, fg, panel_rect.x + 24, panel_rect.y + 40)
            draw_text_left(screen, f"Solved: {solved}/{QUESTIONS_PER_STAGE}", font_mid, fg, panel_rect.x + 24, panel_rect.y + 92)
            draw_text_left(screen, "Goal: solve three questions", font_small, muted, panel_rect.x + 24, panel_rect.y + 150)

            btn_start_room.draw(screen, font_mid, (25, 45, 75), accent, fg)

        elif screen_name == "question":
            stage = STAGES[stage_index]
            if question is None:
                question = next_question(stage)
                question_index += 1

            draw_background(screen, bg, backgrounds, question_index, font_mid, badc)

            top_rect = pygame.Rect(0, 0, WINDOW_W, 56)
            pygame.draw.rect(screen, (10, 14, 20), top_rect)
            pygame.draw.line(screen, stroke, (0, 56), (WINDOW_W, 56), 2)

            left = f"Stage: {stage}    Solved: {solved}/{QUESTIONS_PER_STAGE}"
            right = f"Attempts left: {question['attempts_left']}"
            draw_text_left(screen, left, font_small, (200, 210, 225), 14, 18)
            img = font_small.render(right, True, (200, 210, 225))
            screen.blit(img, (WINDOW_W - img.get_width() - 14, 18))

            panel_rect = pygame.Rect(WINDOW_W // 2 - 360, 90, 720, 160)
            pygame.draw.rect(screen, panel, panel_rect, border_radius=18)
            pygame.draw.rect(screen, stroke, panel_rect, width=2, border_radius=18)

            draw_text_left(screen, "Solve to escape", font_small, muted, panel_rect.x + 22, panel_rect.y + 18)

            q_lines = wrap_lines(question["prompt"], font_big, panel_rect.w - 44)
            py = panel_rect.y + 60
            for s in q_lines[:2]:
                draw_text_left(screen, s, font_big, fg, panel_rect.x + 22, py)
                py += 52

            for i in range(4):
                choice_buttons[i].label = str(question["choices"][i])
                choice_buttons[i].draw(screen, font_mid, (24, 30, 40), stroke, fg)

            if toast_text and now <= toast_until:
                draw_text_center(screen, toast_text, font_mid, toast_color, WINDOW_W // 2, WINDOW_H - 30)
            if toast_text and now > toast_until:
                toast_text = ""

        elif screen_name == "end_win":
            draw_text_center(screen, "Escaped", font_big, fg, WINDOW_W // 2, 90)

            panel_rect = pygame.Rect(WINDOW_W // 2 - 420, 150, 840, 380)
            pygame.draw.rect(screen, panel, panel_rect, border_radius=18)
            pygame.draw.rect(screen, stroke, panel_rect, width=2, border_radius=18)

            if exit_img is not None:
                img_w, img_h = exit_img.get_size()
                max_w = panel_rect.w - 6
                max_h = panel_rect.h - 110
                scale = min(max_w / float(img_w), max_h / float(img_h))
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)
                img = pygame.transform.smoothscale(exit_img, (new_w, new_h))
                img_x = panel_rect.x + (panel_rect.w - new_w) // 2
                img_y = panel_rect.y + 6
                screen.blit(img, (img_x, img_y))

            text_area_w = panel_rect.w - 48
            lines = wrap_lines(MSG_WIN, font_mid, text_area_w)
            y = panel_rect.y + panel_rect.h - 92
            for s in lines:
                draw_text_left(screen, s, font_mid, fg, panel_rect.x + 24, y)
                y += 34

            btn_try_again.draw(screen, font_mid, (25, 45, 75), accent, fg)

        elif screen_name == "end_lose":
            draw_text_center(screen, MSG_LOSE, font_big, badc, WINDOW_W // 2, 160)

            panel_rect = pygame.Rect(WINDOW_W // 2 - 420, 230, 840, 210)
            pygame.draw.rect(screen, panel, panel_rect, border_radius=18)
            pygame.draw.rect(screen, stroke, panel_rect, width=2, border_radius=18)

            draw_text_center(screen, "You used all attempts on a question", font_mid, fg, WINDOW_W // 2, 310)
            draw_text_center(screen, "Press Start again to restart", font_mid, fg, WINDOW_W // 2, 350)

            btn_try_again.draw(screen, font_mid, (25, 45, 75), accent, fg)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()