import cv2, os
from .config import *
from .utils import draw_circle, draw_line, get_list_of_presentation_images

class Presentation:
    def __init__(self, folder_path):
        self.path_images = get_list_of_presentation_images(folder_path)
        self.img_number = 0
        self.annotations = [[]]
        self.annotation_number = 0
        self.annotation_start = False

    def load_current_image(self):
        path_full_image = os.path.join(folderPath, self.path_images[self.img_number])
        img_current = cv2.imread(path_full_image)

        # Apply zoom
        new_width, new_height = int(screenWidth * zoomFactor), int(screenHeight * zoomFactor)
        img_current = cv2.resize(img_current, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Center zoomed image
        x_offset = (new_width - screenWidth) // 2
        y_offset = (new_height - screenHeight) // 2
        img_current = img_current[y_offset:y_offset + screenHeight, x_offset:x_offset + screenWidth]

        return img_current

    def handle_gestures(self, hands, img_current, index_finger):
        if hands and not buttonPressed:
            hand = hands[0]
            fingers = self.detector.fingersUp(hand)
            cx, cy = hand["center"]

            if cy <= gestureThresholdHeight:  # Hand on top right quarter

                # Gesture 1 - Left
                if fingers == leftSide:
                    self.annotations = [[]]
                    self.annotation_number = 0
                    self.annotation_start = False
                    buttonPressed = True
                    self.img_number = (self.img_number - 1) % len(self.path_images)

                # Gesture 2 - Right
                if fingers == rightSide:
                    self.annotations = [[]]
                    self.annotation_number = 0
                    self.annotation_start = False
                    buttonPressed = True
                    self.img_number = (self.img_number + 1) % len(self.path_images)

                # Gesture 3 - Pointer
                if fingers == pointerSide:
                    draw_circle(img_current, index_finger, 8, (0, 0, 0), cv2.FILLED)

                # Gesture 4 - Draw Pointer
                if fingers == drawSide:
                    if not self.annotation_start:
                        self.annotation_start = True
                        self.annotation_number += 1
                        self.annotations.append([])
                    draw_circle(img_current, index_finger, 8, (0, 0, 255), cv2.FILLED)
                    self.annotations[self.annotation_number].append(index_finger)
                else:
                    self.annotation_start = False

                # Gesture 5- Undo
                if fingers == undoSide:
                    if self.annotation_number > 0:
                        self.annotation_number -= 1
                        self.annotations.pop(-1)
                        buttonPressed = True

                # Gesture 6 - Zoom In
                if fingers == zoominSide:
                    if zoomFactor < maxZoom:
                        zoomFactor += 0.25
                        buttonPressed = True

                # Gesture 7 - Zoom Out
                if fingers == zoomoutSide:
                    if zoomFactor > minZoom:
                        zoomFactor -= 0.25
                        buttonPressed = True

    def draw_annotations(self, img_current):
        for i in range(len(self.annotations)):
            for j in range(1, len(self.annotations[i])):
                draw_line(img_current, self.annotations[i][j-1], self.annotations[i][j], (0, 0, 200), 8)

    def add_camera_footage(self, img_current, camera):
        img_small = cv2.resize(camera, (cameraWidth, cameraHeight))
        h, w, _ = img_current.shape
        img_current[0:cameraHeight, w - cameraWidth:w] = img_small
        return img_current