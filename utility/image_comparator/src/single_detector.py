"""
Single Template Detection Module

This module provides functionality for detecting a single template in a reference image.
It handles threshold-based decision making and provides a clean API for 1:1 template
matching operations.
"""

import os
from .core_matcher import CoreMatcher
from .config import ImageComparatorConfig
from .logging_utils import get_logger


class SingleDetector:
    """
    Class for single template detection operations.
    
    This class provides a simple interface for detecting whether a specific
    template exists in a reference image, with configurable threshold-based
    decision making.
    """

    def __init__(self, logger=None, threshold=None):
        """
        Initialize the SingleDetector instance.
        
        Args:
            logger: Optional logger instance. If None, creates a new logger.
            threshold (float, optional): Detection threshold (0.0-1.0). Uses default if None.
        """
        # Use provided logger or get appropriate logger based on context
        self.logger = logger or get_logger()
        self.core_matcher = CoreMatcher(logger=self.logger)
        self.threshold = threshold or ImageComparatorConfig.DEFAULT_THRESHOLD
        
        if self.logger:
            self.logger.info(f"SingleDetector initialized with threshold: {self.threshold}")

    def detect_single_template(self, ref_img_path, template_path, output_path=None, threshold=None, label=None):
        """
        API method to detect a single template in a reference image.
        
        This method loads both images, performs template matching, and determines
        if the template is present based on the confidence threshold.
        
        Args:
            ref_img_path (str): Path to the reference image file
            template_path (str): Path to the template image file
            output_path (str, optional): Path to save annotated output image
            threshold (float, optional): Detection threshold (0.0-1.0). Uses instance default if None.
            label (str, optional): Custom label for the template. Defaults to filename.
            
        Returns:
            tuple: (result_message, is_detected, detection_result)
                - result_message (str): Human-readable result description
                - is_detected (bool): Whether template was detected above threshold
                - detection_result (DetectionResult): Detailed matching information
        """
        # Use instance threshold if not provided
        detection_threshold = threshold if threshold is not None else self.threshold
        
        if self.logger:
            self.logger.info(f"Starting single template detection: {template_path} in {ref_img_path}")
        
        # Validate input paths
        if not self.core_matcher.validate_image_path(ref_img_path):
            error_msg = f"ERROR: Invalid reference image path: {ref_img_path}"
            if self.logger:
                self.logger.error(error_msg)
            return error_msg, False, None
        
        if not self.core_matcher.validate_image_path(template_path):
            error_msg = f"ERROR: Invalid template image path: {template_path}"
            if self.logger:
                self.logger.error(error_msg)
            return error_msg, False, None
        
        # Load and prepare reference image
        ref_img, ref_gray = self.core_matcher.prepare_reference_image(ref_img_path)
        if ref_img is None:
            error_msg = f"ERROR: Failed to load reference image: {ref_img_path}"
            if self.logger:
                self.logger.error(error_msg)
            return error_msg, False, None
        
        # Load and prepare template image
        template, template_label = self.core_matcher.prepare_template_image(
            template_path, ref_gray.shape, label
        )
        if template is None:
            error_msg = f"ERROR: Failed to load template image: {template_path}"
            if self.logger:
                self.logger.error(error_msg)
            return error_msg, False, None
        
        # Perform template matching
        detection_result = self.core_matcher.perform_template_matching(
            ref_gray, template, template_label
        )
        
        # Determine if detection threshold is met
        is_detected = detection_result.score >= detection_threshold
        status = "DETECTED" if is_detected else "NOT_DETECTED"
        
        # Create result message
        result_message = f"TEMPLATE_{status} (Score: {detection_result.score:.2f})"
        
        # Save annotated image if detection is successful and output path is provided
        if is_detected and output_path:
            try:
                annotated_img = self.core_matcher.draw_detection_rectangle(
                    ref_img.copy(), detection_result
                )
                if self.core_matcher.save_annotated_image(annotated_img, output_path):
                    result_message += f", Image: {output_path}"
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to save output image: {str(e)}")
        
        if self.logger:
            self.logger.info(f"Single template detection completed: {result_message}")
        
        return result_message, is_detected, detection_result

    def detect(self, ref_img_path, template_path, **kwargs):
        """
        Simplified detection method with cleaner interface.
        
        Args:
            ref_img_path (str): Path to the reference image file
            template_path (str): Path to the template image file
            **kwargs: Additional keyword arguments passed to detect_single_template
            
        Returns:
            dict: Detection result dictionary containing:
                - detected (bool): Whether template was detected
                - score (float): Confidence score
                - message (str): Result message
                - detection_result (DetectionResult): Detailed result object
        """
        result_message, is_detected, detection_result = self.detect_single_template(
            ref_img_path, template_path, **kwargs
        )
        
        return {
            "detected": is_detected,
            "score": detection_result.score if detection_result else 0.0,
            "message": result_message,
            "detection_result": detection_result
        }

    def set_threshold(self, new_threshold):
        """
        Update the detection threshold for this detector instance.
        
        Args:
            new_threshold (float): New threshold value (0.0-1.0)
            
        Raises:
            ValueError: If threshold is not in valid range
        """
        if not 0.0 <= new_threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got: {new_threshold}")
        
        old_threshold = self.threshold
        self.threshold = new_threshold
        
        if self.logger:
            self.logger.info(f"Threshold updated from {old_threshold} to {new_threshold}")

    def get_threshold(self):
        """
        Get the current detection threshold.
        
        Returns:
            float: Current threshold value
        """
        return self.threshold

    def validate_template_against_reference(self, ref_img_path, template_path):
        """
        Validate that a template can be processed against a reference image
        without performing actual detection.
        
        Args:
            ref_img_path (str): Path to the reference image file
            template_path (str): Path to the template image file
            
        Returns:
            dict: Validation result containing:
                - valid (bool): Whether validation passed
                - issues (list): List of validation issues found
                - ref_dimensions (tuple): Reference image dimensions if loaded
                - template_dimensions (tuple): Template image dimensions if loaded
        """
        issues = []
        ref_dimensions = None
        template_dimensions = None
        
        # Validate paths
        if not self.core_matcher.validate_image_path(ref_img_path):
            issues.append(f"Invalid reference image path: {ref_img_path}")
        
        if not self.core_matcher.validate_image_path(template_path):
            issues.append(f"Invalid template image path: {template_path}")
        
        if issues:
            return {
                "valid": False,
                "issues": issues,
                "ref_dimensions": ref_dimensions,
                "template_dimensions": template_dimensions
            }
        
        # Try to load images
        ref_img, ref_gray = self.core_matcher.prepare_reference_image(ref_img_path)
        if ref_img is None:
            issues.append(f"Failed to load reference image: {ref_img_path}")
        else:
            ref_dimensions = ref_gray.shape
        
        template = self.core_matcher.load_image(template_path, grayscale=True)
        if template is None:
            issues.append(f"Failed to load template image: {template_path}")
        else:
            template_dimensions = template.shape
            
            # Check if template would need resizing
            if ref_dimensions and template_dimensions:
                h_ref, w_ref = ref_dimensions
                h_temp, w_temp = template_dimensions
                
                if h_temp > h_ref or w_temp > w_ref:
                    scale = min(h_ref / h_temp, w_ref / w_temp, ImageComparatorConfig.MAX_TEMPLATE_SCALE)
                    issues.append(f"Template will be resized (scale factor: {scale:.3f})")
        
        return {
            "valid": len(issues) == 0 or all("will be resized" in issue for issue in issues),
            "issues": issues,
            "ref_dimensions": ref_dimensions,
            "template_dimensions": template_dimensions
        }
