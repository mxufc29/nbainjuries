class InjuryReportError(Exception):
    pass


class URLRetrievalError(InjuryReportError):
    def __init__(self, url, reason):
        self.url = url
        self.reason = reason
        super().__init__()

    def __str__(self):
        return f"Failed to access src data: {self.reason}"


class LocalRetrievalError(InjuryReportError, FileNotFoundError):
    def __init__(self, filepath, reason):
        self.filepath = filepath
        self.reason = reason
        super().__init__()

    def __str__(self):
        return f"Failed to access local src data: {self.reason}"


class DataValidationError(InjuryReportError):
    pass
