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
    t = time.time()
    df = DataFrame([[t]], columns=['Timestamp'])
    df.to_csv(f'timestamp-{t}.csv', index=False)


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
            'name': 'label',
            'records': set_labels
        }, {
            'name': 'environment',
            'records': set_settings
        }, {
            'name': 'headset',
            'records': set_headset,
        }]

    return dataset


def send_dataset(dataset: list, maximum_dataset_length: int, dataset_counter: int):
    catch_timestamp = True

    for session_index in range(0, maximum_dataset_length):
        # Shuffle in order to create non-synchronized records
        random.shuffle(dataset)

        print(cyan('============================ START SESSION ============================'))
        for i in range(0, len(dataset)):
            if dataset[i]['name'] == 'headset':
                # Read the 22 channels data in the dataset
                headset_channels = dataset[i]['records'].iloc[session_index*22:session_index*22 + 22, :].to_dict('records')

                # Shuffle the headset EEG data
                random.shuffle(headset_channels)

                for m in range(0, len(headset_channels)):
                    record = headset_channels[m]
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
                record = dataset[i]['records'].loc[session_index].to_dict()

                if random.random() < 0.01:
                    print(f'({record["uuid"]})' + yellow(f' Generating a missing sample [{dataset[i]["name"]}]'))
                else:
                    print(f'({record["uuid"]})' + blue(f' Sending {dataset[i]["name"]} data'))
                    post(connection_string, json=record)

                    if dataset_counter == 0 and catch_timestamp:
                        save_timestamp()
                        catch_timestamp = False

        # Send a session very X milliseconds
        time.sleep(0.8)


if __name__ == '__main__':

    connection_string = f'http://{INGESTION_SYSTEM_IP}:{INGESTION_SYSTEM_PORT}/record'
    print(blue(f'Connection to {connection_string}'))
    print(blue(f'Testing mode: {TESTING_MODE}\n'))

    dataset_to_send = read_dataset()
    dataset_length = len(dataset_to_send[0]['records'])

    if TESTING_MODE:
        j = 0
        # while j < DATASET_TO_SEND:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S.%f")
            print(f'({current_time})' + cyan(f' Sending Dataset #{j + 1}'))
            send_dataset(dataset=dataset_to_send, maximum_dataset_length=dataset_length, dataset_counter=j)
            j += 1
    else:
        send_dataset(dataset=dataset_to_send, maximum_dataset_length=dataset_length, dataset_counter=-1)
