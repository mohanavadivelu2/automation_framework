"""
Core Template Matching Module

This module provides the foundational OpenCV operations for image comparison
and template matching. It handles all low-level image processing operations
including loading, resizing, matching, and annotation.
"""

import os
import cv2
import numpy as np
from .config import ImageComparatorConfig, DetectionResult
from .logging_utils import get_logger


class CoreMatcher:
    """
    Core class providing fundamental OpenCV operations for template matching.
    
    This class handles:
    - Image loading and validation
    - Template resizing and preprocessing
    - OpenCV template matching operations
    - Image annotation and drawing utilities
    """

    def __init__(self, logger=None):
        """
        Initialize the CoreMatcher instance.
        
        Args:
            logger: Optional logger instance. If None, creates a new logger.
        """
        self.logger = logger or get_logger()
        self.config = ImageComparatorConfig()
        
        self.logger.info("CoreMatcher initialized successfully")

    def load_image(self, image_path, grayscale=False):
        """
        Load an image from the specified file path with error handling.
        
        Args:
            image_path (str): Path to the image file
            grayscale (bool): If True, load image in grayscale mode
            
        Returns:
            numpy.ndarray or None: Loaded image array, None if loading fails
        """
        try:
            # Determine the OpenCV read mode based on grayscale flag
            read_mode = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
            
            # Attempt to load the image
            image = cv2.imread(image_path, read_mode)
            
            if image is None:
                self.logger.error(f"Failed to load image: {image_path}")
                return None
            
            self.logger.debug(f"Successfully loaded image: {image_path} (Shape: {image.shape})")
            return image
            
        except Exception as e:
            self.logger.error(f"Exception while loading image {image_path}: {str(e)}")
            return None

    def resize_template_if_needed(self, template, ref_shape):
        """
        Resize template image if it's larger than the reference image.
        
        This prevents template matching issues when the template is larger
        than the reference image being searched.
        
        Args:
            template (numpy.ndarray): Template image to potentially resize
            ref_shape (tuple): Shape (height, width) of reference image
            
        Returns:
            numpy.ndarray: Resized template image
        """
        h_ref, w_ref = ref_shape
        h_temp, w_temp = template.shape[:2]
        
        # Check if template dimensions exceed reference image dimensions
        if h_temp > h_ref or w_temp > w_ref:
            # Calculate scaling factor to fit template within reference bounds
            # Also cap the maximum scale to prevent overly large templates
            scale = min(h_ref / h_temp, w_ref / w_temp, self.config.MAX_TEMPLATE_SCALE)
            
            # Calculate new dimensions
            new_width = int(w_temp * scale)
            new_height = int(h_temp * scale)
            
            self.logger.info(f"Resizing template from {w_temp}x{h_temp} to {new_width}x{new_height} (scale: {scale:.3f})")
            
            # Resize the template using OpenCV
            template = cv2.resize(template, (new_width, new_height))
        
        return template

    def perform_template_matching(self, ref_gray, template_img, label=""):
        """
        Execute template matching algorithm on the images.
        
        Uses OpenCV's matchTemplate with TM_CCOEFF_NORMED method which provides
        normalized correlation coefficient values between 0 and 1.
        
        Args:
            ref_gray (numpy.ndarray): Grayscale reference image
            template_img (numpy.ndarray): Grayscale template image
            label (str): Label identifier for the template
            
        Returns:
            DetectionResult: Object containing match results
        """
        # Perform template matching using normalized correlation coefficient
        result = cv2.matchTemplate(ref_gray, template_img, cv2.TM_CCOEFF_NORMED)
        
        # Find the location of the best match
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        # Get template dimensions for bounding box calculation
        h, w = template_img.shape[:2]
        
        # Calculate bounding box coordinates
        top_left = max_loc
        bottom_right = (max_loc[0] + w, max_loc[1] + h)
        
        # Create structured result object
        detection_result = DetectionResult(
            label=label,
            score=max_val,
            top_left=top_left,
            bottom_right=bottom_right
        )
        
        self.logger.debug(f"Template matching result for '{label}': score={max_val:.4f}, location={top_left}")
        
        return detection_result

    def draw_detection_rectangle(self, image, detection_result):
        """
        Draw a detection rectangle and label on the image.
        
        This method annotates the image with a green rectangle around the detected
        region and adds a text label with the confidence score.
        
        Args:
            image (numpy.ndarray): Image to annotate
            detection_result (DetectionResult): Detection result object
            
        Returns:
            numpy.ndarray: Annotated image with detection rectangle and label
        """
        # Draw green rectangle around detected region
        cv2.rectangle(
            image, 
            detection_result.top_left, 
            detection_result.bottom_right, 
            self.config.DETECTION_COLOR,
            self.config.DETECTION_LINE_THICKNESS
        )
        
        # Create label text with score information
        label_text = f"{detection_result.label} ({detection_result.score:.2f})"
        
        # Calculate text position (slightly above the detection rectangle)
        text_x = detection_result.top_left[0]
        text_y = detection_result.top_left[1] - self.config.DETECTION_TEXT_OFFSET_Y
        
        # Ensure text stays within image bounds
        if text_y < self.config.DETECTION_TEXT_MIN_Y:
            text_y = detection_result.bottom_right[1] + self.config.DETECTION_TEXT_MIN_Y
        
        # Add text label to the image
        cv2.putText(
            image,
            label_text,
            (text_x, text_y),
            getattr(cv2, self.config.DETECTION_FONT),
            self.config.DETECTION_FONT_SCALE,
            self.config.DETECTION_COLOR,
            self.config.DETECTION_TEXT_THICKNESS
        )
        
        self.logger.debug(f"Drew detection rectangle for '{detection_result.label}' at {detection_result.top_left}")
        
        return image

    def prepare_reference_image(self, ref_img_path):
        """
        Load and prepare reference image for template matching.
        
        Args:
            ref_img_path (str): Path to the reference image file
            
        Returns:
            tuple: (color_image, grayscale_image) or (None, None) if loading fails
        """
        # Load the reference image in color
        ref_img = self.load_image(ref_img_path)
        if ref_img is None:
            return None, None
        
        # Convert reference image to grayscale for template matching
        ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
        
        return ref_img, ref_gray

    def prepare_template_image(self, template_path, ref_shape, label=None):
        """
        Load and prepare template image for template matching.
        
        Args:
            template_path (str): Path to the template image file
            ref_shape (tuple): Shape of reference image for resizing calculations
            label (str, optional): Label for the template
            
        Returns:
            tuple: (processed_template, label) or (None, None) if loading fails
        """
        # Load the template image in grayscale
        template = self.load_image(template_path, grayscale=True)
        if template is None:
            return None, None
        
        # Resize template if it's larger than the reference image
        template = self.resize_template_if_needed(template, ref_shape)
        
        # Generate label from filename if not provided
        if label is None:
            label = os.path.basename(template_path).split('.')[0]
        
        return template, label

    def save_annotated_image(self, image, output_path):
        """
        Save annotated image to the specified path.
        
        Args:
            image (numpy.ndarray): Image to save
            output_path (str): Path to save the image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            success = cv2.imwrite(output_path, image)
            if success:
                self.logger.info(f"Saved annotated image to: {output_path}")
                return True
            else:
                self.logger.error(f"Failed to save image to: {output_path}")
                return False
        except Exception as e:
            self.logger.error(f"Exception while saving image to {output_path}: {str(e)}")
            return False

    def validate_image_path(self, image_path):
        """
        Validate if the image path exists and has a supported extension.
        
        Args:
            image_path (str): Path to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not os.path.exists(image_path):
            self.logger.error(f"Image path does not exist: {image_path}")
            return False
        
        _, ext = os.path.splitext(image_path.lower())
        if ext not in self.config.SUPPORTED_IMAGE_EXTENSIONS:
            self.logger.error(f"Unsupported image extension: {ext}")
            return False
        
        return True
