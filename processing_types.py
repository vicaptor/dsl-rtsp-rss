from enum import Enum

class ProcessingType(Enum):
    OBJECT_DETECTION = "object_detection"
    FACE_DETECTION = "face_detection"
    MOTION_DETECTION = "motion_detection"
    LICENSE_PLATE = "license_plate"
    CROWD_COUNTING = "crowd_counting"
    CUSTOM = "custom"
