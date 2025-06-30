class BaseHandler:
    def processCommand(self, command_data: dict):
        raise NotImplementedError("Subclasses must implement processCommand()")
