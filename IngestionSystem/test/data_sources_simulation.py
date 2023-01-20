import os
import random
import time
from datetime import datetime

from pandas import read_csv, DataFrame
from requests import post

INGESTION_SYSTEM_IP = 'localhost'
INGESTION_SYSTEM_PORT = 5000
MISSING_SAMPLES = [9, 10, 11]
TESTING_MODE = False
NUM_OF_DATASET = 3

YELLOW_COLOR = "\033[93m"
BLUE_COLOR = "\033[94m"
CYAN_COLOR = "\033[96m"
WHITE_COLOR = "\033[97m"
DEFAULT_COLOR = WHITE_COLOR


def blue(string):
    return BLUE_COLOR + string + DEFAULT_COLOR


def cyan(string):
    return CYAN_COLOR + string + DEFAULT_COLOR


def yellow(string):
    return YELLOW_COLOR + string + DEFAULT_COLOR


def save_timestamp():
    # Save timestamp into a CSV
    current_time = datetime.now().strftime("%H:%M:%S.%f")
    df = DataFrame([[current_time]], columns=['Timestamp'])
    df.to_csv('timestamp.csv', index=False)


def read_dataset():
    calendar = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_calendar.csv'))
    set_calendar = calendar.rename(columns={'CALENDAR': 'calendar', 'TIMESTAMP': 'timestamp', 'UUID': 'uuid'})

    headset = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_headset.csv'))
    set_headset = headset.rename(columns={'CHANNEL': 'channel', 'TIMESTAMP': 'timestamp', 'UUID': 'uuid'})

    settings = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_setting.csv'))
    set_settings = settings.rename(columns={'SETTINGS': 'environment', 'TIMESTAMP': 'timestamp', 'UUID': 'uuid'})

    labels = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_labels.csv'))
    set_labels = labels[['LABELS', 'UUID']].rename(columns={'LABELS': 'label', 'UUID': 'uuid'})

    sets = [
        {
            'name': 'calendar',
            'records': set_calendar
        }, {
            'name': 'headset',
            'records': set_headset,
        }, {
            'name': 'label',
            'records': set_labels
        }, {
            'name': 'environment',
            'records': set_settings
        }]

    return sets


def send_dataset(dataset_counter: int):
    stop_sending = False
    catch_timestamp = True

    while not stop_sending:

        # Shuffle in order to create non-synchronized records
        random.shuffle(sets)

        print(cyan('============================ START SESSION ============================'))
        for i in range(0, len(sets)):

            if sets[i]['records'].empty:
                stop_sending = True
                break

            if sets[i]['name'] == 'headset':
                headset_channels = sets[i]['records'].iloc[:22, :].to_dict('records')
                sets[i]['records'].drop(sets[i]['records'].index[:22], inplace=True)
                sets[i]['records'].reset_index(drop=True, inplace=True)

                while headset_channels:
                    # Shuffle the headset EEG data
                    random.shuffle(headset_channels)

                    record = headset_channels.pop(0)
                    uuid = record['uuid']
                    channel = record['channel']

                    # Sending a record with a probability of 0.2
                    if channel in MISSING_SAMPLES and random.random() < 0.2:
                        print(f'({record["uuid"]})' + yellow(f' Generating a missing sample [channel {channel}]'))
                    else:
                        print(f'({record["uuid"]})' + blue(f' Sending headset EEG data [channel {channel}]'))
                        post(connection_string, json=record)

                        if TESTING_MODE and catch_timestamp and dataset_counter == 0:
                            save_timestamp()
                            catch_timestamp = False

            else:
                record = sets[i]['records'].loc[0].to_dict()
                sets[i]['records'].drop(0, inplace=True)
                sets[i]['records'].reset_index(drop=True, inplace=True)

                if random.random() < 0.01:
                    print(f'({record["uuid"]})' + yellow(f' Generating a missing sample [{sets[i]["name"]}]'))
                else:
                    print(f'({record["uuid"]})' + blue(f' Sending {sets[i]["name"]} data'))
                    post(connection_string, json=record)

                    if TESTING_MODE and catch_timestamp and dataset_counter == 0:
                        save_timestamp()
                        catch_timestamp = False


if __name__ == '__main__':

    connection_string = f'http://{INGESTION_SYSTEM_IP}:{INGESTION_SYSTEM_PORT}/record'
    print(blue(f'Connection to {connection_string}'))
    print(blue(f'Testing mode: {TESTING_MODE}\n'))

    if TESTING_MODE:
        for i in range(0, NUM_OF_DATASET):
            print(cyan(f'Dataset {i + 1}'))
            sets = read_dataset()
            send_dataset(i)
    else:
        sets = read_dataset()
        send_dataset(-1)
