import os
import random
import time
from datetime import datetime

from pandas import read_csv, DataFrame
from requests import post

INGESTION_SYSTEM_IP = 'localhost'
INGESTION_SYSTEM_PORT = 4000
MISSING_SAMPLES = [9, 10, 11]
TESTING_MODE = True
DATASET_TO_SEND = 3

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
    df = DataFrame([[time.time()]], columns=['Timestamp'])
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

    dataset = [
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

    return dataset


def send_dataset(dataset_copy: list, dataset_counter: int):
    catch_timestamp = True

    while True:
        # Shuffle in order to create non-synchronized records
        random.shuffle(dataset_copy)

        for i in range(0, len(dataset_copy)):
            if dataset_copy[i]['records'].empty:
                return

        print(cyan('============================ START SESSION ============================'))
        for i in range(0, len(dataset_copy)):
            if dataset_copy[i]['name'] == 'headset':
                headset_channels = dataset_copy[i]['records'].iloc[:22, :].to_dict('records')
                dataset_copy[i]['records'].drop(dataset_copy[i]['records'].index[:22], inplace=True)
                dataset_copy[i]['records'].reset_index(drop=True, inplace=True)

                # Shuffle the headset EEG data
                random.shuffle(headset_channels)

                while headset_channels:
                    record = headset_channels.pop(0)
                    uuid = record['uuid']
                    channel = record['channel']

                    # Sending a record with a probability of 0.2
                    if channel in MISSING_SAMPLES and random.random() < 0.2:
                        print(f'({uuid})' + yellow(f' Generating a missing sample [channel {channel}]'))
                    else:
                        print(f'({uuid})' + blue(f' Sending headset EEG data [channel {channel}]'))
                        post(connection_string, json=record)

                        if dataset_counter == 0 and catch_timestamp:
                            save_timestamp()
                            catch_timestamp = False

            else:
                record = dataset_copy[i]['records'].loc[0].to_dict()
                dataset_copy[i]['records'].drop(0, inplace=True)
                dataset_copy[i]['records'].reset_index(drop=True, inplace=True)

                if random.random() < 0.01:
                    print(f'({record["uuid"]})' + yellow(f' Generating a missing sample [{dataset_copy[i]["name"]}]'))
                else:
                    print(f'({record["uuid"]})' + blue(f' Sending {dataset_copy[i]["name"]} data'))
                    post(connection_string, json=record)

                    if dataset_counter == 0 and catch_timestamp:
                        save_timestamp()
                        catch_timestamp = False


if __name__ == '__main__':

    connection_string = f'http://{INGESTION_SYSTEM_IP}:{INGESTION_SYSTEM_PORT}/record'
    print(blue(f'Connection to {connection_string}'))
    print(blue(f'Testing mode: {TESTING_MODE}\n'))

    if TESTING_MODE:
        j = 0
        # while j < DATASET_TO_SEND:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S.%f")
            print(f'({current_time})' + cyan(f' Sending Dataset #{j + 1}'))
            sets = read_dataset()
            send_dataset(dataset_copy=sets, dataset_counter=j)
            j += 1
    else:
        sets = read_dataset()
        send_dataset(dataset_copy=sets, dataset_counter=-1)