
LABELS_MAP = ["move", "stop", "left", "right"]


class MonitoringPhase:

    def __init__(self):
        self._session_counter = 0
        self._label = None

    def increment_session_counter(self):
        self._session_counter+=1

    def check_threshold(self, threshold: int):
        print(f"***MonitoringPhase***   Session counter:{self._session_counter}")
        return self._session_counter >= threshold

    def prepare_label(self, uuid: str, label_from_classifier: int) -> dict:
        return {'uuid': uuid, 'label': LABELS_MAP[label_from_classifier]}
