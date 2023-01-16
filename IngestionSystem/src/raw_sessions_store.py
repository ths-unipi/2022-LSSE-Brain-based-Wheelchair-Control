import json
from jsonschema import validate, ValidationError


class RawSessionsStore:
    """
        RawSessionsStore class
    """

    def __init__(self) -> None:
        pass

    def store_record(self, record: dict) -> None:
        pass

    def delete_raw_session(self, uuid: str) -> None:
        pass

    def load_raw_session(self, uuid: str) -> None:
        pass

    def is_session_complete(self, uuid: str) -> bool:
        pass
