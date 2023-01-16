class RawSession:
    """
        RawSession class
    """

    def __init__(self, uuid: str, calendar: str, headset: dict, command_thought: str, environment: str) -> None:
        self.uuid = uuid
        self.calendar = calendar
        self.headset = headset
        self.command_thought = command_thought
        self.environment = environment
