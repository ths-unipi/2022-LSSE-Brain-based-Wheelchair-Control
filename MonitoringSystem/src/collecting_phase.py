


class CollectingPhase:
    _collecting_phase_instance = None

    @staticmethod
    def get_instance():
        if CollectingPhase._collecting_phase_instance is None:
            CollectingPhase._collecting_phase_instance = CollectingPhase()
        return CollectingPhase._collecting_phase_instance


    def __init__(self,labels_threshold):
        self.counter_session_labels = 0
        self.labels_threshold = labels_threshold


    def increment_counter(self):
        self.counter_session_labels +=1

    def check_labels_thresold(self):
        if self.counter_session_labels < self.labels_threshold:
            return False
        else:
            return True

    def get_counter_session_label(self):
        return self.counter_session_labels
