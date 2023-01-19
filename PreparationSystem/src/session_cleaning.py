class SessionCleaning:

    def correct_missing_samples(self, headset: list):
        for channel in range(len(headset)):
            # if a sample (a channel) is missing the interpolation is computed
            if not headset[channel]:
                self.interpolate_list(headset, channel)

    @staticmethod
    def interpolate_list(headset, channel):
        # list of adjacent channels in the EEG headset
        lists_to_use = [channel - 1, channel + 1, channel - 6, channel + 6]
        channel_length = len(headset[0])
        for i in range(channel_length):
            value = 0
            list_number = 0
            for j in lists_to_use:
                if 0 <= j < len(headset) and headset[j]:
                    value += headset[j][i]
                    list_number += 1
            if list_number != 0:
                headset[channel].append(value / list_number)

    @staticmethod
    def correct_outliers(headset: list, min_eeg: int, max_eeg: int):
        for channel in headset:
            for i in range(len(channel)):
                if channel[i] > max_eeg:
                    channel[i] = max_eeg
                elif channel[i] < min_eeg:
                    channel[i] = min_eeg
