class RawSession:
    """
        RawSession class
    """

    def __str__(self) -> str:
        info = 'UUID: ' + self.uuid + '\n'\
            'CALENDAR: ' + self.calendar + '\n' \
            'COMMAND_THOUGHT: ' + self.command_thought + '\n'\
            'ENVIRONMENT: ' + self.environment + '\n'\
            'HEADSET_DATA: \n'

        for elem in self.headset:
            info += str(elem) + '\n'

        return info

    def __init__(self, uuid: str, calendar: str, headset: list, command_thought: str, environment: str) -> None:
        self.uuid = uuid
        self.calendar = calendar
        self.headset = list()
        self.headset = headset
        self.command_thought = command_thought
        self.environment = environment

    def get_headset(self) -> list:
        return self.headset
