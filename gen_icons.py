#!/usr/bin/env python3
"""앱 아이콘(PNG) 생성기 — 헤더의 앰버 경고 스트라이프 테마.
의존성 없이 raw PNG를 직접 인코딩한다."""
import struct, zlib, math

BG    = (19, 19, 13)     # #13130d
PANEL = (28, 28, 20)     # #1c1c14
AMBER = (214, 163, 40)   # #d6a328
DARK  = (17, 17, 11)     # #11110b
TEXTC = (236, 231, 216)  # #ece7d8


def make_png(n, path, maskable=False):
    pad = int(n * 0.10) if maskable else 0  # 마스커블: 안전영역 확보
    cx, cy = n / 2.0, n / 2.0
    rows = bytearray()
    band_half = n * 0.20
    stripe_w = max(1, int(n * 0.075))
    # 둥근 사각 패널 반경(마스커블이 아니면 살짝 둥글게)
    radius = n * 0.16
    inner = pad
    for y in range(n):
        rows.append(0)  # filter type 0
        for x in range(n):
            # 기본 배경
            r, g, b = BG
            # 둥근 사각형 패널 영역 판정
            in_panel = True
            if not maskable:
                rx = min(x - inner, (n - 1 - inner) - x)
                ry = min(y - inner, (n - 1 - inner) - y)
                # 모서리 둥글게
                if rx < radius and ry < radius:
                    dx = radius - rx
                    dy = radius - ry
                    if dx * dx + dy * dy > radius * radius:
                        in_panel = False
            if in_panel:
                r, g, b = PANEL
                # 경고 스트라이프 밴드 (좌하 -> 우상 대각선)
                v = x + y
                if abs(v - n) < band_half:
                    u = x - y
                    if (u // stripe_w) % 2 == 0:
                        r, g, b = AMBER
                    else:
                        r, g, b = DARK
            rows.extend((r, g, b))
    raw = bytes(rows)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", n, n, 8, 2, 0, 0, 0)  # 8bit, color type 2 (RGB)
    idat = zlib.compress(raw, 9)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote", path, len(png), "bytes")


if __name__ == "__main__":
    make_png(192, "icons/icon-192.png")
    make_png(512, "icons/icon-512.png")
    make_png(512, "icons/icon-maskable-512.png", maskable=True)
    make_png(180, "icons/apple-touch-icon.png")
