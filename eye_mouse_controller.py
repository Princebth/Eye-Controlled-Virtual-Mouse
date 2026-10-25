import cv2
import mediapipe as mp
import pyautogui
import time

class EyeMouseController:
    def __init__(self):
        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)

        # Screen size
        self.screen_w, self.screen_h = pyautogui.size()

        # Smoothing
        self.prev_x, self.prev_y = 0, 0
        self.smoothening = 7

        # Blink detection
        self.blink_threshold = 0.004
        self.last_click_time = 0
        self.click_delay = 0.7

        # Double blink (Right Click)
        self.blink_count = 0
        self.blink_timer = 0

        # Drag feature
        self.dragging = False
        self.blink_start = 0

        # Scroll control
        self.scroll_delay = 0.3
        self.last_scroll_time = 0

        # ✅ NEW: Eye close screenshot
        self.eye_close_start = 0
        self.screenshot_taken = False

        # Camera
        self.cap = cv2.VideoCapture(0)

        # FPS
        self.pTime = 0

    def process_frame(self, frame):
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = self.face_mesh.process(rgb_frame)

        if output.multi_face_landmarks:
            landmarks = output.multi_face_landmarks[0].landmark

            # Iris (cursor control)
            iris = landmarks[474]

            screen_x = self.screen_w * iris.x
            screen_y = self.screen_h * iris.y

            # Smooth movement
            curr_x = self.prev_x + (screen_x - self.prev_x) / self.smoothening
            curr_y = self.prev_y + (screen_y - self.prev_y) / self.smoothening

            pyautogui.moveTo(curr_x, curr_y)
            self.prev_x, self.prev_y = curr_x, curr_y

            current_time = time.time()

            # ===========================
            # SCROLL
            # ===========================
            if iris.y < 0.35:
                if current_time - self.last_scroll_time > self.scroll_delay:
                    pyautogui.scroll(30)
                    self.last_scroll_time = current_time
                    cv2.putText(frame, "SCROLL UP", (50, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            elif iris.y > 0.65:
                if current_time - self.last_scroll_time > self.scroll_delay:
                    pyautogui.scroll(-30)
                    self.last_scroll_time = current_time
                    cv2.putText(frame, "SCROLL DOWN", (50, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            # ===========================
            # BLINK DETECTION
            # ===========================
            top = landmarks[159]
            bottom = landmarks[145]
            blink = abs(top.y - bottom.y)

            # ===========================
            # 🔥 3-SECOND EYE CLOSE → SCREENSHOT
            # ===========================
            if blink < self.blink_threshold:

                # Start timer
                if self.eye_close_start == 0:
                    self.eye_close_start = current_time

                # Countdown display
                elapsed = current_time - self.eye_close_start
                remaining = max(0, 3 - int(elapsed))

                cv2.putText(frame, f"Screenshot in {remaining}s", (50, 220),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                # Take screenshot after 3 sec
                if elapsed > 3 and not self.screenshot_taken:
                    pyautogui.screenshot("eye_screenshot.png")
                    self.screenshot_taken = True

                    cv2.putText(frame, "SCREENSHOT TAKEN", (50, 260),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                # ===========================
                # LEFT CLICK
                # ===========================
                if current_time - self.last_click_time > self.click_delay:
                    pyautogui.click()
                    self.last_click_time = current_time
                    cv2.putText(frame, "CLICK", (50, 120),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # ===========================
                # RIGHT CLICK (DOUBLE BLINK)
                # ===========================
                if current_time - self.blink_timer < 0.5:
                    self.blink_count += 1
                else:
                    self.blink_count = 1

                self.blink_timer = current_time

                if self.blink_count == 2:
                    pyautogui.rightClick()
                    cv2.putText(frame, "RIGHT CLICK", (50, 160),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

                # ===========================
                # DRAG
                # ===========================
                if self.blink_start == 0:
                    self.blink_start = current_time
                elif current_time - self.blink_start > 1:
                    pyautogui.mouseDown()
                    self.dragging = True

            else:
                # Reset
                self.eye_close_start = 0
                self.screenshot_taken = False
                self.blink_start = 0

                if self.dragging:
                    pyautogui.mouseUp()
                    self.dragging = False

            # Draw iris
            x = int(iris.x * w)
            y = int(iris.y * h)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        return frame

    def show_fps(self, frame):
        cTime = time.time()
        fps = 1 / (cTime - self.pTime) if (cTime - self.pTime) != 0 else 0
        self.pTime = cTime

        cv2.putText(frame, f'FPS: {int(fps)}', (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            frame = self.process_frame(frame)
            frame = self.show_fps(frame)

            cv2.imshow("Eye Mouse Control", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    controller = EyeMouseController()
    controller.run()