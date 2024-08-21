import exceptions

class InvalidDirectoryError(exceptions.BooException):
    """Exception raised when the path does not point to a directory."""
    def __init__(self, message="The path does not point to a valid directory."):
        super().__init__(message)

class SearchNotFound(exceptions.BooException):
    """Exception raised when search term is not found in file content."""
    def __init__(self, message="Search term not found in content"):
        super().__init__(message)

class InvalidArgumentError(exceptions.BooException):
    """Exception raised when an invalid value is passed."""
    def __init__(self, message="Invalid value passed."):
        super().__init__(message)