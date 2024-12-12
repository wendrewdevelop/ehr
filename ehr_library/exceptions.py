class HTTPRequestException(Exception):
    """
    Custom exception for HTTP request errors.
    """
    def __init__(self, message, status_code=None, url=None):
        """
        Initialize the exception.

        :param message: Description of the error
        :param status_code: Optional HTTP status code
        :param url: Optional URL associated with the error
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.url = url

    def __str__(self):
        base_message = self.message
        if self.status_code:
            base_message += f" (Status code: {self.status_code})"
        if self.url:
            base_message += f" [URL: {self.url}]"
        return base_message


class ConnectionFailedException(HTTPRequestException):
    """
    Exception raised for connection errors.
    """
    pass


class TimeoutException(HTTPRequestException):
    """
    Exception raised for request timeouts.
    """
    pass


class InvalidURLException(HTTPRequestException):
    """
    Exception raised for invalid URLs.
    """
    pass