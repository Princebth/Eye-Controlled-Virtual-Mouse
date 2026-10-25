# Eye-Controlled Virtual Mouse

A computer vision project that uses eye tracking and facial landmarks to control mouse actions through a webcam.

## Features
- Cursor movement using iris tracking
- Blink-based mouse interaction
- Scroll control using eye position
- Screenshot capture after prolonged eye closure
- Drag-and-drop interaction
- Real-time webcam processing and FPS display

## Technologies Used
- Python
- OpenCV
- MediaPipe Face Mesh
- PyAutoGUI

## Installation and Usage
1. Install Python compatible with your MediaPipe version.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python eye_mouse.py`
4. Press `q` to exit.

## Note
Mouse actions are controlled by eye tracking and blink detection. Behavior may vary with lighting, camera quality, and calibration.