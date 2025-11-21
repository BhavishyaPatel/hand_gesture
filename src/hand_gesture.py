import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
import screen_brightness_control as sbc

wCam, hCam = 480, 360
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()

frame_margin = 60
smoothening = 3
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0

pinch_threshold = 28
cooldown = 0.35
last_time = 0

brightness_last_y = None
brightness_last_time = 0
brightness_cooldown = 0.3

scroll_last_y = None
scroll_last_time = 0
scroll_cooldown = 0.25

print("FINAL Gesture Control System Running... Press Q to Quit")

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    scroll_mode = False

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:

            lm = hand.landmark

            def xy(id):
                return int(lm[id].x * wCam), int(lm[id].y * hCam)

            tx, ty = xy(4)
            ix, iy = xy(8)
            mx, my = xy(12)
            rx, ry = xy(16)
            lx, ly = xy(20)

            for x, y in [(tx,ty), (ix,iy), (mx,my), (rx,ry), (lx,ly)]:
                cv2.circle(frame, (x, y), 7, (255,255,0), cv2.FILLED)

            index_down  = lm[8].y > lm[6].y
            middle_down = lm[12].y > lm[10].y
            ring_down   = lm[16].y > lm[14].y
            little_down = lm[20].y > lm[18].y
            thumb_down_fist = lm[4].x < lm[3].x

            if index_down and middle_down and ring_down and little_down and thumb_down_fist:

                scroll_mode = True

                cv2.putText(frame, "SCROLL MODE", (10, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)

                hand_center_y = int(lm[9].y * hCam)

                if scroll_last_y is not None:
                    dy = hand_center_y - scroll_last_y
                    now = time.time()

                    if abs(dy) > 12 and now - scroll_last_time > scroll_cooldown:
                        if dy < 0:
                            pyautogui.scroll(400)
                            cv2.putText(frame, "SCROLL UP", (10, 240),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                        else:
                            pyautogui.scroll(-400)
                            cv2.putText(frame, "SCROLL DOWN", (10, 240),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                        scroll_last_time = now

                scroll_last_y = hand_center_y

            else:
                scroll_last_y = None

            if not scroll_mode:
                finger_x, finger_y = ix, iy

                finger_x = np.clip(finger_x, frame_margin, wCam - frame_margin)
                finger_y = np.clip(finger_y, frame_margin, hCam - frame_margin)

                target_x = np.interp(finger_x, (frame_margin, wCam - frame_margin), (0, screen_w))
                target_y = np.interp(finger_y, (frame_margin, hCam - frame_margin), (0, screen_h))

                curr_x = prev_x + (target_x - prev_x) / smoothening
                curr_y = prev_y + (target_y - prev_y) / smoothening

                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y

            if not scroll_mode:
                dist_index  = math.hypot(ix - tx, iy - ty)
                dist_middle = math.hypot(mx - tx, my - ty)
                dist_ring   = math.hypot(rx - tx, ry - ty)
                dist_little = math.hypot(lx - tx, ly - ty)

                now = time.time()

                if dist_index < pinch_threshold:
                    if now - last_time > cooldown:
                        pyautogui.click()
                        last_time = now
                        cv2.putText(frame, "CLICK", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                elif dist_middle < pinch_threshold:
                    if now - last_time > cooldown:
                        pyautogui.press("volumeup")
                        last_time = now
                        cv2.putText(frame, "VOLUME UP", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                elif dist_ring < pinch_threshold:
                    if now - last_time > cooldown:
                        pyautogui.press("volumedown")
                        last_time = now
                        cv2.putText(frame, "VOLUME DOWN", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                elif dist_little < pinch_threshold:
                    if now - last_time > cooldown:
                        pyautogui.press("volumemute")
                        last_time = now
                        cv2.putText(frame, "MUTE", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

            if not scroll_mode:
                index_up  = lm[8].y < lm[6].y
                middle_up = lm[12].y < lm[10].y
                ring_up   = lm[16].y < lm[14].y
                little_up = lm[20].y < lm[18].y
                thumb_down = lm[4].x > lm[3].x

                if index_up and middle_up and ring_up and little_up and thumb_down:

                    cv2.putText(frame, "BRIGHTNESS MODE", (10, 110),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

                    hand_center_y = int(lm[9].y * hCam)

                    if brightness_last_y is not None:
                        dy = hand_center_y - brightness_last_y
                        now = time.time()

                        if abs(dy) > 10 and now - brightness_last_time > brightness_cooldown:
                            current_brightness = sbc.get_brightness()[0]

                            if dy < 0:
                                sbc.set_brightness(min(current_brightness + 10, 100))
                                cv2.putText(frame, "BRIGHTNESS +", (10, 150),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                            else:
                                sbc.set_brightness(max(current_brightness - 10, 0))
                                cv2.putText(frame, "BRIGHTNESS -", (10, 150),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                            brightness_last_time = now

                    brightness_last_y = hand_center_y

                else:
                    brightness_last_y = None

            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("FINAL Gesture Control System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()