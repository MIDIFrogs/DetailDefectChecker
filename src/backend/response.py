import json
from dataclasses import dataclass
from typing import List

@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int

@dataclass
class CalculatedSize:
    width: float
    height: float

@dataclass
class Detection:
    bbox: BoundingBox
    calculated_size: CalculatedSize
    class_name: str
    defects_count: int
    is_rough: bool
    passed: bool
    size_passed: bool

@dataclass
class Response:
    detections: List[Detection]
    detections_count: int
    download_id: int
    passed_count: int

def from_json(json_str: str) -> Response:
    data = json.loads(json_str)
    detections = [
        Detection(
            bbox=BoundingBox(**detection['bbox']),
            calculated_size=CalculatedSize(**detection['calculatedSize']),
            class_name=detection['className'],
            defects_count=detection['defectsCount'],
            is_rough=detection['isRough'],
            passed=detection['passed'],
            size_passed=detection['sizePassed']
        ) for detection in data['detections']
    ]
    return Response(
        detections=detections,
        detections_count=data['detectionsCount'],
        download_id=data['downloadId'],
        passed_count=data['passedCount']
    )