class CheckerError(Exception):
    """Base class for expected checker errors."""


class InvalidPDFError(CheckerError):
    pass


class UploadTooLargeError(CheckerError):
    pass


class ValidationTimeoutError(CheckerError):
    pass


class VeraPDFExecutionError(CheckerError):
    pass
