#!/usr/bin/env python3
"""news-image-20261124: one image summing up the world's news of
Tuesday 24 November 2026, drawn in pure Python (standard library only).

The program renders a newspaper front page -- masthead, date band, lead
story (Ukraine peace talks in Stockholm), four secondary stories (Iran,
Venezuela, Indonesia factory fire, COP31) and a bottom strip (Himalayan
flood) -- with a small built-in 5x7 bitmap font, and writes it as a PNG
to $MAKEFUN_OUTPUT_DIR/entry.png (default /output). No network, no wall
clock, no randomness: two runs produce byte-identical output.
"""

import math
import os
import struct
import zlib

W, H = 960, 960

PAPER = (248, 244, 233)
INK = (22, 22, 22)
WHITE = (255, 253, 245)
SKY = (220, 233, 245)
UKR_BLUE = (43, 108, 176)
UKR_YELLOW = (246, 196, 69)
US_RED = (178, 34, 52)
US_BLUE = (60, 59, 110)
SEA = (30, 90, 138)
STEEL = (107, 114, 128)
TABLE = (139, 94, 60)
TABLE_DARK = (110, 72, 44)
FIRE = (232, 89, 12)
FIRE_DARK = (201, 42, 42)
LEAF = (47, 158, 68)
MOUNTAIN = (90, 101, 117)
WATER = (25, 113, 194)
SLATE = (122, 147, 168)

# 5x7 bitmap font: each glyph is 7 rows of 5 bits ("1" = ink).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "(": ("00011", "00100", "01000", "01000", "01000", "00100", "00011"),
    ")": ("11000", "00100", "00010", "00010", "00010", "00100", "11000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10010", "01000", "10101", "10010", "01101"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=3):
        for k in range(360):
            a = math.radians(k)
            for rr in range(r - t + 1, r + 1):
                self.set(int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)), c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        ys = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        for y in range(ay, cy + 1):
            if y < by:
                xa = ax + (bx - ax) * (y - ay) / max(1, by - ay)
                xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
            else:
                xa = bx + (cx - bx) * (y - by) / max(1, cy - by)
                xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
            lo, hi = sorted((int(xa), int(xb)))
            self.rect(lo, y, hi - lo + 1, 1, c)

    # --- text ---------------------------------------------------------
    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale if s else 0

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale

    def text_center(self, y, s, scale, c):
        self.text((self.w - self.text_w(s, scale)) // 2, y, s, scale, c)

    def wrap(self, s, scale, maxw):
        lines, cur = [], ""
        for word in s.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def png_bytes(self):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * self.w * 3:(y + 1) * self.w * 3]

        def chunk(tag, data):
            out = struct.pack(">I", len(data)) + tag + data
            return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


def draw_panel(cv, x, y, w, h, strip, headline, body):
    cv.rect(x, y, w, h, WHITE)
    cv.frame(x, y, w, h, INK, 2)
    cv.rect(x, y, w, 8, strip)
    tx = x + 138
    tw = w - 138 - 14
    lines = cv.wrap(headline, 3, tw)
    yy = y + 16
    for ln in lines:
        cv.text(tx, yy, ln, 3, INK)
        yy += 24
    yy += 4
    for ln in cv.wrap(body, 2, tw):
        if yy + 14 > y + h - 8:
            break
        cv.text(tx, yy, ln, 2, INK)
        yy += 16


def draw_carrier(cv, x, y):
    # Aircraft carrier on the sea.
    cv.rect(x, y + 70, 110, 40, SEA)
    cv.rect(x, y + 70, 110, 3, (255, 255, 255))
    cv.triangle(x + 8, y + 96, x + 102, y + 96, x + 88, y + 74, STEEL)
    cv.triangle(x + 8, y + 96, x + 88, y + 74, x + 24, y + 74, (140, 148, 160))
    cv.rect(x + 58, y + 52, 18, 22, STEEL)
    cv.rect(x + 62, y + 44, 4, 8, STEEL)
    cv.line(x + 14, y + 104, x + 46, y + 104, WHITE)
    cv.line(x + 60, y + 107, x + 96, y + 107, WHITE)


