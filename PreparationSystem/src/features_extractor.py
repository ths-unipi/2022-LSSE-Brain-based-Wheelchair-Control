import numpy as np
from scipy.signal import welch
from scipy.integrate import simps


class FeaturesExtractor:

    def extract_features(self, features: dict, raw_session: dict, prepared_session: dict, operative_mode: str):
        delta, theta, alpha, beta = self.extract_headset_features(raw_session['headset'], features)
        if operative_mode == 'development':
            self.prepare_session_development(raw_session, prepared_session, delta, theta, alpha, beta)
        elif operative_mode == 'execution':
            self.prepare_session_execution(raw_session, prepared_session, delta, theta, alpha, beta, features)

    def extract_headset_features(self, headset: list, features: dict):
        delta, theta, alpha, beta = [], [], [], []
        for channel in headset:
            delta.append(self.compute_average_power(channel, features['delta_wave']['start_frequency'],
                                                    features['delta_wave']['end_frequency']))
            theta.append(self.compute_average_power(channel, features['theta_wave']['start_frequency'],
                                                    features['theta_wave']['end_frequency']))
            alpha.append(self.compute_average_power(channel, features['alpha_wave']['start_frequency'],
                                                    features['alpha_wave']['end_frequency']))
            beta.append(self.compute_average_power(channel, features['beta_wave']['start_frequency'],
                                                   features['beta_wave']['end_frequency']))
        return delta, theta, alpha, beta

    def compute_average_power(self, headset: list, start_frequency: int, end_frequency: int):
        sampling_frequency = 250
        window_seconds = 1.25
        # Define window length
        # segment_length = (2 / start_frequency) * sampling_frequency
        segment_length = window_seconds * sampling_frequency

        # Compute the modified periodogram (Welch)
        frequencies, psd = welch(headset, sampling_frequency, nperseg=segment_length)

        # Frequency resolution
        frequency_resolution = frequencies[1] - frequencies[0]

        # Find intersecting values in frequency vector
        intersecting_bands = np.logical_and(frequencies >= start_frequency, frequencies <= end_frequency)

        # Integral approximation of the spectrum using Simpson's rule.
        return simps(psd[intersecting_bands], dx=frequency_resolution)

    def prepare_session_development(self, raw_session: dict, prepared_session: dict, delta: list, theta: list,
                                    alpha: list, beta: list):
        prepared_session['uuid'] = raw_session['UUID']
        prepared_session['features'] = {}
        prepared_session['features']['delta'] = delta
        prepared_session['features']['theta'] = theta
        prepared_session['features']['alpha'] = alpha
        prepared_session['features']['beta'] = beta
        prepared_session['features']['environment'] = raw_session['environment']
        prepared_session['calendar'] = raw_session['calendar']
        prepared_session['commandThought'] = raw_session['commandThought']

    def prepare_session_execution(self, raw_session: dict, prepared_session: dict, delta: list, theta: list,
                                  alpha: list, beta: list, features: dict):
        prepared_session['uuid'] = raw_session['UUID']
        # Take the numeric value corresponding to the value of environment in raw session
        environment = features['environment'][raw_session['environment']]
        prepared_session['features'] = alpha + beta + delta + theta + [environment]
