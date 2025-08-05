import serial
import serial.tools.list_ports
import time
import platform
import logging
from utility.usb_controller.base_controller import BaseController
from utility.usb_controller import usb_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HarmanController(BaseController):
    """
    A class to manage interactions with a Harman USB matrix device.
    It handles device discovery, connection, and command execution in a structured,
    cross-platform manner.
    """
    def __init__(self, port=None):
        """
        Initializes the HarmanMatrix controller.
        Args:
            port (str, optional): The serial port to connect to. If None, it will be auto-detected.
        """
        self.port_name = port
        self.serial_connection = None
        self.platform = platform.system().lower()
        self.serial_config = usb_config.SERIAL_CONFIG.get(self.platform, usb_config.SERIAL_CONFIG["windows"])

    def __enter__(self):
        """Enter the runtime context related to this object."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and close the connection."""
        self.disconnect()

    def _find_device_port(self):
        """
        Finds the Harman device serial port by iterating through available ports
        and matching them against platform-specific patterns.
        """
        logging.info("Searching for Harman device...")
        ports = serial.tools.list_ports.comports()
        patterns = usb_config.DEVICE_PATTERNS.get(self.platform)

        if not patterns:
            raise RuntimeError(f"Unsupported platform: {self.platform.capitalize()}")

        for port in ports:
            # Check device path against defined patterns
            port_device_matches = any(p in port.device for p in patterns.get("port_patterns", [patterns.get("port_pattern")]))
            
            # Check description for matching keywords
            description_matches = any(desc.lower() in port.description.lower() for desc in patterns["descriptions"])

            if port_device_matches and description_matches:
                logging.info(f"Found Harman device: {port.device} - {port.description}")
                return port.device
        
        raise RuntimeError("Harman USB serial device not found.")

    def connect(self):
        """
        Establishes a serial connection to the Harman device.
        If the port is not specified, it will be auto-detected.
        """
        if self.serial_connection and self.serial_connection.is_open:
            logging.info("Serial connection is already open.")
            return

        if not self.port_name:
            self.port_name = self._find_device_port()

        logging.info(f"Opening serial connection to {self.port_name} on {self.platform.capitalize()}...")
        try:
            self.serial_connection = serial.Serial(port=self.port_name, **self.serial_config)
            time.sleep(usb_config.TIMING["device_init_delay"])
            logging.info("Serial connection established successfully.")
        except serial.SerialException as e:
            tip = usb_config.TROUBLESHOOTING_TIPS.get(self.platform, "Check device connection and permissions.")
            logging.error(f"Serial communication error: {e}. Tip: {tip}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred while connecting: {e}")
            raise

    def disconnect(self):
        """Closes the serial connection if it is open."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                logging.info("Serial connection closed.")
            except Exception as e:
                logging.warning(f"Error closing serial connection: {e}")
        self.serial_connection = None

    def _send_command(self, command, command_name):
        """
        Sends a command to the device and waits for a response.
        Retries the command if it fails.
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            raise RuntimeError("Serial connection is not open. Call connect() first.")

        for attempt in range(usb_config.TIMING["command_retry_count"]):
            try:
                self.serial_connection.write(command.encode())
                logging.info(f"Sent command ({command_name}): {command.strip()}")
                time.sleep(usb_config.TIMING["response_wait_delay"])
                
                response = self._read_response()
                if response:
                    logging.info(f"Received response: {response}")
                else:
                    logging.info("No response received.")
                return
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for command '{command_name}': {e}")
                if attempt < usb_config.TIMING["command_retry_count"] - 1:
                    time.sleep(usb_config.TIMING["retry_delay"])
                else:
                    logging.error(f"Failed to send command '{command_name}' after multiple retries.")
                    raise

    def _read_response(self):
        """Reads any available data from the serial buffer."""
        if self.serial_connection.in_waiting > 0:
            return self.serial_connection.read(self.serial_connection.in_waiting).decode(errors='ignore').strip()
        return None

    def get_enable_command(self):
        """Constructs the 'enable' command string."""
        return f"setusbport({usb_config.COMMAND_ENABLE_PORT_STATE}, {usb_config.COMMAND_ENABLE_PORT_ID}, {usb_config.COMMAND_ENABLE_PORT_ON_DURATION}, {usb_config.COMMAND_ENABLE_PORT_OFF_DURATION})\r"

    def get_disable_command(self):
        """Constructs the 'disable' command string."""
        return "setusbport(0, 0, 10, 10)\r"

    def enable_port(self):
        """Sends the command to enable the designated USB port."""
        try:
            self.connect()
            command = self.get_enable_command()
            self._send_command(command, "enable_port")
        finally:
            self.disconnect()

    def disable_port(self):
        """Sends the command to disable all USB ports."""
        try:
            self.connect()
            command = self.get_disable_command()
            self._send_command(command, "disable_ports")
        finally:
            self.disconnect()

    def reset_port(self, delay_between_commands=2.0):
        """
        Resets the USB port by disabling all ports and then enabling the target port.
        This is the default and most common operation.
        """
        try:
            self.connect()
            logging.info("Starting USB port reset sequence...")
            command = self.get_disable_command()
            self._send_command(command, "disable_ports")
            logging.info(f"Waiting for {delay_between_commands} seconds before enabling the port...")
            time.sleep(delay_between_commands)
            command = self.get_enable_command()
            self._send_command(command, "enable_port")
            logging.info("USB port reset sequence completed.")
        finally:
            self.disconnect()