def draw_boat(cv, x, y):
    # Small boat on the Caribbean sea, red burst above it.
    cv.rect(x, y + 70, 110, 40, SEA)
    cv.rect(x, y + 70, 110, 3, (255, 255, 255))
    cv.triangle(x + 28, y + 92, x + 82, y + 92, x + 72, y + 76, (60, 60, 60))
    cv.triangle(x + 28, y + 92, x + 72, y + 76, x + 38, y + 76, (110, 110, 110))
    cv.line(x + 55, y + 76, x + 55, y + 52, (60, 60, 60))
    cx, cy = x + 84, y + 34
    for k in range(8):
        a = math.radians(k * 45)
        cv.line(cx, cy, int(cx + 16 * math.cos(a)),
                int(cy + 16 * math.sin(a)), FIRE_DARK)
    cv.disc(cx, cy, 6, FIRE)


def draw_factory(cv, x, y):
    # Factory with flames.
    cv.rect(x + 8, y + 66, 44, 44, (120, 120, 120))
    cv.rect(x + 56, y + 52, 48, 58, (150, 150, 150))
    cv.rect(x + 84, y + 22, 12, 34, (100, 100, 100))
    cv.triangle(x + 16, y + 66, x + 28, y + 66, x + 22, y + 44, FIRE)
    cv.triangle(x + 34, y + 66, x + 48, y + 66, x + 41, y + 40, FIRE_DARK)
    cv.triangle(x + 64, y + 52, x + 78, y + 52, x + 71, y + 32, FIRE)
    cv.rect(x + 16, y + 80, 10, 10, (60, 60, 60))
    cv.rect(x + 34, y + 80, 10, 10, (60, 60, 60))
    cv.rect(x + 64, y + 66, 10, 10, (60, 60, 60))


def draw_globe(cv, x, y):
    # Green globe for the climate talks.
    cx, cy, r = x + 55, y + 55, 48
    cv.disc(cx, cy, r, LEAF)
    cv.ring(cx, cy, r, (20, 90, 40), 3)
    cv.line(cx - 44, cy - 18, cx + 44, cy - 18, (180, 240, 190))
    cv.line(cx - 48, cy + 16, cx + 48, cy + 16, (180, 240, 190))
    cv.line(cx, cy - 48, cx, cy + 48, (180, 240, 190))
    cv.disc(cx - 20, cy - 26, 9, (90, 200, 110))
    cv.disc(cx + 22, cy + 24, 11, (90, 200, 110))


def draw_mountains(cv, x, y, w, h):
    # Himalayan peaks above flood water.
    base = y + h
    cv.triangle(x + 6, base, x + 66, base, x + 36, y + 8, MOUNTAIN)
    cv.triangle(x + 56, base, x + 126, base, x + 91, y + 2, (70, 80, 95))
    cv.triangle(x + 116, base, x + 176, base, x + 146, y + 12, MOUNTAIN)
    cv.triangle(x + 28, y + 22, x + 44, y + 22, x + 36, y + 8, WHITE)
    cv.triangle(x + 83, y + 16, x + 99, y + 16, x + 91, y + 2, WHITE)
    cv.rect(x, base - 14, w, 14, WATER)
    cv.line(x + 8, base - 8, x + 40, base - 8, WHITE)
    cv.line(x + 60, base - 5, x + 110, base - 5, WHITE)
    cv.line(x + 130, base - 8, x + 168, base - 8, WHITE)


