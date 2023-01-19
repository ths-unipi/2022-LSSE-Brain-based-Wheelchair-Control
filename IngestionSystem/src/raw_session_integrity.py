class RawSessionIntegrity:

    def __init__(self) -> None:
        self.missing_samples = None

    def get_missing_samples(self) -> int:
        return self.missing_samples

    def mark_missing_samples(self, headset_eeg: list, threshold: int) -> None:
        self.missing_samples = 3
