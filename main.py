import cv2
import numpy as np
from .config import screenWidth, screenHeight, folderPath, cameraHeight, cameraWidth, gestureThresholdHeight
from .hand_tracking import HandTracker
from .presentation import Presentation

def main():
    cv2.namedWindow("Slides", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Slides", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    (x, y, screenWidth, screenHeight) = cv2.getWindowImageRect("Slides")
    screenWidth -= 150
    screenHeight -= 150

    presentation = Presentation(folderPath)
    hand_tracker = HandTracker()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Failed to open camera.")
        exit()
    cap.set(3, screenWidth)
    cap.set(4, screenHeight)

    while True:
        success, camera = cap.read()
        if not success:
            print("Error: Failed to read camera frame.")
            break
        camera = cv2.flip(camera, 1)

        img_current = presentation.load_current_image()

        hands, camera = hand_tracker.find_hands(camera)
        cv2.line(camera, (0, gestureThresholdHeight), (screenWidth, gestureThresholdHeight), (0, 200, 200), 2)

        # Get the index finger landmark for drawing/annotation purposes
        if hands:
            hand = hands[0]
            landmarks = hand['lmList']
            x_index = int(np.interp(landmarks[8][0], [screenWidth // 2, screenWidth], [0, screenWidth]))
            y_index = int(np.interp(landmarks[8][1], [50, screenHeight - 50], [0, screenHeight]))
            index_finger = (x_index, y_index)  # Now defined as a tuple of (x, y) coordinates

        presentation.handle_gestures(hands, index_finger, img_current)  # Pass img_current
        presentation.draw_annotations(img_current)

        img_current = presentation.add_camera_footage(img_current, camera)

        cv2.imshow("Slides", img_current)
        # cv2.imshow("Video", camera)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

if __name__ == "__main__":
    main()