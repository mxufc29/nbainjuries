class InjuryReportError(Exception):
    pass


class URLRetrievalError(InjuryReportError):
    def __init__(self, url, reason):
        self.url = url
        self.reason = reason
        super().__init__()

    def __str__(self):
        return f"Failed to access the source file at {self.url}: {self.reason}"


class LocalRetrievalError(InjuryReportError, FileNotFoundError):
    def __init__(self, filepath, reason):
        self.filepath = filepath
        self.reason = reason
        super().__init__()

    def __str__(self):
        return f"Cannot access local file at {self.filepath}: {self.reason}"


class DataValidationError(InjuryReportError):
    pass



