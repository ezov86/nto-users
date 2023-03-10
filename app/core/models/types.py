from sqlalchemy import TypeDecorator, String, Dialect


# noinspection PyAbstractClass
class ScopesArrayType(TypeDecorator):
    """
    Array of user scopes that is stored as a string in DB. Note that scope should not contain any blank characters.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value: list[str], dialect: Dialect) -> str:
        return " ".join(value)

    def process_result_value(self, value: str, dialect: Dialect) -> list[str]:
        return value.split()