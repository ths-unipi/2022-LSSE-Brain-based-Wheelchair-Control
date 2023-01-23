class SessionCleaning:

    def correct_missing_samples(self, headset: list):
        """
        Corrects missing samples in the list of headset channels.
        :param headset: List of EEG channels.
        :return: None
        """
        for channel in range(len(headset)):
            # If a sample (a channel) is missing the interpolation is computed
            if not headset[channel]:
                print(f'[-] Channel nr. {channel + 1} is missing')
                if 7 <= channel <= 11:
                    self._interpolate_list(headset, channel)

    @staticmethod
    def _interpolate_list(headset, channel):
        """
        Interpolates the specified channel with the adjacent ones
        :param headset: List of EEG channels.
        :param channel: The channel to interpolate.
        :return: None
        """
        # List of adjacent channels in the EEG headset
        lists_to_use = [channel - 1, channel + 1, channel - 6, channel + 6]
        channel_length = len(headset[0])
        for i in range(channel_length):
            value = 0
            list_number = 0
            for j in lists_to_use:
                if headset[j]:
                    value += headset[j][i]
                    list_number += 1
            if list_number != 0:
                headset[channel].append(value / list_number)

    @staticmethod
    def correct_outliers(headset: list, min_eeg: int, max_eeg: int):
        """
        Corrects outliers in the EEG data of the different channels.
        :param headset: List of EEG channels.
        :param min_eeg: Minimum EEG value.
        :param max_eeg: Maximum EEG value.
        :return: None
        """
        for channel in headset:
            for i in range(len(channel)):
                if channel[i] > max_eeg:
                    channel[i] = max_eeg
                elif channel[i] < min_eeg:
                    channel[i] = min_eeg
