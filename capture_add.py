"""
기존 config.json에서 특정 좌표만 재캡처
F10 = 캡처, ESC = 건너뛰기
"""
import ctypes
import ctypes.wintypes
import json
import time
import os
from PIL import ImageGrab

user32 = ctypes.windll.user32
try:
    user32.SetProcessDPIAware()
except:
    pass

VK_F10 = 0x79
VK_ESCAPE = 0x1B

def get_cursor_pos():
    pt = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def get_pixel_color(x, y):
    img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
    r, g, b = img.getpixel((0, 0))
    return r, g, b

config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 수정할 좌표 목록
items = list(config["coords"].items())

print("=" * 50)
print("  좌표 재캡처 (F10=캡처, ESC=건너뛰기)")
print("=" * 50)
print()

for i, (key, val) in enumerate(items):
    desc = val.get("desc", key)
    print(f"  [{i+1}/{len(items)}] {desc}")
    print(f"    현재값: ({val['x']}, {val['y']})")
    print(f"    F10=재캡처 / ESC=건너뛰기")

    while True:
        if user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
            print("    건너뜀")
            time.sleep(0.3)
            break
        if user32.GetAsyncKeyState(VK_F10) & 0x8000:
            x, y = get_cursor_pos()
            r, g, b = get_pixel_color(x, y)
            config["coords"][key] = {
                "x": x, "y": y,
                "color_sample": {"r": r, "g": g, "b": b},
                "desc": desc
            }
            print(f"    ✓ 변경: ({x}, {y}) 색상: RGB({r},{g},{b})")
            time.sleep(0.3)
            break
        time.sleep(0.01)
    print()

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
print("저장 완료!")
