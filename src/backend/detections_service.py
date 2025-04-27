from typing import List, Dict
from PIL import Image
import math

class Detection:
    def __init__(self, bbox, calculated_size, class_name, defects_count, is_rough, passed, size_passed):
        self.bbox = bbox
        self.calculatedSize = calculated_size
        self.className = class_name
        self.defectsCount = defects_count
        self.isRough = is_rough
        self.passed = passed
        self.sizePassed = size_passed

def process_image(image: Image, scale_x: float, scale_y: float) -> Dict:
    # Dummy processing logic
    detections = [
        Detection(
            bbox={"x": 0, "y": 0, "width": 100, "height": 100},
            calculated_size={"width": 0.5 * scale_x, "height": 0.5 * scale_y},
            class_name="Part A",
            defects_count=1,
            is_rough=False,
            passed=False,
            size_passed=True
        )
    ]

    return {
        "detections": [detection.__dict__ for detection in detections],
        "detectionsCount": len(detections),
        "passedCount": 1,
    }
