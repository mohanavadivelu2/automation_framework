import subprocess
import os
import signal
import time
from datetime import datetime
from server_manager.server_base import AppiumServerBase

class UnixAppiumServer(AppiumServerBase):
    """
    Handles Appium server management for macOS and Linux.
    """
    
    def start_appium_server(self, port, base_path):
        """
        Initialize and start an Appium server instance on the specified port and base path.
        
        Args:
            port (int): The port on which the Appium server will run.
            base_path (str): The base path for the Appium server.
        
        Returns:
            bool: True if the server starts successfully, False otherwise.
        """
        try:
            timestamp = datetime.now().strftime("%d%m%y_%H%M%S")
            log_dir = self.log_folder
            os.makedirs(log_dir, exist_ok=True)

            log_file = f"{log_dir}/appium_{timestamp}_{port}_{base_path}.log"
            command = ['appium', '-a', self.ip_address, '-p', str(port), '--base-path', base_path, '--log-level', 'debug']
            self.alog.d(f"Executing command: {' '.join(command)}")

            server_process = subprocess.Popen(
                command,
                stdout=open(log_file, 'w'),
                stderr=subprocess.STDOUT,
            )
            self.server_process_list[base_path] = server_process
            
            time.sleep(5)
            url = f"http://{self.ip_address}:{port}/{base_path}"
            self.urls[base_path] = url
            self.alog.d(f"Appium server started at {url}")
            
            return True
        except Exception as e:
            self.alog.e(f"Error starting Appium server on port {port}: {e}")
            return False

    def force_deinit_appium_server(self):
        """
        Forcefully terminate the Appium server using the specified port.
        If the port is not busy, fallback to killing all 'node' processes.
        """
        try:
            # Check for processes on common Appium ports
            port = 4723  # Default Appium port
            self.alog.d(f"Checking if port {port} is in use...")
            command = ["lsof", "-i", f":{port}"]
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True).splitlines()

            if len(output) > 1:
                self.alog.d(f"Processes using port {port}:")
                for line in output[1:]:  # Skip the header
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        self.alog.d(f"Killing process with PID {pid} using port {port}")
                        os.kill(int(pid), signal.SIGKILL)
                return
            else:
                self.alog.d(f"No process found using port {port}")
        
        except subprocess.CalledProcessError:
            self.alog.d(f"No process found on port {port}")

        # Fallback to kill all 'node' processes
        try:
            self.alog.d("Trying to terminate all Appium-related node processes...")
            node_pids = subprocess.check_output(["pgrep", "-x", "node"], text=True).strip().splitlines()
            for pid in node_pids:
                self.alog.d(f"Killing node process with PID: {pid}")
                os.kill(int(pid), signal.SIGKILL)
        except subprocess.CalledProcessError:
            self.alog.d("No existing Appium (node) processes found.")
        except Exception as e:
            self.alog.e(f"Unexpected error while killing Appium processes: {e}")
    
    def _deinit_appium_server(self):
      """
      Forcefully clean up all running Appium server processes stored in server_process_list.
      """
      for base_path, process in self.server_process_list.items():
         if process and process.poll() is None:
            process.kill()
            self.alog.d(f"Forcefully terminated Appium server for base_path: {base_path}")
      self.server_process_list.clear()
    
    def stop_appium_server(self):
        """
        Stop all running Appium servers.
        """
        self.force_deinit_appium_server()
        #self._deinit_appium_server() # Commented out to avoid killing the server process, its not working
