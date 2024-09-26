import cv2
import os
import numpy as np
import threading
import speech_recognition as sr
from cvzone.HandTrackingModule import HandDetector

# Variables
cv2.namedWindow("Slides", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Slides", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
(x, y, screenWidth, screenHeight) = cv2.getWindowImageRect("Slides") 
screenWidth -= 150
screenHeight -= 150
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
zoomFactor = 1.0
minZoom = 1.0
maxZoom = 4.0
voiceCommand = None  # Global variable to store voice command

# Gestures
leftSide = [1, 0, 0, 0, 0]
rightSide = [0, 0, 0, 0, 1]
pointerSide = [0, 1, 1, 0, 0]
drawSide = [0, 1, 0, 0, 0]
undoSide = [0, 1, 1, 1, 0]
zoominSide = [0, 1, 0, 0, 1]
zoomoutSide = [0, 1, 1, 1, 1]

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

# Function to listen for voice commands
def listen_for_voice_commands():
    global voiceCommand
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                print("Listening for voice commands...")
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                print(f"Recognized voice command: {command}")

                if "babu" in command:
                        if "left slide" in command:
                                voiceCommand = "left"
                        elif "right slide" in command:
                                voiceCommand = "right"   
                        elif "zoom in" in command:
                                voiceCommand = "zoomin"
                        elif "zoom out" in command:
                                voiceCommand = "zoomout"
                        elif "bye" in command:
                            voiceCommand = "exit"

        except sr.UnknownValueError:
            print("Voice command not understood. Please try again.")
        except sr.RequestError:
            print("Could not request results from speech recognition service.")

# Start the voice command listener thread
voice_thread = threading.Thread(target=listen_for_voice_commands)
voice_thread.daemon = True
voice_thread.start()

while True:
    # Video camera
    success, camera = cap.read()
    if not success:
        print("Error: Failed to read camera frame.")
        break
    camera = cv2.flip(camera, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    # Apply zoom
    newWidth, newHeight = int(screenWidth * zoomFactor), int(screenHeight * zoomFactor)
    imgCurrent = cv2.resize(imgCurrent, (newWidth, newHeight), interpolation=cv2.INTER_AREA)

    # Center zoomed image
    xOffset = (newWidth - screenWidth) // 2
    yOffset = (newHeight - screenHeight) // 2
    imgCurrent = imgCurrent[yOffset:yOffset + screenHeight, xOffset:xOffset + screenWidth]

    # Gesture handling
    hands, camera = detector.findHands(camera)
    cv2.line(camera, (0, gestureThresholdHeight), (screenWidth, gestureThresholdHeight), (0, 200, 200), 2)

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand["center"]

        #Index finger landmarks
        landmarks = hand['lmList']
        xIndex = int(np.interp(landmarks[8][0], [screenWidth // 2, screenWidth], [0, screenWidth]))
        yIndex = int(np.interp(landmarks[8][1], [50, screenHeight - 50], [0, screenHeight]))
        indexFinger = xIndex, yIndex

        if cy <= gestureThresholdHeight:  # Hand on top right quarter

            # Gesture 1 - Left
            if fingers == leftSide or voiceCommand == "left":
                annotations = [[]]
                annotationNumber = 0
                annotationStart = False
                buttonPressed = True
                voiceCommand = None
                imgNumber = (imgNumber - 1) % slidesCount

            # Gesture 2 - Right
            if fingers == rightSide or voiceCommand == "right":
                annotations = [[]]
                annotationNumber = 0
                annotationStart = False
                buttonPressed = True
                voiceCommand = None
                imgNumber = (imgNumber + 1) % slidesCount

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

        # Gesture 6 - Zoom In
        if fingers == zoominSide or voiceCommand == "zoomin":
            if zoomFactor < maxZoom:
                zoomFactor += 0.25
                buttonPressed = True

        # Gesture 7 - Zoom Out
        if fingers == zoomoutSide or voiceCommand == "zoomout":
            if zoomFactor > minZoom:
                zoomFactor -= 0.25
                buttonPressed = True

    # Button presses iterations
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonPressed = False
            buttonCounter = 0

    for i in range(len(annotations)):
        for j in range(1, len(annotations[i])):
            cv2.line(imgCurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 200), 8)

    # Adding camera footage on slides
    imgSmall = cv2.resize(camera, (cameraWidth, cameraHeight))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:cameraHeight, w - cameraWidth:w] = imgSmall

    cv2.imshow("Slides", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q') or voiceCommand=="exit":
        break

cap.release()
cv2.destroyAllWindows()
