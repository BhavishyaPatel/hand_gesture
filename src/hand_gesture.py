import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
import os
import screen_brightness_control as sbc
import tkinter as tk

wCam, hCam = 480, 360
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()

frame_margin = 60
smoothening = 3
prev_x, prev_y = 0, 0

pinch_threshold = 28
cooldown = 0.35
last_time = 0

brightness_last_y = None
brightness_last_time = 0
brightness_cooldown = 0.3

scroll_last_y = None
scroll_last_time = 0
scroll_cooldown = 0.25

lock_start_time = None
lock_duration = 3

popup = tk.Tk()
popup.title("Warning")
popup.attributes("-topmost", True)
popup.withdraw()

popup_label = tk.Label(
    popup,
    text="",
    font=("Arial", 22, "bold"),
    padx=30,
    pady=20
)
popup_label.pack()

def show_popup(text):
    popup_label.config(text=text)
    popup.update_idletasks()
    w = popup.winfo_reqwidth()
    h = popup.winfo_reqheight()
    popup.geometry(f"{w}x{h}+{screen_w//2 - w//2}+{screen_h//2 - h//2}")
    popup.deiconify()

def hide_popup():
    popup.withdraw()

print("Gesture System Running... Enter 'ctrl + c' in terminal to quit.")

while True:
    popup.update()

    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    scroll_mode = False
    brightness_mode = False
    lock_mode = False

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            lm = hand.landmark
            def xy(id): return int(lm[id].x * wCam), int(lm[id].y * hCam)

            tx, ty = xy(4)
            ix, iy = xy(8)
            mx, my = xy(12)
            rx, ry = xy(16)
            lx, ly = xy(20)

            for x, y in [(tx,ty),(ix,iy),(mx,my),(rx,ry),(lx,ly)]:
                cv2.circle(frame, (x,y), 7, (255,255,0), cv2.FILLED)

            index_down = lm[8].y > lm[6].y
            middle_down = lm[12].y > lm[10].y
            ring_down = lm[16].y > lm[14].y
            little_down = lm[20].y > lm[18].y
            thumb_down_fist = lm[4].x < lm[3].x

            if index_down and middle_down and ring_down and little_down and thumb_down_fist:
                scroll_mode = True
                cv2.putText(frame,"SCROLL MODE",(10,200),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2)
                hand_center_y = int(lm[9].y*hCam)
                if scroll_last_y is not None:
                    dy = hand_center_y - scroll_last_y
                    now = time.time()
                    if abs(dy)>12 and now-scroll_last_time>scroll_cooldown:
                        if dy<0:
                            pyautogui.scroll(400)
                        else:
                            pyautogui.scroll(-400)
                        scroll_last_time = now
                scroll_last_y = hand_center_y
            else:
                scroll_last_y = None

            index_up  = lm[8].y < lm[6].y
            middle_up = lm[12].y < lm[10].y
            ring_up   = lm[16].y < lm[14].y
            little_up = lm[20].y < lm[18].y
            thumb_down = lm[4].x > lm[3].x

            if index_up and middle_up and ring_up and little_up and thumb_down:
                brightness_mode = True
                cv2.putText(frame,"BRIGHTNESS MODE",(10,110),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
                hand_center_y = int(lm[9].y*hCam)
                if brightness_last_y is not None:
                    dy = hand_center_y - brightness_last_y
                    now = time.time()
                    if abs(dy)>10 and now-brightness_last_time>brightness_cooldown:
                        current_brightness = sbc.get_brightness()[0]
                        if dy<0:
                            sbc.set_brightness(min(current_brightness+10,100))
                        else:
                            sbc.set_brightness(max(current_brightness-10,0))
                        brightness_last_time = now
                brightness_last_y = hand_center_y
            else:
                brightness_last_y = None

            ring_down = lm[16].y > lm[14].y
            little_down = lm[20].y > lm[18].y
            index_up = lm[8].y < lm[6].y
            middle_up = lm[12].y < lm[10].y

            if index_up and middle_up and ring_down and little_down:
                lock_mode = True
                if lock_start_time is None:
                    lock_start_time = time.time()

                elapsed = time.time() - lock_start_time
                remaining = max(0, lock_duration - int(elapsed))

                show_popup(f"⚠ Laptop locking in {remaining} seconds. Change gesture to cancel.")

                if elapsed >= lock_duration:
                    hide_popup()
                    os.system("rundll32.exe user32.dll,LockWorkStation")
                    lock_start_time = None

            else:
                if lock_start_time is not None:
                    hide_popup()
                lock_start_time = None

            if not scroll_mode and not brightness_mode and not lock_mode:
                hide_popup()
                finger_x, finger_y = ix, iy
                finger_x = np.clip(finger_x, frame_margin, wCam-frame_margin)
                finger_y = np.clip(finger_y, frame_margin, hCam-frame_margin)
                target_x = np.interp(finger_x,(frame_margin,wCam-frame_margin),(0,screen_w))
                target_y = np.interp(finger_y,(frame_margin,hCam-frame_margin),(0,screen_h))
                curr_x = prev_x + (target_x-prev_x)/smoothening
                curr_y = prev_y + (target_y-prev_y)/smoothening
                pyautogui.moveTo(curr_x,curr_y)
                prev_x, prev_y = curr_x, curr_y

            if not scroll_mode and not brightness_mode and not lock_mode:
                dist_index = math.hypot(ix-tx, iy-ty)
                dist_middle = math.hypot(mx-tx,my-ty)
                dist_ring = math.hypot(rx-tx,ry-ty)
                dist_little = math.hypot(lx-tx,ly-ty)
                now = time.time()
                if dist_index<pinch_threshold and now-last_time>cooldown:
                    pyautogui.click()
                    last_time = now
                elif dist_middle<pinch_threshold and now-last_time>cooldown:
                    pyautogui.press("volumeup")
                    last_time = now
                elif dist_ring<pinch_threshold and now-last_time>cooldown:
                    pyautogui.press("volumedown")
                    last_time = now
                elif dist_little<pinch_threshold and now-last_time>cooldown:
                    pyautogui.press("volumemute")
                    last_time = now

            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

hide_popup()
cap.release()
cv2.destroyAllWindows()
popup.destroy()