def draw_lead_scene(cv, x, y, w, h):
    """Summit scene: skyline, peace symbol, Ukraine and US flags, table."""
    cv.rect(x, y, w, h, SKY)
    cv.frame(x, y, w, h, INK, 2)
    # Stockholm skyline.
    for bx, bw, bh in ((8, 60, 58), (78, 44, 80), (132, 70, 46),
                       (212, 52, 70), (274, 64, 52), (700, 56, 66),
                       (766, 70, 44), (846, 52, 74)):
        cv.rect(x + bx, y + h - 52 - bh, bw, bh, SLATE)
    # Peace symbol in the middle.
    cx, cy, r = x + w // 2, y + 82, 52
    cv.disc(cx, cy, r, WHITE)
    cv.ring(cx, cy, r, INK, 4)
    cv.line(cx, cy - r, cx, cy + r, INK)
    cv.line(cx, cy, cx - int(r * 0.72), cy + int(r * 0.72), INK)
    cv.line(cx, cy, cx + int(r * 0.72), cy + int(r * 0.72), INK)
    # Ukraine flag (left) and US flag (right).
    fx, fy, fw, fh = x + 96, y + 30, 110, 66
    cv.rect(fx, fy, 6, 148, INK)
    cv.rect(fx + 6, fy, fw, fh // 2, UKR_BLUE)
    cv.rect(fx + 6, fy + fh // 2, fw, fh - fh // 2, UKR_YELLOW)
    cv.frame(fx + 6, fy, fw, fh, INK, 2)
    fx = x + w - 96 - 116
    cv.rect(fx, fy, 6, 148, INK)
    stripe_h = [10, 9, 10, 9, 10, 9, 9]
    yy = fy
    for i, sh in enumerate(stripe_h):
        cv.rect(fx + 6, yy, fw, sh, US_RED if i % 2 == 0 else WHITE)
        yy += sh
    cv.rect(fx + 6, fy, 46, 36, US_BLUE)
    for dx in (8, 20, 32):
        for dy in (9, 21):
            cv.disc(fx + 6 + dx, fy + dy, 2, WHITE)
    cv.frame(fx + 6, fy, fw, fh, INK, 2)
    # Summit table with microphones (kept clear of the peace symbol
    # in the middle and of the two flags).
    cv.rect(x, y + h - 52, w, 52, TABLE)
    cv.rect(x, y + h - 52, w, 6, TABLE_DARK)
    for mx in (x + 260, x + 612):
        for dx in (-1, 0, 1):
            cv.line(mx + dx, y + h - 52, mx + dx, y + h - 86, INK)
        cv.disc(mx, y + h - 92, 9, INK)


def draw():
    cv = Canvas(W, H, PAPER)
    cv.frame(8, 8, W - 16, H - 16, INK, 3)
    cv.frame(18, 18, W - 36, H - 36, INK, 1)

    # Masthead.
    cv.text_center(30, "THE WORLD TODAY", 6, INK)
    cv.rect(24, 82, W - 48, 42, INK)
    cv.text_center(90, "TUESDAY, 24 NOVEMBER 2026", 4, WHITE)

    # Lead story.
    lx, ly, lw, lh = 24, 140, W - 48, 350
    cv.rect(lx, ly, lw, lh, WHITE)
    cv.frame(lx, ly, lw, lh, INK, 2)
    cv.text(lx + 20, ly + 12, "UKRAINE PEACE TALKS", 5, INK)
    cv.text(lx + 20, ly + 56, "TRUMP'S 28-POINT PLAN CHALLENGED IN STOCKHOLM", 3, INK)
    cv.text(lx + 20, ly + 82, "ZELENSKY ADDRESSES CRIMEA PLATFORM SUMMIT", 3, INK)
    draw_lead_scene(cv, lx + 20, ly + 114, lw - 40, 198)
    cv.text(lx + 20, ly + 322, "EUROPEAN LEADERS GATHER AS TALKS GO ON", 2, INK)

    # Divider.
    cv.rect(24, 506, W - 48, 2, INK)

    # Four secondary stories.
    panels = [
        (24, 520, US_RED, "TRUMP WARNS IRAN",
         "VERY TRAUMATIC OUTCOME IF NUCLEAR DEAL FAILS. "
         "SECOND US CARRIER WEIGHED FOR THE MIDDLE EAST.", draw_carrier),
        (484, 520, SEA, "US NAMES CARTEL DE LOS SOLES A TERROR GROUP",
         "21 STRIKES ON DRUG BOATS SINCE SEPTEMBER. 83 KILLED.",
         draw_boat),
        (24, 694, FIRE, "FACTORY FIRE IN INDONESIA",
         "WORKERS MISSING AS RESCUE GOES ON.", draw_factory),
        (484, 694, LEAF, "COP31 TALKS STALL",
         "FOSSIL FUELS AND FINANCE DIVIDE NATIONS IN TURKIYE.",
         draw_globe),
    ]
    for px, py, strip, head, body, icon in panels:
        draw_panel(cv, px, py, 436, 158, strip, head, body)
        icon(cv, px + 14, py + 30)

    # Bottom strip: Himalayan flood.
    bx, by, bw, bh = 24, 866, W - 48, 68
    cv.rect(bx, by, bw, bh, WHITE)
    cv.frame(bx, by, bw, bh, INK, 2)
    cv.text(bx + 20, by + 8, "HIMALAYAN FLOOD: 4 DEAD,", 3, INK)
    cv.text(bx + 20, by + 34, "ABOUT 100 MISSING", 3, INK)
    draw_mountains(cv, bx + bw - 196, by + 4, 176, 60)

    return cv.png_bytes()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = draw()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
