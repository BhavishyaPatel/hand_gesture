# Hand Gesture Control System (Webcam-Based)

A complete gesture-controlled interface for Windows, using Python, OpenCV, MediaPipe, and Tkinter.

This system allows you to control basic functions in laptop **without touching the mouse or keyboard**, using only your hand.

## ✋ Features

### 🖱 Cursor Control
- Move cursor with index finger
- Smooth, stabilized pointer movement

### 👆 Click Gesture
- Pinch (thumb + index) → Left Click

### 🔊 Volume Control
- Thumb + Middle finger pinch → Volume Up  
- Thumb + Ring finger pinch → Volume Down  
- Thumb + Little finger pinch → Mute  

### 🌞 Brightness Control
- Show 4 fingers → Brightness Mode  
- Move hand up/down → Adjust brightness  
- Cursor movement disabled during brightness mode

### 📜 Scroll Control
- Make a fist → Scroll Mode  
- Move hand up/down → Scroll  
- Cursor movement disabled during scroll mode

### 🔒 Laptop Lock (Peace Sign Gesture)
- Show ✌️ sign → Starts a 3-second countdown  
- A popup window appears:  
  **“Laptop locking in 3 seconds. Change gesture to cancel.”**  
- If gesture stays → Auto-locks laptop  
- If gesture changes → Lock canceled

## 🛠 Technologies Used
- Python
- OpenCV
- MediaPipe Hands
- NumPy
- PyAutoGUI
- Tkinter (Popup UI)
- Screen Brightness Control

## 📦 Installation




## ▶️ Run the Program




## ⚠️ Notes
- Works on Windows (due to LockWorkStation command)
- Laptop must allow brightness control
- Webcam required