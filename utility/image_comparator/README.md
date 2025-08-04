# Image Comparator Module

A modular image comparison and template matching library designed for automated testing and image analysis. This module provides specialized classes for single template detection, multi-template matching, and core OpenCV operations with context-aware logging.

## Architecture Overview

The module follows a focused, modular design with three specialized classes:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CoreMatcher   │    │ SingleDetector   │    │ MultiDetector   │
│                 │    │                  │    │                 │
│ Low-level       │    │ 1:1 Template     │    │ Best Match      │
│ OpenCV          │◄───┤ Detection        │    │ from Multiple   │
│ Operations      │    │                  │    │ Templates       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Class Responsibilities

- **CoreMatcher**: Fundamental OpenCV operations (image loading, resizing, matching, annotation)
- **SingleDetector**: Specialized for detecting a single template in a reference image
- **MultiDetector**: Specialized for finding the best match among multiple template candidates

## Image Processing Flow

### Single Template Detection Flow

```
Reference Image ──┐
                  │
Template Image ───┼─► [Load & Validate] ──► [Convert to Grayscale] ──► [Resize Template if Needed]
                  │
                  └─► [OpenCV Template Matching (TM_CCOEFF_NORMED)] ──► [Threshold Check]
                      │
                      ├─► DETECTED ──► [Annotate & Save Output] ──► Result
                      │
                      └─► NOT_DETECTED ──► Result
```

**Detailed Steps:**

1. **Input Validation**
   - Validate file paths exist
   - Check supported image formats (.png, .jpg, .jpeg, .bmp, .tiff, .tif)

2. **Image Loading**
   - Load reference image in color (for annotation)
   - Convert reference to grayscale (for matching)
   - Load template image in grayscale

3. **Template Preprocessing**
   - Check if template is larger than reference image
   - Resize template if needed (max scale: 50% of reference dimensions)
   - Maintain aspect ratio during resizing

4. **Template Matching**
   - Use OpenCV's `matchTemplate` with `TM_CCOEFF_NORMED` method
   - Returns normalized correlation coefficient (0.0 to 1.0)
   - Find location of best match using `minMaxLoc`

5. **Threshold Decision**
   - Compare match score against threshold (default: 0.7)
   - Return detection status and confidence score
   - Generate human-readable result message

6. **Output Generation** (if detected and output path provided)
   - Draw green rectangle around detected region
   - Add label with confidence score
   - Save annotated image

### Multi-Template Detection Flow

```
Reference Image ──┐
                  │
Template 1 ───────┤
Template 2 ───────┼─► [Process Each Template] ──► [Collect All Scores] ──► [Find Best Match]
Template N ───────┤     │                         │                        │
                  │     └─► Single Detection ──► Score                    │
                  │            Flow                                        │
                  └─────────────────────────────────────────────────────► Best Template + Score
```

**Detailed Steps:**

1. **Batch Processing Setup**
   - Validate reference image once
   - Iterate through all template candidates
   - Collect results from each template matching operation

2. **Individual Template Processing**
   - Apply single template detection flow to each template
   - Store match score and location for each template

3. **Best Match Selection**
   - Compare all collected scores
   - Select template with highest confidence score
   - Return best match label and detailed statistics

4. **Advanced Features**
   - Confidence ranking: Sort all matches by score
   - Threshold filtering: Return only matches above specified threshold
   - Pairwise comparison: Analyze confidence differences between templates

### Core OpenCV Operations Flow

```
Image Path ──► [Path Validation] ──► [cv2.imread] ──► [Error Handling] ──► Loaded Image
                      │                    │                  │
                      ├─► File exists?     ├─► Success?       ├─► None if failed
                      └─► Format support?  └─► Shape check    └─► numpy.ndarray if success

Template Matching:
Reference (Gray) ──┐
                   ├─► [cv2.matchTemplate] ──► [cv2.minMaxLoc] ──► Match Result
Template (Gray) ───┘      │                        │                   │
                          └─► TM_CCOEFF_NORMED     └─► Best location   └─► Score + Coordinates

Annotation:
Image + Match Info ──► [cv2.rectangle] ──► [cv2.putText] ──► [cv2.imwrite] ──► Annotated Output
```

## Usage Examples

### Basic Single Template Detection

```python
from utility.image_comparator import SingleDetector

# Initialize detector
detector = SingleDetector(threshold=0.8)

# Detect template in reference image
result_msg, is_detected, detection_result = detector.detect_single_template(
    ref_img_path="screenshots/current_screen.png",
    template_path="templates/login_button.png",
    output_path="output/detection_result.png"
)

print(f"Detection: {result_msg}")
print(f"Detected: {is_detected}")
if detection_result:
    print(f"Score: {detection_result.score:.4f}")
    print(f"Location: {detection_result.top_left}")
```

### Multi-Template State Detection

```python
from utility.image_comparator import MultiDetector

# Initialize multi-detector
multi_detector = MultiDetector()

# Define state templates
templates = {
    "button_enabled": "templates/button_on.png",
    "button_disabled": "templates/button_off.png",
    "button_loading": "templates/button_loading.png"
}

# Detect current state
result_msg, detected_state = multi_detector.detect_best_match(
    ref_img_path="screenshots/current_ui.png",
    template_paths_dict=templates,
    output_path="output/state_detection.png"
)

print(f"Current state: {detected_state}")
print(f"Result: {result_msg}")
```

