from datetime import datetime

class HLog:
    LOG_LEVELS = {"verbose": 0, "debug": 1, "info": 2, "warning": 3, "error": 4}
    GLOBAL_LOG_LEVEL = "verbose"

    def __init__(self, log_file: str):
        self.log_file = log_file  # No folder validation or creation here

    @classmethod
    def set_log_level(cls, level):
        if level in cls.LOG_LEVELS:
            cls.GLOBAL_LOG_LEVEL = level
        else:
            print(f"Invalid log level: {level}. Using default: {cls.GLOBAL_LOG_LEVEL}")

    def v(self, message): self._log(message, "verbose")
    def d(self, message): self._log(message, "debug")
    def i(self, message): self._log(message, "info")
    def w(self, message): self._log(message, "warning")
    def e(self, message): self._log(message, "error")

    def _log(self, message, level="info"):
        if self.LOG_LEVELS[level] < self.LOG_LEVELS[self.GLOBAL_LOG_LEVEL]:
            return
        try:
            with open(self.log_file, "a", encoding="utf-8") as log:
                log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {level.upper()}: {message}\n"
                log.write(log_entry)
            print(f"{level.upper()}: {message}")
        except Exception as e:
            print(f"Logger encountered an error: {e}")
