"""
색상 읽기 테스트 - 게임 화면에서 색상이 제대로 읽히는지 확인
마우스 위치의 색상을 실시간으로 표시
F12로 종료
"""
import ctypes
import ctypes.wintypes
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32
VK_F12 = 0x7B

# DPI 스케일링 대응
try:
    user32.SetProcessDPIAware()
except:
    pass

def get_cursor_pos():
    pt = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def get_pixel_color_screenshot(x, y):
    """스크린샷 방식으로 픽셀 색상 가져오기 (DirectX 게임도 가능)"""
    # 해당 좌표 주변 1x1 캡처
    img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
    r, g, b = img.getpixel((0, 0))
    return r, g, b

print("색상 읽기 테스트 (스크린샷 방식)")
print("마우스를 게임 화면 위에 올려보세요")
print("F12 = 종료")
print()

while True:
    if user32.GetAsyncKeyState(VK_F12) & 0x8000:
        print("\n종료")
        break

    x, y = get_cursor_pos()
    try:
        r, g, b = get_pixel_color_screenshot(x, y)
        print(f"\r  위치: ({x:4d}, {y:4d})  색상: RGB({r:3d}, {g:3d}, {b:3d})  ", end="", flush=True)
    except Exception as e:
        print(f"\r  위치: ({x:4d}, {y:4d})  에러: {e}  ", end="", flush=True)

    time.sleep(0.1)
