class SmartAPIException(Exception):

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(SmartAPIException, self).__init__(message)
        self.code = code


class GeneralException(SmartAPIException):
    """
    An unclassified, general error.
    Default code is 500.
    """

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(GeneralException, self).__init__(message, code)


class TokenException(SmartAPIException):
    """
    Represents all token and authentication related errors. 
    Default code is 403.
    """

    def __init__(self, message, code=403):
        """Initialize the exception."""
        super(TokenException, self).__init__(message, code)


class PermissionException(SmartAPIException):
    """
    Represents permission denied exceptions for certain calls. 
    Default code is 403.
    """

    def __init__(self, message, code=403):
        """Initialize the exception."""
        super(PermissionException, self).__init__(message, code)


class OrderException(SmartAPIException):
    """
    Represents all order placement and manipulation errors.
    Default code is 500.
    """

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(OrderException, self).__init__(message, code)


class InputException(SmartAPIException):
    """
    Represents user input errors such as missing and invalid parameters. 
    Default code is 400.
    """

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(InputException, self).__init__(message, code)


class DataException(SmartAPIException):
    """
    Represents a bad response from the backend Order Management System (OMS). 
    Default code is 502.
    """

    def __init__(self, message, code=502):
        """Initialize the exception."""
        super(DataException, self).__init__(message, code)


class NetworkException(SmartAPIException):
    """
    Represents a network issue between api and the backend Order Management System (OMS). 
    Default code is 503.
    """

    def __init__(self, message, code=503):
        """Initialize the exception."""
        super(NetworkException, self).__init__(message, code)
