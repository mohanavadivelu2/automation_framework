"""
Unit tests for MultiTemplateHandler.

These tests verify that the MultiTemplateHandler correctly processes
commands with multiple template images.
"""

import os
import unittest
from unittest.mock import MagicMock, patch
import shutil
import sys
import cv2
import numpy as np

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from command_handler.widget.handler.multi_template import MultiTemplateHandler
from logger import LogManager


class TestMultiTemplateHandler(unittest.TestCase):
    """Test cases for MultiTemplateHandler."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        # Create a test output directory
        cls.test_output_dir = os.path.join(os.path.dirname(__file__), 'test_output')
        os.makedirs(cls.test_output_dir, exist_ok=True)
        
        # Create test images directory if it doesn't exist
        cls.test_images_dir = os.path.join(os.path.dirname(__file__), 'test_images')
        os.makedirs(cls.test_images_dir, exist_ok=True)
        
        # Create test images if they don't exist
        cls.create_test_images()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are done."""
        # Remove test output directory
        if os.path.exists(cls.test_output_dir):
            shutil.rmtree(cls.test_output_dir)

    @classmethod
    def create_test_images(cls):
        """Create test images for testing."""
        # Create reference image (black background with white square in top-left)
        ref_img = np.zeros((100, 100, 3), dtype=np.uint8)
        ref_img[10:30, 10:30] = [255, 255, 255]  # White square in top-left
        cv2.imwrite(os.path.join(cls.test_images_dir, 'ref_img.png'), ref_img)
        
        # Create template1 (white square in top-left)
        template1 = np.zeros((30, 30, 3), dtype=np.uint8)
        template1[0:20, 0:20] = [255, 255, 255]  # White square
        cv2.imwrite(os.path.join(cls.test_images_dir, 'template1.png'), template1)
        
        # Create template2 (white square in bottom-right)
        template2 = np.zeros((30, 30, 3), dtype=np.uint8)
        template2[10:30, 10:30] = [255, 255, 255]  # White square
        cv2.imwrite(os.path.join(cls.test_images_dir, 'template2.png'), template2)
        
        # Create template3 (white square in center)
        template3 = np.zeros((30, 30, 3), dtype=np.uint8)
        template3[5:25, 5:25] = [255, 255, 255]  # White square
        cv2.imwrite(os.path.join(cls.test_images_dir, 'template3.png'), template3)

    def setUp(self):
        """Set up before each test."""
        # Mock logger
        self.mock_logger = MagicMock()
        
        # Mock LogManager
        patcher = patch('logger.LogManager')
        self.addCleanup(patcher.stop)
        self.mock_log_manager = patcher.start()
        self.mock_log_manager.get_instance.return_value.get_test_case_logger.return_value = self.mock_logger
        self.mock_log_manager.get_instance.return_value.get_log_dir.return_value = self.test_output_dir
        
        # Mock driver
        self.mock_driver = MagicMock()
        
        # Create a test screenshot (copy of ref_img)
        ref_img_path = os.path.join(self.test_images_dir, 'ref_img.png')
        with open(ref_img_path, 'rb') as f:
            self.mock_driver.get_screenshot_as_png.return_value = f.read()
        
        # Mock WidgetUtils
        patcher = patch('command_handler.widget.widget_utils.WidgetUtils')
        self.addCleanup(patcher.stop)
        self.mock_widget_utils = patcher.start()
        self.mock_widget_utils.validate_required_fields.return_value = (True, "")
        self.mock_widget_utils.get_driver.return_value = (True, self.mock_driver)
        
        # Mock IMAGES_PATH
        patcher = patch('command_handler.widget.handler.multi_template.IMAGES_PATH', self.test_images_dir)
        self.addCleanup(patcher.stop)
        patcher.start()
        
        # Create handler
        self.handler = MultiTemplateHandler()

    def test_multi_template_detection(self):
        """Test MultiTemplateHandler with multiple templates."""
        # Prepare command data
        command_data = {
            "base_path": "test_app",
            "image_one": "template1.png",
            "image_two": "template2.png",
            "image_three": "template3.png",
            "ref_img_name": "test_ref.png",
            "output_name": "test_output.png"
        }
        
        # Execute handler
        success, message = self.handler.processCommand(command_data)
        
        # Assertions
        self.assertTrue(success)
        self.assertIn("TEMPLATE_", message)
        self.assertTrue(os.path.exists(os.path.join(self.test_output_dir, "test_output.png")))

    # Note: We keep the detect parameter functionality in the handler for backward compatibility,
    # but we don't test it specifically since it's not a required feature.

    def test_multi_template_no_images(self):
        """Test MultiTemplateHandler with no template images."""
        # Prepare command data with no image_* parameters
        command_data = {
            "base_path": "test_app",
            "ref_img_name": "test_ref.png"
        }
        
        # Execute handler
        success, message = self.handler.processCommand(command_data)
        
        # Assertions
        self.assertFalse(success)
        self.assertIn("ERROR", message)


if __name__ == '__main__':
    unittest.main()
