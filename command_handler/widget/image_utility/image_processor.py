"""
Image processing utilities for widget handlers.
This module provides functions for template matching, image comparison,
and other image processing operations.
"""

import os
import cv2
import numpy as np
from logger import LogManager

def load_images(ref_path, template_paths):
    """
    Load and prepare images for processing.
    
    Args:
        ref_path (str): Path to the reference image
        template_paths (list or str): Path(s) to the template image(s)
            
    Returns:
        tuple: (ref_img, ref_gray, template_images)
            where template_images is a list of grayscale template images
    """
    ref_img = cv2.imread(ref_path)
    ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    
    # Handle both single template and multiple templates
    if isinstance(template_paths, str):
        template_paths = [template_paths]
    
    template_images = []
    for path in template_paths:
        template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if template is not None:
            template_images.append(template)
    
    return ref_img, ref_gray, template_images

def resize_template(template, ref_shape):
    """
    Resize template if it's larger than the reference image.
    
    Args:
        template: The template image
        ref_shape: Shape of the reference image
            
    Returns:
        The resized template
    """
    h_ref, w_ref = ref_shape
    h_temp, w_temp = template.shape
    if h_temp > h_ref or w_temp > w_ref:
        scale = min(h_ref / h_temp, w_ref / w_temp, 0.5)
        template = cv2.resize(template, (int(w_temp * scale), int(h_temp * scale)))
    return template

def match_template(template_img, ref_gray, label=""):
    """
    Match a template in the reference image.
    
    Args:
        template_img: The template image
        ref_gray: The grayscale reference image
        label: Label for the template (default: "")
            
    Returns:
        dict: Match information including score and location
    """
    result = cv2.matchTemplate(ref_gray, template_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    h, w = template_img.shape
    return {
        "label": label,
        "score": max_val,
        "top_left": max_loc,
        "bottom_right": (max_loc[0] + w, max_loc[1] + h)
    }

def draw_detection_rectangle(image, match_info):
    """
    Draw a rectangle around the detected area.
    
    Args:
        image: The image to draw on
        match_info: Match information
            
    Returns:
        The annotated image
    """
    cv2.rectangle(image, match_info["top_left"], match_info["bottom_right"], (0, 255, 0), 2)
    label_text = match_info['label']
    if match_info['score'] is not None:
        label_text += f" ({match_info['score']:.2f})"
    
    cv2.putText(
        image,
        label_text,
        (match_info["top_left"][0], match_info["top_left"][1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
        (0, 255, 0), 2
    )
    return image

def detect_multi_template(ref_img_path, template_paths_dict, output_path=None):
    """
    Detect which of multiple templates best matches a reference image.
    
    Args:
        ref_img_path (str): Path to the reference image
        template_paths_dict (dict): Dictionary mapping template labels to template paths
            e.g. {"image_one": "path/to/template1.png", "image_two": "path/to/template2.png"}
        output_path (str, optional): Path to save the annotated image
            
    Returns:
        tuple: (result_message, detected_state)
    """
    # Reduce threading issue on some systems
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    
    if not template_paths_dict:
        return "ERROR: No template images provided", None
    
    # Load reference image
    ref_img = cv2.imread(ref_img_path)
    if ref_img is None:
        return "ERROR: Failed to load reference image", None
    
    ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    
    # Process each template
    matches = []
    for label, template_path in template_paths_dict.items():
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            continue
        
        template = resize_template(template, ref_gray.shape)
        match_info = match_template(template, ref_gray, label)
        matches.append(match_info)
    
    if not matches:
        return "ERROR: Failed to load any template images", None
    
    # Find the best match
    best_match = max(matches, key=lambda x: x["score"])
    detected_state = best_match["label"]
    
    if output_path:
        annotated_img = draw_detection_rectangle(ref_img.copy(), best_match)
        cv2.imwrite(output_path, annotated_img)
        result_message = f"TEMPLATE_{detected_state}_DETECTED (Score: {best_match['score']:.2f}, Image: {output_path})"
    else:
        result_message = f"TEMPLATE_{detected_state}_DETECTED (Score: {best_match['score']:.2f})"
    
    return result_message, detected_state

def detect_double_template(ref_img_path, template1_path, template2_path, output_path=None, label1="image_one", label2="image_two"):
    """
    Detect which of two templates better matches a reference image.
    
    Args:
        ref_img_path (str): Path to the reference image
        template1_path (str): Path to the first template
        template2_path (str): Path to the second template
        output_path (str, optional): Path to save the annotated image
        label1 (str, optional): Label for the first template (default: "image_one")
        label2 (str, optional): Label for the second template (default: "image_two")
            
    Returns:
        tuple: (result_message, detected_state)
    """
    # Use the more general multi-template function
    template_paths_dict = {
        label1: template1_path,
        label2: template2_path
    }
    return detect_multi_template(ref_img_path, template_paths_dict, output_path)

def detect_single_template(ref_img_path, template_path, output_path=None, threshold=0.7, label=None):
    """
    Detect if a template matches a reference image.
    
    Args:
        ref_img_path (str): Path to the reference image
        template_path (str): Path to the template
        output_path (str, optional): Path to save the annotated image
        threshold (float, optional): Minimum score to consider a match (0.0-1.0)
        label (str, optional): Label for the template
            
    Returns:
        tuple: (result_message, is_detected, match_info)
    """
    # Reduce threading issue on some systems
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    
    ref_img, ref_gray, templates = load_images(ref_img_path, template_path)
    
    if not templates:
        return "ERROR: Failed to load template image", False, None
    
    template = templates[0]
    template = resize_template(template, ref_gray.shape)
    
    # Use filename as label if not provided
    if label is None:
        label = os.path.basename(template_path).split('.')[0]
    
    match_info = match_template(template, ref_gray, label)
    is_detected = match_info["score"] >= threshold
    
    status = "DETECTED" if is_detected else "NOT_DETECTED"
    
    if output_path and is_detected:
        annotated_img = draw_detection_rectangle(ref_img.copy(), match_info)
        cv2.imwrite(output_path, annotated_img)
        result_message = f"TEMPLATE_{status} (Score: {match_info['score']:.2f}, Image: {output_path})"
    else:
        result_message = f"TEMPLATE_{status} (Score: {match_info['score']:.2f})"
    
    return result_message, is_detected, match_info
