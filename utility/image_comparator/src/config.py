"""
Configuration and Constants for Image Comparator Module

This module contains all configuration constants and default values used
across the image comparison system.
"""

import os


class ImageComparatorConfig:
    """Configuration class containing all default values and constants."""
    
    # Default detection threshold for template matching
    DEFAULT_THRESHOLD = 0.7
    
    # Maximum scale factor for template resizing
    MAX_TEMPLATE_SCALE = 0.5
    
    # OpenBLAS thread configuration to reduce threading issues
    OPENBLAS_NUM_THREADS = "1"
    
    # OpenCV template matching method
    TEMPLATE_MATCH_METHOD = 'TM_CCOEFF_NORMED'
    
    # Annotation settings
    DETECTION_COLOR = (0, 255, 0)  # Green color in BGR format
    DETECTION_LINE_THICKNESS = 2
    DETECTION_FONT = 'FONT_HERSHEY_SIMPLEX'
    DETECTION_FONT_SCALE = 0.6
    DETECTION_TEXT_THICKNESS = 2
    DETECTION_TEXT_OFFSET_Y = 10
    DETECTION_TEXT_MIN_Y = 20
    
    # File extensions for supported image formats
    SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}
    
    @classmethod
    def configure_environment(cls):
        """Configure environment variables for optimal OpenCV performance."""
        os.environ["OPENBLAS_NUM_THREADS"] = cls.OPENBLAS_NUM_THREADS


class BatchProcessingConfig:
    """Configuration specific to batch processing operations."""
    
    # Default output filename suffix for annotated images
    ANNOTATED_SUFFIX = "_annotated"
    
    # Progress logging interval (log every N images)
    PROGRESS_LOG_INTERVAL = 10
    
    # Maximum batch size for processing (0 = unlimited)
    MAX_BATCH_SIZE = 0


class DetectionResult:
    """Standard result structure for detection operations."""
    
    def __init__(self, label="", score=0.0, top_left=(0, 0), bottom_right=(0, 0)):
        self.label = label
        self.score = score
        self.top_left = top_left
        self.bottom_right = bottom_right
    
    def to_dict(self):
        """Convert result to dictionary format."""
        return {
            "label": self.label,
            "score": self.score,
            "top_left": self.top_left,
            "bottom_right": self.bottom_right
        }
    
    def __str__(self):
        return f"DetectionResult(label='{self.label}', score={self.score:.4f}, location={self.top_left})"


# Initialize environment on module import
ImageComparatorConfig.configure_environment()
