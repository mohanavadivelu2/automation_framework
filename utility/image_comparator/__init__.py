"""
Image Comparator Module

A modular image comparison and template matching library with focused architecture.
This module provides functionality for single template detection and multi-template matching
with proper logging and error handling.

Architecture:
- CoreMatcher: Fundamental OpenCV operations and utilities
- SingleDetector: Specialized for 1:1 template detection
- MultiDetector: Specialized for best match detection from multiple templates

Usage Examples:

    # Single template detection
    from utility.image_comparator import SingleDetector
    detector = SingleDetector()
    result = detector.detect("reference.png", "template.png")
    
    # Multi-template detection (state detection)
    from utility.image_comparator import MultiDetector
    multi_detector = MultiDetector()
    templates = {"on": "on.png", "off": "off.png"}
    message, state = multi_detector.detect_best_match("screenshot.png", templates)
    
    # Core operations (if you need low-level access)
    from utility.image_comparator import CoreMatcher
    core = CoreMatcher()
    ref_img, ref_gray = core.prepare_reference_image("reference.png")
"""

# Import configuration and result classes
from .src.config import (
    ImageComparatorConfig,
    BatchProcessingConfig,
    DetectionResult
)

# Import core functionality
from .src.core_matcher import CoreMatcher

# Import detector classes
from .src.single_detector import SingleDetector
from .src.multi_detector import MultiDetector

# Version information
__version__ = "2.1.0"
__author__ = "Automation Framework Team"
__description__ = "Modular image comparison and template matching library"

# Public API exports
__all__ = [
    # Configuration classes
    "ImageComparatorConfig",
    "BatchProcessingConfig",
    "DetectionResult",
    
    # Core functionality
    "CoreMatcher",
    
    # Detector classes (main API)
    "SingleDetector",
    "MultiDetector",
    
    # Module metadata
    "__version__",
    "__author__",
    "__description__"
]

# Convenience factory functions
def create_single_detector(threshold=None, logger=None):
    """
    Factory function to create a SingleDetector instance.
    
    Args:
        threshold (float, optional): Detection threshold (0.0-1.0)
        logger: Optional logger instance
        
    Returns:
        SingleDetector: Configured detector instance
    """
    return SingleDetector(logger=logger, threshold=threshold)

def create_multi_detector(logger=None):
    """
    Factory function to create a MultiDetector instance.
    
    Args:
        logger: Optional logger instance
        
    Returns:
        MultiDetector: Configured detector instance
    """
    return MultiDetector(logger=logger)

# Add factory functions to exports
__all__.extend([
    "create_single_detector",
    "create_multi_detector"
])

# Module initialization
def get_version():
    """Get the current version of the image comparator module."""
    return __version__

def get_supported_formats():
    """Get list of supported image formats."""
    return list(ImageComparatorConfig.SUPPORTED_IMAGE_EXTENSIONS)

def get_default_config():
    """Get the default configuration settings."""
    return {
        "default_threshold": ImageComparatorConfig.DEFAULT_THRESHOLD,
        "max_template_scale": ImageComparatorConfig.MAX_TEMPLATE_SCALE,
        "supported_formats": get_supported_formats(),
        "detection_color": ImageComparatorConfig.DETECTION_COLOR,
        "batch_progress_interval": BatchProcessingConfig.PROGRESS_LOG_INTERVAL
    }

# Add utility functions to exports  
__all__.extend([
    "get_version",
    "get_supported_formats",
    "get_default_config"
])
