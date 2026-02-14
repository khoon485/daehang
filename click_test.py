"""
클릭 방식 테스트 스크립트
- 5초 대기 후 현재 마우스 위치에서 클릭
- 여러 방식을 시도해서 어떤 게 게임에서 먹히는지 확인
"""
import ctypes
import ctypes.wintypes
import time
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# 상수
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001

# 구조체 정의
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("_input", _INPUT),
    ]

def get_cursor_pos():
    pt = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def method1_sendinput_click():
    """방법1: SendInput - 표준 방식"""
    print("[방법1] SendInput 표준 클릭")

    down = INPUT()
    down.type = INPUT_MOUSE
    down._input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
    down._input.mi.time = 0
    down._input.mi.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))

    up = INPUT()
    up.type = INPUT_MOUSE
    up._input.mi.dwFlags = MOUSEEVENTF_LEFTUP
    up._input.mi.time = 0
    up._input.mi.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))

    user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(INPUT))
    time.sleep(0.05)
    user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(INPUT))

def method2_mouse_event():
    """방법2: mouse_event - 레거시 API"""
    print("[방법2] mouse_event 레거시 클릭")
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def method3_sendinput_with_move():
    """방법3: SendInput으로 먼저 이동 후 클릭 (절대좌표)"""
    print("[방법3] SendInput 절대좌표 이동 + 클릭")

    x, y = get_cursor_pos()
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    abs_x = int(x * 65535 / screen_w)
    abs_y = int(y * 65535 / screen_h)

    # 먼저 이동
    move = INPUT()
    move.type = INPUT_MOUSE
    move._input.mi.dx = abs_x
    move._input.mi.dy = abs_y
    move._input.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
    move._input.mi.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
    user32.SendInput(1, ctypes.byref(move), ctypes.sizeof(INPUT))

    time.sleep(0.1)

    # 클릭
    down = INPUT()
    down.type = INPUT_MOUSE
    down._input.mi.dx = abs_x
    down._input.mi.dy = abs_y
    down._input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_ABSOLUTE
    down._input.mi.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))

    up = INPUT()
    up.type = INPUT_MOUSE
    up._input.mi.dx = abs_x
    up._input.mi.dy = abs_y
    up._input.mi.dwFlags = MOUSEEVENTF_LEFTUP | MOUSEEVENTF_ABSOLUTE
    up._input.mi.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))

    user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(INPUT))
    time.sleep(0.05)
    user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(INPUT))

def method4_postmessage():
    """방법4: PostMessage - 윈도우 메시지 직접 전송"""
    print("[방법4] PostMessage 윈도우 메시지")

    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    MK_LBUTTON = 0x0001

    hwnd = user32.GetForegroundWindow()
    x, y = get_cursor_pos()

    # 클라이언트 좌표로 변환
    pt = ctypes.wintypes.POINT(x, y)
    user32.ScreenToClient(hwnd, ctypes.byref(pt))

    lparam = pt.y << 16 | (pt.x & 0xFFFF)

    user32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
    time.sleep(0.05)
    user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lparam)


methods = {
    '1': method1_sendinput_click,
    '2': method2_mouse_event,
    '3': method3_sendinput_with_move,
    '4': method4_postmessage,
}

if __name__ == "__main__":
    print("=" * 50)
    print("대항해시대 온라인 클릭 테스트")
    print("=" * 50)
    print()
    print("방법 선택:")
    print("1: SendInput 표준")
    print("2: mouse_event 레거시")
    print("3: SendInput 절대좌표 이동+클릭")
    print("4: PostMessage 윈도우 메시지")
    print()

    choice = input("번호 입력 (1-4): ").strip()
    if choice not in methods:
        print("잘못된 선택")
        sys.exit(1)

    print()
    print("5초 후 현재 마우스 위치에 클릭합니다!")
    print("게임 상품(소시지 등) 위에 마우스를 올려놓으세요!")
    print()

    for i in range(5, 0, -1):
        pos = get_cursor_pos()
        print(f"  {i}초... (마우스 위치: {pos[0]}, {pos[1]})")
        time.sleep(1)

    print()
    methods[choice]()
    print("클릭 완료! 계산기 팝업이 떴는지 확인하세요.")
