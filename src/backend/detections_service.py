from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
import math
import cv2
import numpy as np
from ultralytics import YOLO
from noise_detector import is_noisy

font_path = "arial.ttf"
font_size = 24

font = ImageFont.truetype(font_path, font_size)

class Detection:
    def __init__(self, bbox, calculated_size, class_name, defects_count, is_noisy, passed, size_passed):
        self.bbox = bbox
        self.calculatedSize = calculated_size
        self.className = class_name
        self.defectsCount = defects_count
        self.isRough = is_noisy
        self.passed = passed
        self.sizePassed = size_passed

# Cache the YOLO models
detail_finder = YOLO("details.pt")
defects_finder = YOLO("defects.pt")

# Detail size thresholds and class names
detailSizeThresholds = {
    "bars": (0.2, 0.1),
    "pads": (0.05, 0.02),
    "nuts": (0.05, 0.05),
    "bolts": (0.1, 0.05),
    "spacers": (0.1, 0.15)
}

classNames = {
    "bars": "Брусок",
    "pads": "Шайба",
    "nuts": "Гайка",
    "bolts": "Болт",
    "spacers": "Прокладка"
}

defectNames = {
    "adj": "прил.",
    "int": "целост.",
    "geo": "геом.",
    "pro": "обраб.",
    "non": "выполн."
}

def preprocess_image(image: Image.Image) -> Tuple[Image.Image, list, list]:
    # Convert the PIL Image to OpenCV format
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Use the cached detail and defects detection models
    detail_results = detail_finder(image_cv)
    defects_results = defects_finder(image_cv)

    annotated_image = image.copy()
    draw = ImageDraw.Draw(annotated_image)

    for result in detail_results:
        for bbox in result.boxes:
            box, class_id, score = (bbox.xywh[0], int(bbox.cls[0]), float(bbox.conf[0]))
            x, y, width, height = [int(v) for v in box]
            class_name = classNames.get(result.names[class_id].lower(), 'Unknown')
            draw_bounding_box(draw, x, y, width, height, class_name, score, font, (36, 255, 12))

    for result in defects_results:
        for bbox in result.boxes:
            box, class_id, score = (bbox.xywh[0], int(bbox.cls[0]), float(bbox.conf[0]))
            x, y, width, height = [int(v) for v in box]
            class_name = defectNames.get(result.names[class_id].lower(), 'Unknown')
            draw_bounding_box(draw, x, y, width, height, class_name, score, font, (255, 0, 0))

    return annotated_image, detail_results, defects_results

def draw_bounding_box(draw: ImageDraw.ImageDraw, x, y, width, height, class_name, score, font, color):
    """Draw a bounding box with the class name and score on the image."""
    draw.rectangle([(x - width // 2, y - height // 2), (x + width // 2, y + height // 2)], outline=color, width=2)
    text = f"{class_name} ({score:.2f})"
    text_size = draw.textbbox((0, 0), text, font)[2:]
    draw.text((x - width // 2, y - height // 2 - text_size[1] - 4), text, font=font, fill=color)

def process_image(image: Image.Image, detail_results: list, defect_results: list, scale_x: float, scale_y: float) -> Dict:
    """
    Processes the image and returns the detection results.
    """
    
    detections = []
    passed_count = 0
    
    for result in detail_results:
        for i, bbox in enumerate(result.boxes):
            x1, y1, x2, y2 = [int(coord) for coord in bbox.xyxy[0]]
            calculated_size = {
                "width": (x2 - x1) * scale_x,
                "height": (y2 - y1) * scale_y
            }
            
            # Check if the part is noisy
            part_image = image.crop((x1, y1, x2, y2))
            is_noisy_part = is_noisy(part_image)
            
            # Count the number of defects for the part
            part_defects = [defect for defect in defect_results[0].boxes.xyxy if defect[0] == i]
            defects_count = len(part_defects)
            
            # Determine the class name based on the size
            class_id = int(bbox.cls[0])
            class_name = result.names[class_id].lower()
            
            # Determine if the part passed the inspection
            size_passed = calculated_size["height"] > detailSizeThresholds[class_name][0] and calculated_size["height"] > detailSizeThresholds[class_name][1]
            passed = size_passed and not is_noisy_part and defects_count == 0
            
            if passed:
                passed_count += 1
            
            detection = Detection(
                bbox={"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1},
                calculated_size=calculated_size,
                class_name=classNames[class_name],
                defects_count=defects_count,
                is_noisy=is_noisy_part,
                passed=passed,
                size_passed=size_passed
            )
            detections.append(detection)
    
    return {
        "detections": [detection.__dict__ for detection in detections],
        "detectionsCount": len(detections),
        "passedCount": passed_count,
    }
