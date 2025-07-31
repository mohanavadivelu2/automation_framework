import os
import sys
import cv2
import numpy as np

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


# --- Copied functions from command_handler.widget.image_utility.image_processor ---

def load_images(ref_path, template_paths):
    """
    Load and prepare images for processing.
    """
    ref_img = cv2.imread(ref_path)
    ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    
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

def detect_single_template(ref_img_path, template_path, output_path=None, threshold=0.7, label=None):
    """
    Detect if a template matches a reference image.
    """
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    
    ref_img, ref_gray, templates = load_images(ref_img_path, template_path)
    
    if not templates:
        return "ERROR: Failed to load template image", False, None
    
    template = templates[0]
    template = resize_template(template, ref_gray.shape)
    
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

# --- End of copied functions ---


def find_template_in_image(reference_image_path: str, template_image_path: str, output_image_path: str, threshold: float = 0.7):
    """
    Finds a template image within a reference image and highlights the matching area.
    """
    output_dir = os.path.dirname(output_image_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"Reference Image: {reference_image_path}")
    print(f"Template Image: {template_image_path}")
    print(f"Output Image: {output_image_path}")
    print(f"Threshold: {threshold}")

    result, is_detected, match_info = detect_single_template(
        reference_image_path,
        template_image_path,
        output_image_path,
        threshold,
        label="TestTemplate"
    )

    print(f"Detection Result: {result}")
    print(f"Is Detected: {is_detected}")
    if match_info:
        print(f"Match Score: {match_info.get('score', 'N/A'):.2f}")

    return result, is_detected, match_info

if __name__ == '__main__':
    # Define paths for local images within the test_handler directory
    script_dir = os.path.dirname(__file__)
    reference_img_path = os.path.join(script_dir, "reference-iphone12-720.png")
    template_img_path = os.path.join(script_dir, "template.png")
    output_img_path = os.path.join(script_dir, "test_output-iphone12-720.png")

    print(f"Running single template detection utility...")
    print(f"Reference: {reference_img_path}")
    print(f"Template: {template_img_path}")
    print(f"Output: {output_img_path}")

    if not os.path.exists(reference_img_path):
        print(f"Error: Reference image not found at {reference_img_path}")
        sys.exit(1)
    if not os.path.exists(template_img_path):
        print(f"Error: Template image not found at {template_img_path}")
        sys.exit(1)

    find_template_in_image(
        reference_image_path=reference_img_path,
        template_image_path=template_img_path,
        output_image_path=output_img_path,
        threshold=0.7
    )

    print(f"Detection complete. Check the output image at: {output_img_path}")
