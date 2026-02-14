"""
좌표 캡처 도구
- 게임 각 버튼의 좌표를 하나씩 캡처해서 config.json에 저장
- F10으로 현재 마우스 위치 캡처, ESC로 종료
"""
import ctypes
import ctypes.wintypes
import json
import time
import os
from PIL import ImageGrab

user32 = ctypes.windll.user32

# DPI 스케일링 대응
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
    """스크린샷 방식으로 픽셀 색상 가져오기 (DirectX 게임도 가능)"""
    img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
    r, g, b = img.getpixel((0, 0))
    return r, g, b

def is_key_pressed(vk):
    return user32.GetAsyncKeyState(vk) & 0x8000

# 클릭 좌표 캡처 목록
POINTS_TO_CAPTURE = [
    ("buy_button", "구입 버튼 (교역소주인 옆 '구입' 버튼)"),
    ("item_sausage", "소시지 상품 클릭 위치"),
    ("calc_1", "계산기 숫자 '1' 버튼"),
    ("calc_ok", "계산기 'OK' 버튼"),
    ("haggle_button", "깎기 버튼"),
    ("renegotiate_box", "재교섭 요청서 사용 버튼 (작은 박스)"),
    ("renegotiate_item", "아이템 사용 창에서 재교섭 요청서 아이콘 위치"),
    ("sell_confirm", "확인 버튼 (최종 확인/판매)"),
]

# 영역(박스) 캡처 - 두 점(좌상단, 우하단) 필요
REGIONS_TO_CAPTURE = [
    ("price_area", "가격 숫자 영역 (깎기 성공/실패 판단용)"),
    ("haggle_button_area", "깎기 버튼 영역 (활성화/비활성화 판단용 - 버튼 주변 박스)"),
]

# 색상 캡처 - 깎기 버튼 활성화/비활성화
COLOR_CAPTURES = [
    ("haggle_active_color", "깎기 버튼 활성화 상태 색상 (활성화된 깎기 버튼 위에서 F10)"),
    ("haggle_inactive_color", "깎기 버튼 비활성화 상태 색상 (비활성화된 깎기 버튼 위에서 F10)"),
]

def capture_point(config, key, desc):
    """한 점 캡처"""
    existing = config["coords"].get(key)
    if existing:
        print(f"    기존값: ({existing['x']}, {existing['y']})")
    print(f"    마우스를 해당 위치로 이동 후 F10을 누르세요 (ESC=종료)")

    while True:
        if is_key_pressed(VK_ESCAPE):
            return False
        if is_key_pressed(VK_F10):
            x, y = get_cursor_pos()
            r, g, b = get_pixel_color(x, y)
            config["coords"][key] = {
                "x": x, "y": y,
                "color_sample": {"r": r, "g": g, "b": b},
                "desc": desc
            }
            print(f"    ✓ 캡처: ({x}, {y}) 색상: RGB({r},{g},{b})")
            time.sleep(0.3)
            return True
        time.sleep(0.01)

def main():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")

    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

    if "coords" not in config:
        config["coords"] = {}
    if "regions" not in config:
        config["regions"] = {}
    if "colors" not in config:
        config["colors"] = {}

    print("=" * 60)
    print("  대항해시대 온라인 - 좌표 캡처 도구")
    print("=" * 60)
    print()
    print("  F10 = 현재 마우스 위치 캡처")
    print("  ESC = 종료 (저장됨)")
    print()
    print("  게임 창을 고정 위치에 놓고 시작하세요!")
    print()

    # === 1. 버튼 좌표 캡처 ===
    print("-" * 40)
    print("  [파트1] 버튼 좌표 캡처")
    print("-" * 40)
    for i, (key, desc) in enumerate(POINTS_TO_CAPTURE):
        print(f"\n  [{i+1}/{len(POINTS_TO_CAPTURE)}] {desc}")
        if not capture_point(config, key, desc):
            break
    print()

    # === 2. 가격 영역 박스 캡처 ===
    print("-" * 40)
    print("  [파트2] 가격 숫자 영역 캡처 (두 점)")
    print("-" * 40)
    print()
    for key, desc in REGIONS_TO_CAPTURE:
        print(f"  {desc}")
        existing = config["regions"].get(key)
        if existing:
            print(f"    기존값: ({existing['x1']},{existing['y1']}) ~ ({existing['x2']},{existing['y2']})")

        # 좌상단
        print(f"    [좌상단] 가격 숫자의 왼쪽 위 모서리에 마우스 → F10")
        x1, y1 = None, None
        while True:
            if is_key_pressed(VK_ESCAPE):
                break
            if is_key_pressed(VK_F10):
                x1, y1 = get_cursor_pos()
                print(f"    ✓ 좌상단: ({x1}, {y1})")
                time.sleep(0.3)
                break
            time.sleep(0.01)

        if x1 is None:
            break

        # 우하단
        print(f"    [우하단] 가격 숫자의 오른쪽 아래 모서리에 마우스 → F10")
        while True:
            if is_key_pressed(VK_ESCAPE):
                x1 = None
                break
            if is_key_pressed(VK_F10):
                x2, y2 = get_cursor_pos()
                config["regions"][key] = {
                    "x1": x1, "y1": y1,
                    "x2": x2, "y2": y2,
                    "desc": desc
                }
                w = x2 - x1
                h = y2 - y1
                print(f"    ✓ 우하단: ({x2}, {y2})  →  영역: {w}x{h}px")
                time.sleep(0.3)
                break
            time.sleep(0.01)
    print()

    # === 3. 깎기 버튼 색상 캡처 ===
    print("-" * 40)
    print("  [파트3] 깎기 버튼 활성화/비활성화 색상")
    print("-" * 40)
    print()
    for key, desc in COLOR_CAPTURES:
        existing = config["colors"].get(key)
        print(f"  {desc}")
        if existing:
            print(f"    기존값: RGB({existing['r']},{existing['g']},{existing['b']})")
        print(f"    해당 상태에서 F10 / ESC=건너뛰기")

        while True:
            if is_key_pressed(VK_ESCAPE):
                print("    건너뜀")
                time.sleep(0.3)
                break
            if is_key_pressed(VK_F10):
                x, y = get_cursor_pos()
                r, g, b = get_pixel_color(x, y)
                config["colors"][key] = {"r": r, "g": g, "b": b, "x": x, "y": y}
                print(f"    ✓ 색상: RGB({r},{g},{b}) at ({x},{y})")
                time.sleep(0.3)
                break
            time.sleep(0.01)
        print()

    # 저장
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"설정 저장 완료: {config_path}")
    print()
    print("다음 단계: python macro.py 로 매크로 실행")

if __name__ == "__main__":
    main()
