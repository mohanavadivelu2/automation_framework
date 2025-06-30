import platform
from .windows_server import WindowsAppiumServer
from .unix_server import UnixAppiumServer
from logger import HLog

def AppiumServerManagerFactory(config_file):
    """Factory function to create an instance of AppiumServerManager based on the platform."""
    system_platform = platform.system()
    if system_platform == "Windows":
        return WindowsAppiumServer(config_file)
    elif system_platform in ["Linux", "Darwin"]:  # Darwin = macOS
        return UnixAppiumServer(config_file)
    else:
        raise RuntimeError(f"Unsupported platform: {system_platform}")
