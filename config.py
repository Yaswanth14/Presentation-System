# Constants
screenWidth, screenHeight = 1280, 720
folderPath = "Presentation"
imgNumber = 0
cameraHeight, cameraWidth = int(120 * 1.2), int(213 * 1.2)
gestureThresholdHeight = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 15
zoomFactor = 1.0
minZoom = 1.0
maxZoom = 4.0

# Gestures
leftSide = [1, 0, 0, 0, 0]
rightSide = [0, 0, 0, 0, 1]
pointerSide = [0, 1, 1, 0, 0]
drawSide = [0, 1, 0, 0, 0]
undoSide = [0, 1, 1, 1, 0]
zoominSide = [0, 1, 0, 0, 1]
zoomoutSide = [0, 1, 1, 1, 1]