### Advanced Multi-Template Analysis

```python
# Get confidence rankings for all templates
rankings = multi_detector.detect_with_confidence_ranking(
    ref_img_path="screenshots/current_ui.png",
    template_paths_dict=templates,
    top_n=3
)

print("Confidence Rankings:")
for result in rankings["rankings"]:
    print(f"  {result['label']}: {result['score']:.4f} (Rank {result['rank']})")

# Get detailed statistics
stats = multi_detector.get_match_statistics(
    ref_img_path="screenshots/current_ui.png",
    template_paths_dict=templates
)

print(f"Best match: {stats['score_statistics']['best_match_label']}")
print(f"Score range: {stats['score_statistics']['min_score']:.4f} - {stats['score_statistics']['max_score']:.4f}")
```

### Core Operations (Low-Level Access)

```python
from utility.image_comparator import CoreMatcher

# Initialize core matcher
core = CoreMatcher()

# Prepare images
ref_img, ref_gray = core.prepare_reference_image("reference.png")
template, label = core.prepare_template_image("template.png", ref_gray.shape)

# Perform matching
detection_result = core.perform_template_matching(ref_gray, template, label)

# Annotate result
annotated_img = core.draw_detection_rectangle(ref_img.copy(), detection_result)
core.save_annotated_image(annotated_img, "output.png")
```

## Configuration

### Default Settings

- **Detection Threshold**: 0.7 (70% confidence)
- **Max Template Scale**: 0.5 (50% of reference image dimensions)
- **Template Matching Method**: TM_CCOEFF_NORMED
- **Detection Color**: Green (0, 255, 0) in BGR format
- **Supported Formats**: .png, .jpg, .jpeg, .bmp, .tiff, .tif

### Customizing Settings

```python
from utility.image_comparator import ImageComparatorConfig

# View current configuration
config = ImageComparatorConfig()
print(f"Default threshold: {config.DEFAULT_THRESHOLD}")
print(f"Max template scale: {config.MAX_TEMPLATE_SCALE}")

# Create detector with custom threshold
detector = SingleDetector(threshold=0.9)  # 90% confidence required

# Runtime threshold adjustment
detector.set_threshold(0.6)  # Lower to 60% confidence
current_threshold = detector.get_threshold()
```

## Context-Aware Logging

The module automatically routes logging based on the calling context:

### Unit Test Context
- **Behavior**: Always logs to console
- **Detection**: Automatically detects calls from `unit_test` folder paths
- **Format**: Simple console output (DEBUG:, INFO:, WARNING:, ERROR:)

### Source Code Context  
- **Behavior**: Uses LogManager for application logging
- **Integration**: Logs through `LogManager.get_instance().get_application_logger()`
- **Fallback**: Falls back to console if LogManager is unavailable

```python
# Logging is automatic - no manual configuration needed
detector = SingleDetector()  # Logging will be routed appropriately

# In unit tests: console logging
# In application: LogManager integration
```

## Error Handling

### Common Error Scenarios

1. **Invalid Image Paths**
   ```python
   result_msg, is_detected, detection_result = detector.detect_single_template(
       "nonexistent.png", "template.png"
   )
   # Returns: ("ERROR: Invalid reference image path: nonexistent.png", False, None)
   ```

2. **Unsupported Image Formats**
   ```python
   # .gif files are not supported
   result_msg, is_detected, detection_result = detector.detect_single_template(
       "image.gif", "template.png"
   )
   # Returns error message about unsupported format
   ```

3. **Image Loading Failures**
   ```python
   # Corrupted or invalid image files
   # Returns error message with details about loading failure
   ```

4. **Template Too Large**
   ```python
   # Template larger than reference image will be automatically resized
   # Warning logged about resize operation
   ```

## Performance Considerations

### Optimization Features

1. **OpenBLAS Thread Limiting**: Reduces threading conflicts
2. **Efficient Template Resizing**: Only resizes when necessary
3. **Grayscale Processing**: Uses grayscale for matching operations
4. **Memory Management**: Proper cleanup of OpenCV objects

### Best Practices

- Use appropriate image sizes (avoid unnecessarily large images)
- Choose optimal thresholds for your use case
- Batch similar operations when possible
- Consider template size relative to reference images

## Dependencies

### Required Packages

- **OpenCV**: `cv2` for image processing operations
- **NumPy**: `numpy` for array operations
- **Logger**: Custom logging system integration

### Installation

```bash
pip install opencv-python numpy
```

## Module Information

- **Version**: 2.1.0
- **Author**: Automation Framework Team
- **Description**: Modular image comparison and template matching library

## API Reference

### Factory Functions

```python
from utility.image_comparator import create_single_detector, create_multi_detector

# Create instances with factory functions
single_detector = create_single_detector(threshold=0.8)
multi_detector = create_multi_detector()
```

### Utility Functions

```python
from utility.image_comparator import get_version, get_supported_formats, get_default_config

print(f"Version: {get_version()}")
print(f"Supported formats: {get_supported_formats()}")
print(f"Default config: {get_default_config()}")
```

This comprehensive documentation covers all aspects of the Image Comparator module, from basic usage to advanced features and internal processing flows.
