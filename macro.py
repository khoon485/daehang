"""
대항해시대 온라인 - 회계 랭작 자동화 매크로
mouse_event 방식 사용 (게임에서 인식됨 확인)

흐름:
1. 구입 버튼 클릭
2. 소시지 클릭 → 계산기 팝업
3. 수량 1 + OK
4. 확인 (구매)
5. 깎기 버튼 체크
   - 활성화 → 깎기 → 성공여부 색상 확인 → 판매
   - 비활성화 → 재교섭 요청서 → 깎기 → 성공여부 확인 → 판매
6. 반복

Home = 시작/일시정지
End = 긴급 종료
"""
import requests
import ctypes
import ctypes.wintypes
import json
import time
import random
import os
import sys
from PIL import ImageGrab

user32 = ctypes.windll.user32

# DPI 스케일링 대응
try:
    user32.SetProcessDPIAware()
except:
    pass

# 키 코드
VK_HOME = 0x24   # 시작/일시정지
VK_END = 0x23    # 긴급 종료

# 마우스 이벤트 상수
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000


class GameMacro:
    def __init__(self):
        self.config = self.load_config()
        self.running = False
        self.paused = False
        self.cycle_count = 0
        self.total_points = 0
        self.telegram_token = "8116431880:AAHEMjJD6AUh1Hssi2xd8WaezcXwOoHqJ4I"
        self.chat_id = "7372837243"

    def send_telegram(self, message):
        """텔레그램으로 알림 보내기"""
        import requests
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": f"🚢 [피터의 대항해시대]\n{message}"
        }
        try:
            # 5초 안에 응답 없으면 넘어가도록 timeout 설정
            requests.post(url, data=payload, timeout=5)
        except Exception as e:
            print(f"[❌] 텔레그램 발송 실패: {e}")

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if not os.path.exists(config_path):
            print("ERROR: config.json이 없습니다!")
            print("먼저 python capture_coords.py 를 실행해서 좌표를 캡처하세요.")
            sys.exit(1)
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_coord(self, name):
        """config에서 좌표 가져오기"""
        c = self.config["coords"][name]
        return c["x"], c["y"]

    def get_pixel_color(self, x, y):
        """스크린샷 방식으로 픽셀 색상 가져오기 (DirectX 게임도 가능)"""
        img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
        r, g, b = img.getpixel((0, 0))
        return r, g, b

    def color_distance(self, c1, c2):
        """두 색상간 거리 (유클리드)"""
        return ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2) ** 0.5

    def move_mouse(self, x, y):
        """마우스를 특정 좌표로 이동 (mouse_event 절대좌표)"""
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        abs_x = int(x * 65535 / screen_w)
        abs_y = int(y * 65535 / screen_h)
        user32.mouse_event(
            MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
            abs_x, abs_y, 0, 0
        )

    def click(self, x, y, delay_after=0.3):
        """mouse_event로 클릭 (게임에서 인식되는 방식)"""
        # 랜덤 오프셋 (사람처럼)
        rx = x + random.randint(-2, 2)
        ry = y + random.randint(-2, 2)

        # 먼저 이동
        self.move_mouse(rx, ry)
        time.sleep(random.uniform(0.05, 0.1))

        # 클릭
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(random.uniform(0.03, 0.06))
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        # 딜레이
        time.sleep(delay_after + random.uniform(0, 0.15))

    def double_click(self, x, y, delay_after=0.3):
        """mouse_event로 더블클릭"""
        rx = x + random.randint(-2, 2)
        ry = y + random.randint(-2, 2)
        self.move_mouse(rx, ry)
        time.sleep(random.uniform(0.05, 0.1))

        # 첫번째 클릭
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(random.uniform(0.03, 0.05))
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(random.uniform(0.05, 0.1))
        # 두번째 클릭
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(random.uniform(0.03, 0.05))
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        time.sleep(delay_after + random.uniform(0, 0.15))

    def press_key(self, vk_code, delay_after=0.2):
        """키보드 키 입력 (keybd_event)"""
        user32.keybd_event(vk_code, 0, 0, 0)  # key down
        time.sleep(random.uniform(0.03, 0.06))
        user32.keybd_event(vk_code, 0, 0x0002, 0)  # key up (KEYEVENTF_KEYUP)
        time.sleep(delay_after + random.uniform(0, 0.1))

    def type_text(self, text, delay_after=0.2):
        """문자열 타이핑 (한 글자씩)"""
        for ch in text:
            vk = ord(ch.upper())
            self.press_key(vk, delay_after=random.uniform(0.05, 0.1))
        time.sleep(delay_after)

    def wait_random(self, base=0.3, variance=0.15):
        """사람처럼 랜덤 대기"""
        time.sleep(base + random.uniform(0, variance))

    def is_key_pressed(self, vk):
        return user32.GetAsyncKeyState(vk) & 0x8000

    def check_hotkeys(self):
        """핫키 체크 - F11 토글, F12 종료"""
        if self.is_key_pressed(VK_END):
            print("\n[End] 긴급 종료!")
            self.running = False
            return False
        if self.is_key_pressed(VK_HOME):
            self.paused = not self.paused
            state = "일시정지" if self.paused else "재개"
            print(f"\n[Home] {state}")
            time.sleep(0.3)
            while self.paused:
                if self.is_key_pressed(VK_HOME):
                    self.paused = False
                    print("[Home] 재개")
                    time.sleep(0.3)
                    break
                if self.is_key_pressed(VK_END):
                    print("\n[End] 긴급 종료!")
                    self.running = False
                    return False
                time.sleep(0.05)
        return True

    def is_haggle_active(self):
        """깎기 버튼이 활성화 상태인지 색상으로 판단"""
        hx, hy = self.get_coord("haggle_button")
        current = self.get_pixel_color(hx, hy)

        active_ref = self.config["colors"].get("haggle_active_color")
        inactive_ref = self.config["colors"].get("haggle_inactive_color")

        if active_ref and inactive_ref:
            active_c = (active_ref["r"], active_ref["g"], active_ref["b"])
            inactive_c = (inactive_ref["r"], inactive_ref["g"], inactive_ref["b"])
            dist_active = self.color_distance(current, active_c)
            dist_inactive = self.color_distance(current, inactive_c)
            return dist_active < dist_inactive
        else:
            # 색상 데이터 없으면 일단 활성화로 간주
            return True

    def grab_price_region(self):
        """가격 영역 스크린샷 캡처"""
        region = self.config["regions"]["price_area"]
        img = ImageGrab.grab(bbox=(
            region["x1"], region["y1"],
            region["x2"], region["y2"]
        ))
        return img

    def images_are_same(self, img1, img2, threshold=5):
        """두 이미지가 같은지 비교 (픽셀 단위)
        threshold: 허용 오차 (픽셀당 RGB 차이)
        Returns: True=같음(깎기 실패), False=다름(깎기 성공)
        """
        if img1.size != img2.size:
            return False

        pixels1 = list(img1.getdata())
        pixels2 = list(img2.getdata())

        diff_count = 0
        total = len(pixels1)

        for p1, p2 in zip(pixels1, pixels2):
            # RGB 차이 계산
            diff = abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]) + abs(p1[2]-p2[2])
            if diff > threshold:
                diff_count += 1

        diff_ratio = diff_count / total if total > 0 else 0
        return diff_ratio < 0.05  # 5% 미만 변화면 같은 이미지로 판단

    def check_haggle_result(self, before_img):
        """깎기 성공/실패 여부를 가격 이미지 비교로 판단
        before_img: 깎기 전 가격 영역 스크린샷
        Returns: True=성공(가격 변함), False=실패(가격 안 변함)
        """
        # 깎기 결과 반영될 때까지 대기 (약 0.9초 + 여유)
        time.sleep(1.2)

        # 깎기 후 가격 영역 캡처
        after_img = self.grab_price_region()

        # 비교
        same = self.images_are_same(before_img, after_img)
        is_success = not same  # 이미지가 다르면 = 가격이 변함 = 성공

        print(f"    깎기 결과: {'성공 (가격 변동!)' if is_success else '실패 (가격 동일)'}")
        return is_success

    def do_buy(self):
        """구매 사이클: 구입버튼 → 소시지 → 키보드 1 + Enter → 깎기 단계로"""
        print(f"  [1] 구입 버튼 클릭")
        self.click(*self.get_coord("buy_button"), delay_after=0.8)
        if not self.check_hotkeys():
            return False

        print(f"  [2] 소시지 클릭")
        self.click(*self.get_coord("item_sausage"), delay_after=0.8)
        if not self.check_hotkeys():
            return False

        print(f"  [3] 키보드 1 입력")
        self.press_key(0x31, delay_after=0.3)  # '1' 키
        if not self.check_hotkeys():
            return False

        print(f"  [4] Enter → 깎기 단계로")
        self.press_key(0x0D, delay_after=0.8)  # Enter 키
        if not self.check_hotkeys():
            return False

        return True

    def do_haggle(self):
        """깎기 사이클"""
        print(f"  [5] 깎기 체크")

        if self.is_haggle_active():
            print(f"    깎기 활성화 상태")
        else:
            print(f"    깎기 비활성화 → 재교섭 요청서 사용")
            self.click(*self.get_coord("renegotiate_box"), delay_after=0.5)
            if not self.check_hotkeys(): return False
            time.sleep(0.9)
            self.double_click(*self.get_coord("renegotiate_item"), delay_after=0.8)
            if not self.check_hotkeys(): return False

            # 활성화 대기 로직...
            # (생략)

        haggle_attempt = 0
        consecutive_fails = 0
        renegotiate_count = 0
        while True:
            haggle_attempt += 1
            # [추가] 10번 넘게 시도해도 안 되면 문제가 생긴 것임
            if renegotiate_count > 10:
                self.send_telegram("주인님 재교섭 로직에 문제가 생겼어요...")
                print(f"\n[🚨 경고] 재교섭 1회 초과! 로직 꼬임 방지를 위해 강제 리셋합니다.")
                # ESC 키를 눌러서 열려있는 창(거래창, 아이템창 등)을 닫음
                self.press_key(0x1B, delay_after=1.0) # 0x1B = ESC 키
                self.press_key(0x1B, delay_after=1.0) # 0x1B = ESC 키
                return True  # 실패를 리턴하여 이번 사이클 종료
            before_img = self.grab_price_region()

            print(f"  [6] 깎기 클릭 (시도 #{haggle_attempt})")
            self.click(*self.get_coord("haggle_button"), delay_after=0.5)
            if not self.check_hotkeys(): return False

            success = self.check_haggle_result(before_img)
            if success:
                print(f"  [7] 깎기 성공 → 확인")
                self.click(*self.get_coord("sell_confirm"), delay_after=0.8)
                if not self.check_hotkeys(): return False
                
                # 중요: 성공했으므로 루프를 나갑니다.
                break 

            else:
                consecutive_fails += 1
                renegotiate_count += 1
                print(f"    깎기 실패 (연속 {consecutive_fails}회)")
                if consecutive_fails > 3:
                    print(f"    재교섭 요청서 사용")
                    self.click(*self.get_coord("renegotiate_box"), delay_after=0.5)
                    if not self.check_hotkeys(): return False
                    self.double_click(*self.get_coord("renegotiate_item"), delay_after=0.8)
                    if not self.check_hotkeys(): return False
                    
                    # 중요: 재교섭을 썼으므로 실패 카운트를 초기화합니다.
                    consecutive_fails = 0 
                    time.sleep(1.0)
        
        # ==========================================
        # 이 부분이 없어서 종료되었던 것입니다!
        return True 
        # ==========================================
    def do_eat(self):
        """밥 먹기 로직: 퀵슬롯 클릭 후 4번 키 11회 입력"""
        print(f"\n[🍴] 밥 먹기 타임! (사이클 {self.cycle_count})")
        
        # 1. 퀵슬롯 클릭 (좌표가 config에 있어야 함)
        # 만약 좌표가 없다면 get_coord 대신 직접 입력하거나 추가하세요.
        self.press_key(0x34, delay_after=0.8)  # 0xC0는 '`'의 가상 키 코드
        if not self.check_hotkeys(): return False

        # 2. '4' 키 11번 누르기
        for i in range(11):
            print(f"    - 밥 먹는 중... ({i+1}/11)")
            self.press_key(0x34, delay_after=0.2)  # 0x34는 숫자 '4'의 가상 키 코드
            if not self.check_hotkeys(): return False
            
        print("[✔] 식사 완료. 다시 랭작을 시작합니다.")
        time.sleep(0.5)
        return True
    

    def run_cycle(self):
        """1회 거래 사이클"""
        self.cycle_count += 1
        self.total_points = self.cycle_count * 16
        # ==========================================
        # 115회마다 밥 먹기 체크
        if self.cycle_count % 105 == 0:
            if not self.do_eat():
                return False
        # ==========================================
        print(f"\n{'='*50}")
        print(f"  사이클 #{self.cycle_count} | 누적 {self.total_points} 포인트")
        print(f"{'='*50}")

        if not self.do_buy():
            return False

        if not self.do_haggle():
            return False

        # 거래 완료 후 대기 (거래창 닫히는 시간)
        self.wait_random(0.5, 0.2)

        return True


    def run(self):
        print("=" * 60)
        print("   대항해시대 온라인 - 회계 랭작 매크로")
        print("=" * 60)
        print("\n   Home = 시작/일시정지")
        print("   End = 긴급 종료\n")
        print("   Home을 눌러 시작...")

        # [1] 시작 대기 루프
        start_pressed = False
        while not start_pressed:
            if self.is_key_pressed(VK_HOME):
                print("\n   🚀 매크로 시작!")
                self.send_telegram("🚀 매크로 가동 시작!")
                start_pressed = True # 이 조건을 만족하면 while문을 빠져나감
                time.sleep(0.5)
            
            if self.is_key_pressed(VK_END):
                print("\n   종료")
                return # 이건 진짜 끝내는 거니까 return이 맞음
            time.sleep(0.05)

        # [2] 메인 실행 루프
        self.running = True
        while self.running:
            # 매 사이클 시작 전에 핫키(일시정지/종료)를 체크
            # check_hotkeys() 함수 내부에 정훈님이 짠 일시정지 로직이 들어가 있어야 합니다.
            if not self.check_hotkeys():
                break

            # 실제 거래 한 바퀴 실행
            if not self.run_cycle():
                # 만약 run_cycle이 False를 리턴하면(깎기 15회 초과 등)
                # 바로 끝내지 말고 잠시 쉬었다가 다음 사이클 시도
                print("   [!] 사이클 리셋... 3초 후 재시작")
                time.sleep(3)
                continue

        # [3] 종료 후 결과 보고
        print(f"\n{'='*60}")
        print(f"   종료!")
        print(f"   총 {self.cycle_count}회 거래")
        print(f"   총 {self.total_points} 포인트 획득 (추정)")
        print(f"{'='*60}")
        self.send_telegram(f"🏁 매크로 종료\n총 {self.cycle_count}회 완료")


if __name__ == "__main__":
    macro = GameMacro()
    macro.run()
