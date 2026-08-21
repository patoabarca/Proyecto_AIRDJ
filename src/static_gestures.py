from dataclasses import dataclass
from enum import Enum
from math import acos, degrees, hypot
from typing import Dict, List, Tuple

from src.hand_detector import HandDetectionResult, HandLandmark, LandmarkPoint


class GestureLabel(str, Enum):
    PALMA = "PALMA"
    PUNO = "PUNO"
    INDICE = "INDICE"
    NEUTRO = "NEUTRO"


@dataclass(frozen=True)
class StaticGestureResult:
    label: GestureLabel
    confidence: float
    extended_fingers: Tuple[str, ...]


class StaticGestureRecognizer:
    def __init__(
        self,
        extension_angle_threshold: float = 150.0,
        extension_ratio_threshold: float = 1.08,
    ) -> None:
        self.extension_angle_threshold = extension_angle_threshold
        self.extension_ratio_threshold = extension_ratio_threshold

    def classify(self, result: HandDetectionResult) -> StaticGestureResult:
        if not result.detected or len(result.landmarks) != 21:
            return StaticGestureResult(GestureLabel.NEUTRO, 0.0, ())

        points = result.landmarks
        palm_scale = self._distance(points, HandLandmark.WRIST, HandLandmark.MIDDLE_FINGER_MCP)
        if palm_scale <= 0.0:
            return StaticGestureResult(GestureLabel.NEUTRO, 0.0, ())

        extended = {
            finger: self._is_extended(points, landmarks, palm_scale)
            for finger, landmarks in self._finger_landmarks().items()
        }
        extended_names = tuple(name for name, is_extended in extended.items() if is_extended)
        extended_count = len(extended_names)

        if extended_count == 5:
            label = GestureLabel.PALMA
        elif extended_count == 1 and extended["index"]:
            label = GestureLabel.INDICE
        elif not any(extended.values()) or (
            extended_count == 1 and extended["thumb"]
        ):
            label = GestureLabel.PUNO
        else:
            label = GestureLabel.NEUTRO

        confidence = self._confidence(label, extended_count)
        return StaticGestureResult(label, confidence, extended_names)

    @staticmethod
    def _finger_landmarks() -> Dict[str, Tuple[HandLandmark, HandLandmark, HandLandmark, HandLandmark]]:
        return {
            "thumb": (
                HandLandmark.THUMB_CMC,
                HandLandmark.THUMB_MCP,
                HandLandmark.THUMB_IP,
                HandLandmark.THUMB_TIP,
            ),
            "index": (
                HandLandmark.INDEX_FINGER_MCP,
                HandLandmark.INDEX_FINGER_PIP,
                HandLandmark.INDEX_FINGER_DIP,
                HandLandmark.INDEX_FINGER_TIP,
            ),
            "middle": (
                HandLandmark.MIDDLE_FINGER_MCP,
                HandLandmark.MIDDLE_FINGER_PIP,
                HandLandmark.MIDDLE_FINGER_DIP,
                HandLandmark.MIDDLE_FINGER_TIP,
            ),
            "ring": (
                HandLandmark.RING_FINGER_MCP,
                HandLandmark.RING_FINGER_PIP,
                HandLandmark.RING_FINGER_DIP,
                HandLandmark.RING_FINGER_TIP,
            ),
            "pinky": (
                HandLandmark.PINKY_MCP,
                HandLandmark.PINKY_PIP,
                HandLandmark.PINKY_DIP,
                HandLandmark.PINKY_TIP,
            ),
        }

    def _is_extended(
        self,
        points: List[LandmarkPoint],
        landmarks: Tuple[HandLandmark, HandLandmark, HandLandmark, HandLandmark],
        palm_scale: float,
    ) -> bool:
        mcp, pip, dip, tip = landmarks
        angle = self._angle(points[mcp], points[pip], points[tip])
        tip_distance = self._distance(points, HandLandmark.WRIST, tip)
        pip_distance = self._distance(points, HandLandmark.WRIST, pip)
        return (
            angle >= self.extension_angle_threshold
            and tip_distance >= pip_distance * self.extension_ratio_threshold
            and tip_distance >= palm_scale * 1.15
        )

    @staticmethod
    def _distance(
        points: List[LandmarkPoint], first: HandLandmark, second: HandLandmark
    ) -> float:
        return hypot(
            points[first].x - points[second].x,
            points[first].y - points[second].y,
        )

    @staticmethod
    def _angle(
        first: LandmarkPoint, vertex: LandmarkPoint, second: LandmarkPoint
    ) -> float:
        first_vector = (first.x - vertex.x, first.y - vertex.y)
        second_vector = (second.x - vertex.x, second.y - vertex.y)
        first_length = hypot(*first_vector)
        second_length = hypot(*second_vector)
        if first_length == 0.0 or second_length == 0.0:
            return 0.0
        cosine = (
            first_vector[0] * second_vector[0]
            + first_vector[1] * second_vector[1]
        ) / (first_length * second_length)
        return degrees(acos(max(-1.0, min(1.0, cosine))))

    @staticmethod
    def _confidence(label: GestureLabel, extended_count: int) -> float:
        if label in (GestureLabel.PALMA, GestureLabel.PUNO):
            return 1.0 if extended_count in (0, 5) else 0.5
        if label == GestureLabel.INDICE:
            return 1.0
        return 0.25
