import cv2
import os
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# Variables
screenWidth, screenHeight = 1280, 720
folderPath = "Presentation"
imgNumber = 0
cameraHeight, cameraWidth = int(120 * 1.2), int(213 * 1.2)
gestureThresholdHeight = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 15
annotations = [[]]
annotationNumber = 0
annotationStart = False

# Gestures
leftSide = [1, 0, 0, 0, 0]
rightSide = [0, 0, 0, 0, 1]
pointerSide = [0, 1, 1, 0, 0]
drawSide = [0, 1, 0, 0, 0]
undoSide = [0, 1, 1, 1, 0]

# Hand Detector
detector = HandDetector(detectionCon=0.5, maxHands=1)

# Get list of presentation images
try:
  pathImages = sorted(os.listdir(folderPath), key=len)
except FileNotFoundError:
  print(f"Error: Folder '{folderPath}' not found. Please check the path.")
  exit()
slidesCount = len(pathImages)

# Camera Setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
  print("Error: Failed to open camera.")
  exit()
cap.set(3, screenWidth)
cap.set(4, screenHeight)

while True:
    # Video camera
    success, camera = cap.read()
    if not success:
        print("Error: Failed to read camera frame.")
        break
    camera = cv2.flip(camera, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    imgCurrent = cv2.resize(imgCurrent, (screenWidth, screenHeight)) 

    # Gesture handling
    hands, camera = detector.findHands(camera)
    cv2.line(camera, (0, gestureThresholdHeight), (screenWidth, gestureThresholdHeight), (0, 200, 200), 2)

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand["center"]
        # print(fingers)

        #Index finger landmarks
        landmarks = hand['lmList']
        xIndex = int(np.interp(landmarks[8][0], [screenWidth//2, w], [0, screenWidth]))
        yIndex = int(np.interp(landmarks[8][1], [150, screenHeight-150], [0, screenHeight]))
        indexFinger = xIndex, yIndex

        if cy <= gestureThresholdHeight: #Hand on top right quarter

            # Gesture 1 - Left
            if fingers == leftSide:
                annotations = [[]]
                annotationNumber = 0
                annotationStart = False
                buttonPressed = True
                imgNumber = (imgNumber-1)%slidesCount

            # Gesture 2 - Right
            if fingers == rightSide:
                annotations = [[]]
                annotationNumber = 0
                annotationStart = False
                buttonPressed = True
                imgNumber = (imgNumber+1)%slidesCount

        # Gesture 3 - Pointer
        if fingers == pointerSide:
            cv2.circle(imgCurrent, indexFinger, 8, (0, 0, 0), cv2.FILLED)
        
        # Gesture 4 - Draw Pointer
        if fingers == drawSide:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 8, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False
        
        # Gesture 5- Undo
        if fingers == undoSide:
            if annotationNumber > 0:
                annotationNumber -= 1
                annotations.pop(-1)
                buttonPressed = True


    # Button presses iterations
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonPressed = False
            buttonCounter = 0
    
    for i in range(len(annotations)):
        for j in range(1, len(annotations[i])):
            cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0, 0, 200), 8)


    # Adding camera footage on slides
    imgSmall = cv2.resize(camera, (cameraWidth, cameraHeight))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:cameraHeight, w-cameraWidth:w] = imgSmall

    cv2.imshow("Slides", imgCurrent)
    # cv2.imshow("Video", camera)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break