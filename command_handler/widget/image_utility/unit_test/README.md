# Template Handler Unit Tests

This directory contains unit tests for the template handlers in the command_handler/widget/handler directory.

## Test Files

- **test_multi_template.py**: Tests for the MultiTemplateHandler class

## Running the Tests

You can run all tests using the provided `run_tests.py` script:

```bash
cd command_handler/widget/image_utility/unit_test
python run_tests.py
```

Or you can run a specific test file directly:

```bash
cd command_handler/widget/image_utility/unit_test
python test_multi_template.py
```

## Test Images

The tests automatically create test images in the `test_images` directory:

- **ref_img.png**: Reference image with a white square in the top-left corner
- **template1.png**: Template with a white square in the top-left corner (should be the best match)
- **template2.png**: Template with a white square in the bottom-right corner
- **template3.png**: Template with a white square in the center

## Test Output

The tests will create a temporary directory called `test_output` to store test artifacts. This directory is automatically cleaned up after the tests complete.

## Adding New Tests

To add new tests:

1. Create a new test file (e.g., `test_new_feature.py`)
2. Add test classes and methods following the unittest framework
3. Import the test class in `run_tests.py` and add it to the test suite
