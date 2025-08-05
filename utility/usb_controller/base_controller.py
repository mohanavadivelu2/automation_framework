from abc import ABC, abstractmethod

class BaseController(ABC):
    """
    Abstract base class for USB controllers.
    """

    @abstractmethod
    def reset_port(self, port_id):
        """
        Reset a specific USB port.
        """
        pass

    @abstractmethod
    def enable_port(self, port_id):
        """
        Enable a specific USB port.
        """
        pass

    @abstractmethod
    def disable_port(self, port_id):
        """
        Disable a specific USB port.
        """
        pass
