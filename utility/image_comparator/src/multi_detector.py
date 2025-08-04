"""
Multi-Template Detection Module

This module provides functionality for detecting the best matching template from
multiple candidates. It handles state detection scenarios where you need to determine
which of several possible states a UI element is currently in.
"""

from .core_matcher import CoreMatcher
from .config import ImageComparatorConfig
from .logging_utils import get_logger


class MultiDetector:
    """
    Class for multi-template detection operations.
    
    This class provides functionality to compare multiple templates against a
    reference image and determine which template has the best match. Useful
    for state detection scenarios.
    """

    def __init__(self, logger=None):
        """
        Initialize the MultiDetector instance.
        
        Args:
            logger: Optional logger instance. If None, creates a new logger.
        """
        self.logger = logger or get_logger()
        self.core_matcher = CoreMatcher(logger=self.logger)
        
        self.logger.info("MultiDetector initialized successfully")

    def detect_best_match(self, ref_img_path, template_paths_dict, output_path=None):
        """
        API method to find the best matching template from multiple candidates.
        
        This method compares multiple templates against a reference image and
        returns the template with the highest confidence score.
        
        Args:
            ref_img_path (str): Path to the reference image file
            template_paths_dict (dict): Dictionary mapping labels to template paths
                Example: {"button_on": "path/to/on.png", "button_off": "path/to/off.png"}
            output_path (str, optional): Path to save annotated output image
            
        Returns:
            tuple: (result_message, detected_state)
                - result_message (str): Human-readable result description
                - detected_state (str): Label of the best matching template
        """
        self.logger.info(f"Starting multi-template detection with {len(template_paths_dict)} templates")
        
        # Validate input parameters
        if not template_paths_dict:
            error_msg = "ERROR: No template images provided"
            self.logger.error(error_msg)
            return error_msg, None
        
        # Validate reference image path
        if not self.core_matcher.validate_image_path(ref_img_path):
            error_msg = f"ERROR: Invalid reference image path: {ref_img_path}"
            self.logger.error(error_msg)
            return error_msg, None
        
        # Load and prepare reference image
        ref_img, ref_gray = self.core_matcher.prepare_reference_image(ref_img_path)
        if ref_img is None:
            error_msg = f"ERROR: Failed to load reference image: {ref_img_path}"
            self.logger.error(error_msg)
            return error_msg, None
        
        # Process each template and collect match results
        detection_results = []
        for label, template_path in template_paths_dict.items():
            self.logger.debug(f"Processing template: {label} ({template_path})")
            
            # Validate template path
            if not self.core_matcher.validate_image_path(template_path):
                self.logger.warning(f"Skipping template '{label}': invalid path")
                continue
            
            # Load and prepare template image
            template, template_label = self.core_matcher.prepare_template_image(
                template_path, ref_gray.shape, label
            )
            if template is None:
                self.logger.warning(f"Skipping template '{label}': failed to load")
                continue
            
            # Perform template matching
            detection_result = self.core_matcher.perform_template_matching(
                ref_gray, template, template_label
            )
            detection_results.append(detection_result)
        
        # Check if any templates were successfully processed
        if not detection_results:
            error_msg = "ERROR: Failed to load any template images"
            self.logger.error(error_msg)
            return error_msg, None
        
        # Find the template with the highest matching score
        best_match = max(detection_results, key=lambda x: x.score)
        detected_state = best_match.label
        
        # Create result message
        result_message = f"TEMPLATE_{detected_state}_DETECTED (Score: {best_match.score:.2f})"
        
        # Save annotated image if output path is provided
        if output_path:
            try:
                annotated_img = self.core_matcher.draw_detection_rectangle(
                    ref_img.copy(), best_match
                )
                if self.core_matcher.save_annotated_image(annotated_img, output_path):
                    result_message += f", Image: {output_path}"
            except Exception as e:
                self.logger.error(f"Failed to save output image: {str(e)}")
        
        self.logger.info(f"Multi-template detection completed. Best match: {detected_state} (score: {best_match.score:.2f})")
        
        return result_message, detected_state

    def detect_with_confidence_ranking(self, ref_img_path, template_paths_dict, top_n=None):
        """
        Detect and rank all templates by confidence score.
        
        This method processes all templates and returns them ranked by confidence,
        useful for understanding the relative quality of all matches.
        
        Args:
            ref_img_path (str): Path to the reference image file
            template_paths_dict (dict): Dictionary mapping labels to template paths
            top_n (int, optional): Return only top N results. None returns all.
            
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether processing succeeded
                - best_match (str): Label of best matching template
                - rankings (list): List of results sorted by confidence score
                - total_processed (int): Number of templates successfully processed
        """
        self.logger.info(f"Starting confidence ranking for {len(template_paths_dict)} templates")
        
        # Validate input parameters
        if not template_paths_dict:
            return {
                "success": False,
                "error": "No template images provided",
                "best_match": None,
                "rankings": [],
                "total_processed": 0
            }
        
        # Load and prepare reference image
        ref_img, ref_gray = self.core_matcher.prepare_reference_image(ref_img_path)
        if ref_img is None:
            return {
                "success": False,
                "error": f"Failed to load reference image: {ref_img_path}",
                "best_match": None,
                "rankings": [],
                "total_processed": 0
            }
        
        # Process all templates
        detection_results = []
        for label, template_path in template_paths_dict.items():
            template, template_label = self.core_matcher.prepare_template_image(
                template_path, ref_gray.shape, label
            )
            if template is None:
                self.logger.warning(f"Skipping template '{label}': failed to load")
                continue
            
            detection_result = self.core_matcher.perform_template_matching(
                ref_gray, template, template_label
            )
            detection_results.append(detection_result)
        
        if not detection_results:
            return {
                "success": False,
                "error": "Failed to load any template images",
                "best_match": None,
                "rankings": [],
                "total_processed": 0
            }
        
        # Sort results by confidence score (highest first)
        detection_results.sort(key=lambda x: x.score, reverse=True)
        
        # Limit results if requested
        if top_n is not None:
            detection_results = detection_results[:top_n]
        
        # Convert to serializable format
        rankings = [
            {
                "label": result.label,
                "score": result.score,
                "top_left": result.top_left,
                "bottom_right": result.bottom_right,
                "rank": i + 1
            }
            for i, result in enumerate(detection_results)
        ]
        
        return {
            "success": True,
            "best_match": detection_results[0].label,
            "rankings": rankings,
            "total_processed": len(detection_results)
        }

    def detect_above_threshold(self, ref_img_path, template_paths_dict, threshold=None):
        """
        Detect all templates that meet or exceed the specified threshold.
        
        This method is useful when you want to find all possible matches above
        a certain confidence level, not just the best match.
        
        Args:
            ref_img_path (str): Path to the reference image file
            template_paths_dict (dict): Dictionary mapping labels to template paths
            threshold (float, optional): Minimum confidence threshold. Uses default if None.
            
        Returns:
            dict: Dictionary containing:
                - success (bool): Whether processing succeeded
                - detected_templates (list): List of templates above threshold
                - all_results (list): All processing results for reference
                - threshold_used (float): The threshold value used
        """
        detection_threshold = threshold or ImageComparatorConfig.DEFAULT_THRESHOLD
        
        self.logger.info(f"Detecting templates above threshold {detection_threshold}")
        
        # Get confidence rankings for all templates
        ranking_result = self.detect_with_confidence_ranking(ref_img_path, template_paths_dict)
        
        if not ranking_result["success"]:
            return {
                "success": False,
                "error": ranking_result.get("error", "Unknown error"),
                "detected_templates": [],
                "all_results": [],
                "threshold_used": detection_threshold
            }
        
        # Filter results by threshold
        detected_templates = [
            result for result in ranking_result["rankings"]
            if result["score"] >= detection_threshold
        ]
        
        return {
            "success": True,
            "detected_templates": detected_templates,
            "all_results": ranking_result["rankings"],
            "threshold_used": detection_threshold
        }

    def get_match_statistics(self, ref_img_path, template_paths_dict):
        """
        API method to get detailed statistics for all template matches.
        
        This method provides comprehensive matching statistics without generating
        output images, useful for analysis and debugging purposes.
        
        Args:
            ref_img_path (str): Path to the reference image file
            template_paths_dict (dict): Dictionary mapping labels to template paths
            
        Returns:
            dict: Dictionary containing detailed statistics for all matches
        """
        self.logger.info(f"Generating match statistics for {len(template_paths_dict)} templates")
        
        # Load and validate reference image
        ref_img, ref_gray = self.core_matcher.prepare_reference_image(ref_img_path)
        if ref_img is None:
            return {"error": f"Failed to load reference image: {ref_img_path}"}
        
        # Collect statistics for all templates
        statistics = {
            "reference_image": ref_img_path,
            "reference_dimensions": ref_gray.shape,
            "total_templates": len(template_paths_dict),
            "successful_matches": 0,
            "failed_loads": 0,
            "template_results": []
        }
        
        for label, template_path in template_paths_dict.items():
            template = self.core_matcher.load_image(template_path, grayscale=True)
            
            if template is None:
                statistics["failed_loads"] += 1
                continue
            
            # Get original template dimensions before resizing
            original_dims = template.shape
            
            # Resize if needed and get final dimensions
            template = self.core_matcher.resize_template_if_needed(template, ref_gray.shape)
            final_dims = template.shape
            
            # Perform matching
            detection_result = self.core_matcher.perform_template_matching(ref_gray, template, label)
            
            # Compile template statistics
            template_stats = {
                "label": label,
                "template_path": template_path,
                "original_dimensions": original_dims,
                "final_dimensions": final_dims,
                "was_resized": original_dims != final_dims,
                "match_score": detection_result.score,
                "match_location": detection_result.top_left,
                "bounding_box": {
                    "top_left": detection_result.top_left,
                    "bottom_right": detection_result.bottom_right
                }
            }
            
            statistics["template_results"].append(template_stats)
            statistics["successful_matches"] += 1
        
        # Add summary statistics
        if statistics["successful_matches"] > 0:
            scores = [t["match_score"] for t in statistics["template_results"]]
            statistics["score_statistics"] = {
                "min_score": min(scores),
                "max_score": max(scores),
                "average_score": sum(scores) / len(scores),
                "best_match_label": max(statistics["template_results"], key=lambda x: x["match_score"])["label"]
            }
        
        self.logger.info(f"Match statistics generated: {statistics['successful_matches']} successful, {statistics['failed_loads']} failed")
        
        return statistics

    def compare_templates_pairwise(self, ref_img_path, template_paths_dict):
        """
        Compare templates and provide pairwise confidence differences.
        
        This method helps analyze how distinct different templates are when
        matched against the same reference image.
        
        Args:
            ref_img_path (str): Path to the reference image file
            template_paths_dict (dict): Dictionary mapping labels to template paths
            
        Returns:
            dict: Dictionary containing pairwise comparison results
        """
        ranking_result = self.detect_with_confidence_ranking(ref_img_path, template_paths_dict)
        
        if not ranking_result["success"]:
            return {
                "success": False,
                "error": ranking_result.get("error", "Unknown error")
            }
        
        rankings = ranking_result["rankings"]
        comparisons = []
        
        # Generate pairwise comparisons
        for i in range(len(rankings)):
            for j in range(i + 1, len(rankings)):
                template1 = rankings[i]
                template2 = rankings[j]
                
                comparison = {
                    "template1": template1["label"],
                    "template2": template2["label"],
                    "score1": template1["score"],
                    "score2": template2["score"],
                    "score_difference": template1["score"] - template2["score"],
                    "confidence_gap": abs(template1["score"] - template2["score"])
                }
                comparisons.append(comparison)
        
        # Sort by confidence gap (largest differences first)
        comparisons.sort(key=lambda x: x["confidence_gap"], reverse=True)
        
        return {
            "success": True,
            "pairwise_comparisons": comparisons,
            "total_comparisons": len(comparisons),
            "best_match": rankings[0]["label"] if rankings else None
        }
