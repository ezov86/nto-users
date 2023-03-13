class InvalidAuthData(Exception):
    """
    Given authentication data is invalid (raised on login/register/auth method addition).
    """

    def __init__(self):
        super().__init__("Invalid authentication data")


class AccessDenied(Exception):
    """
    Access to user is denied (raised if user is disabled/not allowed in given scope).
    """

    def __init__(self, issue: str):
        super().__init__(f"Access denied for {issue}")


class AlreadyExists(Exception):
    """
    When trying to create resource with unique identifiers that already presented in DB.
    """

    def __init__(self, resource: str):
        super().__init__(f"{resource} already exists")


class InvalidToken(Exception):
    """
    Invalid token. Should be reraised as InvalidAuthData before endpoint catches.
    """

    def __init__(self, token_type: str):
        super().__init__(f"Invalid {token_type} token")


class NotFound(Exception):
    """
    Requested resource not found.
    """

    def __init__(self, resource: str):
        super().__init__(f"{resource} not found")


class AlreadyDoneNonIdempotentAction(Exception):
    """
    Same non-idempotent action was already performed.
    """

    def __init__(self, action: str):
        super().__init__(f"{action} is already done")
