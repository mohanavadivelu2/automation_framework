# Default USB Controller Configurations
USB_CONTROLLER_TYPE = "HARMAN" # Options: "ADB", "HARMAN"


# ADB Controller Configurations
USB_OFF_CMD = "echo 'simulateTx(06)4A000101' > /dev/ipcdebug"
USB_ON_CMD = "echo 'simulateTx(06)4A000202' > /dev/ipcdebug"

# Harman Controller Configurations
COMMAND_ENABLE_PORT_ID = 1
COMMAND_ENABLE_PORT_STATE = 1
COMMAND_ENABLE_PORT_ON_DURATION = 200  # ms
COMMAND_ENABLE_PORT_OFF_DURATION = 200  # ms

SERIAL_CONFIG = {
        "windows": {
            "baudrate": 9600,
            "timeout": 2,
            "write_timeout": 2,
            "inter_byte_timeout": 0.1
        },
        "darwin": {
            "baudrate": 9600,
            "timeout": 1,
            "write_timeout": 1
        },
        "linux": {
            "baudrate": 9600,
            "timeout": 1,
            "write_timeout": 1
        }
    }

DEVICE_PATTERNS = {
        "windows": {
            "port_pattern": "COM",
            "descriptions": [
            "Harman",
            "USB Serial",
            "CH340",
            "FTDI"
            ]
        },
        "darwin": {
            "port_patterns": [
                "usbmodem",
                "tty.usb"
            ],
            "descriptions": [
                "Harman",
                "IOUSBHostDevice",
                "USB Serial",
                "CH340",
                "FTDI"
            ]
        },
        "linux": {
            "port_patterns": [
                "ttyUSB",
                "ttyACM"
            ],
            "descriptions": [
                "Harman"
            ]
        }
    }

TIMING = {
    "device_init_delay": 2.0,
    "response_wait_delay": 0.5,
    "command_retry_count": 3,
    "retry_delay": 1.0
}

TROUBLESHOOTING_TIPS = {
    "windows": "Check if another application is using the COM port.",
    "darwin": "You might need to install USB drivers or check permissions.",
    "linux": "You might need to add your user to the 'dialout' group."
}
