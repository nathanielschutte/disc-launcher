

class DiscLauncherException(Exception):
    def __init__(self, msg, *args) -> None:
        super().__init__(msg)
        self._msg = msg
    
    @property
    def message(self):
        return self._msg

class FormattedException(DiscLauncherException):
    def __init__(self, error, *args, header='DiscLauncher error:') -> None:
        self.error = error
        self.header = header
        self.format = '\n{header}\n{error}\n'
    
    @property
    def message(self):
        return self.format.format(header = self.header, error = self.error)
