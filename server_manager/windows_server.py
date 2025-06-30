import subprocess
import os
import time
import re
from datetime import datetime
from server_manager.server_base import AppiumServerBase

class WindowsAppiumServer(AppiumServerBase):
   """
   Handles Appium server management for Windows.
   
   This class provides methods to initialize, start, and stop Appium servers on a Windows machine.
   It maintains a mapping of base paths to their corresponding Appium server processes and ensures
   proper cleanup when stopping the servers.
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
         command = ['cmd', '/c', 'appium', '-a', self.ip_address, '-p', str(port), '--base-path', base_path, '--log-level', 'debug']
         self.alog.d(f"Executing command: {' '.join(command)}")

         with open(log_file, 'w') as log:
            server_process = subprocess.Popen(
               command,
               stdout=log,
               stderr=subprocess.STDOUT,
            )
         
         self.server_process_list[base_path] = server_process

         time.sleep(5)
         url = f"http://{self.ip_address}:{port}/{base_path}"
         self.urls[base_path] = url
         self.alog.d(f"Appium server started on port {port}. Logs: {log_file}. URL: {url}")
        
         return True
      except Exception as e:
         self.alog.e(f"Error starting Appium server on port {port}: {e}")
         return False

   def force_deinit_appium_server(self):
      """
      Forcefully terminate all existing Appium server processes.
      
      Command to list the Appium server processes : tasklist | findstr node.exe
      """
      try:
         command = ['tasklist', '/FI', 'IMAGENAME eq node.exe']
         self.alog.d(f"Executing command: {' '.join(command)}")
         appium_pids = subprocess.check_output(command, text=True)

         matches = re.findall(r"node.exe\s+(\d+)", appium_pids)
         
         if matches:
            for pid in matches:
               kill_command = ['taskkill', '/F', '/PID', pid]
               self.alog.d(f"Executing command: {' '.join(kill_command)}")
               subprocess.run(kill_command)
               self.alog.d(f"Killed existing Appium process with PID: {pid}")
         else:
            self.alog.d("No existing Appium processes to kill.")
      except subprocess.CalledProcessError:
         self.alog.d("No existing Appium processes found.")
      except Exception as e:
         self.alog.e(f"Error killing existing Appium processes: {e}")

   def _deinit_appium_server(self):
      """
      Forcefully clean up all running Appium server processes stored in server_process_list.
      """
      for base_path, process in self.server_process_list.items():
         if process and process.poll() is None:
            self.alog.d(f"Attempting to terminate Appium server for base_path: {base_path}, PID: {process.pid}")
            process.terminate()
            process.wait()
            self.alog.d(f"Forcefully terminated Appium server for base_path: {base_path}, PID: {process.pid}")
      self.server_process_list.clear()

   def stop_appium_server(self):
      """
      Stop all running Appium servers.
      """
      self.force_deinit_appium_server()
      #self._deinit_appium_server()
