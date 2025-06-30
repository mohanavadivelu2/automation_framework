import os
import time
import threading
import base64
from logger.log_manager import LogManager

class ScreenRecorder:
    
    def __init__(self, driver, file_path: str = ".", file_name: str = "screen_recording.mp4"):
        self.hlog = LogManager.get_instance().get_test_case_logger()
        self.driver = driver
        self.file_path = file_path
        self.file_name = file_name
        self.recording = False
        self.thread = None

        # Ensure the directory exists
        os.makedirs(self.file_path, exist_ok=True)
        self.hlog.d(f"ScreenRecorder initialized with path: {self.file_path}, file: {self.file_name}")

    def start_recording(self, bugReport=True):
        if not self.recording:
            self.recording = True
            options = {"bugReport": bugReport, "videoQuality": "medium"}
            self.driver.start_recording_screen(**options)
            self.thread = threading.Thread(target=self._record_screen)
            self.thread.start()
            self.hlog.d(f"Screen recording started with bugReport={bugReport} and videoQuality=medium.")

    def _record_screen(self):
        while self.recording:
            time.sleep(1)

    def stop_recording(self):
        if self.recording:
            self.recording = False
            video_data = self.driver.stop_recording_screen()
            if isinstance(video_data, str):
                video_data = base64.b64decode(video_data.encode())

            full_path = os.path.join(self.file_path, self.file_name)
            with open(full_path, "wb") as video_file:
                video_file.write(video_data)

            self.hlog.d(f"Screen recording stopped and saved as {full_path}")
