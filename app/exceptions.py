class UserNotLoggedInException(Exception): ...

class ValidationException(Exception):
    def __init__(self, errors: dict) -> None:
        self.errors = errors
        super().__init__(errors)

class NotFoundError(Exception): ...