import unittest

from src.hand_detector import HandDetectionResult, HandLandmark, LandmarkPoint
from src.static_gestures import GestureLabel, StaticGestureRecognizer


class TestStaticGestureRecognizer(unittest.TestCase):
    def setUp(self):
        self.recognizer = StaticGestureRecognizer()

    def test_open_palm(self):
        result = self._hand_result({"thumb", "index", "middle", "ring", "pinky"})

        gesture = self.recognizer.classify(result)

        self.assertEqual(gesture.label, GestureLabel.PALMA)
        self.assertEqual(set(gesture.extended_fingers), {"thumb", "index", "middle", "ring", "pinky"})

    def test_closed_fist(self):
        result = self._hand_result(set())

        gesture = self.recognizer.classify(result)

        self.assertEqual(gesture.label, GestureLabel.PUNO)
        self.assertEqual(gesture.extended_fingers, ())

    def test_index_gesture(self):
        result = self._hand_result({"index"})

        gesture = self.recognizer.classify(result)

        self.assertEqual(gesture.label, GestureLabel.INDICE)
        self.assertEqual(gesture.extended_fingers, ("index",))

    def test_missing_hand_is_neutral(self):
        result = HandDetectionResult(detected=False, landmarks=[])

        gesture = self.recognizer.classify(result)

        self.assertEqual(gesture.label, GestureLabel.NEUTRO)
        self.assertEqual(gesture.confidence, 0.0)

    def _hand_result(self, extended_fingers):
        coordinates = [(0.5, 0.8) for _ in range(21)]
        coordinates[HandLandmark.MIDDLE_FINGER_MCP] = (0.5, 0.62)

        finger_data = {
            "thumb": (1, 2, 3, 4, (0.15, 0.57)),
            "index": (5, 6, 7, 8, (0.42, 0.15)),
            "middle": (9, 10, 11, 12, (0.5, 0.10)),
            "ring": (13, 14, 15, 16, (0.58, 0.15)),
            "pinky": (17, 18, 19, 20, (0.66, 0.22)),
        }
        for name, (mcp, pip, dip, tip, open_tip) in finger_data.items():
            x = open_tip[0] if name != "thumb" else coordinates[mcp][0]
            coordinates[mcp] = (x, 0.62)
            if name == "thumb":
                coordinates[1] = (0.45, 0.74)
                coordinates[pip] = (0.35, 0.67)
                coordinates[dip] = (0.25, 0.62)
            else:
                coordinates[pip] = (x, 0.45)
                coordinates[dip] = (x, 0.30)
            if name in extended_fingers:
                coordinates[tip] = open_tip
            elif name == "thumb":
                coordinates[tip] = (0.47, 0.70)
            else:
                coordinates[tip] = (x, 0.68)

        landmarks = [
            LandmarkPoint(index=index, x=x, y=y, z=0.0, pixel_x=0, pixel_y=0)
            for index, (x, y) in enumerate(coordinates)
        ]
        return HandDetectionResult(detected=True, landmarks=landmarks)


if __name__ == "__main__":
    unittest.main()
