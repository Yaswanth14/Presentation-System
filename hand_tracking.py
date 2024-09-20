from cvzone.HandTrackingModule import HandDetector

class HandTracker:
    def __init__(self, detection_con=0.5, max_hands=1):
        self.detector = HandDetector(detectionCon=detection_con, maxHands=max_hands)

    def find_hands(self, image):
        return self.detector.findHands(image)

    def fingers_up(self, hand):
        return self.detector.fingersUp(hand)