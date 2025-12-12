class UserCannotLoseLoginMethodError(Exception):
    def __init__(self) -> None:
        super().__init__("User must have at least one login method.")
