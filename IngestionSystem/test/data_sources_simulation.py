import os
import random
from time import time, sleep
from datetime import datetime

from pandas import read_csv, DataFrame
from requests import post, exceptions

from utility.logging import error, info_simulation, warning_simulation

INGESTION_SYSTEM_IP = 'localhost'
INGESTION_SYSTEM_PORT = 4000
MISSING_SAMPLES = [9, 10, 11]
TESTING_MODE = True
DATASET_TO_SEND = 3


def save_timestamp():
    t = time()
    df = DataFrame([[t]], columns=['Timestamp'])
    df.to_csv(f'timestamp-{t}.csv', index=False)


def send_record(data: dict) -> None:
    try:
        post(url=connection_string, json=data)
    except exceptions.RequestException:
        error('Ingestion System unreachable')
        exit(-1)


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

        info_simulation('', '============================ START SESSION ============================', 0)
        for i in range(0, len(dataset)):
            if dataset[i]['name'] == 'headset':
                # Read the 22 channels data in the dataset
                headset_channels = dataset[i]['records'].iloc[session_index * 22:session_index * 22 + 22, :].to_dict(
                    'records')

                # Shuffle the headset EEG data
                random.shuffle(headset_channels)

                for m in range(0, len(headset_channels)):
                    record = headset_channels[m]
                    uuid = record['uuid']
                    channel = record['channel']

                    # Sending a record with a probability of 0.2
                    if channel in MISSING_SAMPLES and random.random() < 0.2:
                        warning_simulation(uuid, f'Generating a missing sample [channel {channel}]')
                    else:
                        info_simulation(uuid, f'Sending headset EEG data [channel {channel}]', 1)
                        send_record(data=record)

                        if dataset_counter == 0 and catch_timestamp:
                            save_timestamp()
                            catch_timestamp = False
            else:
                record = dataset[i]['records'].loc[session_index].to_dict()

                if random.random() < 0.1:
                    warning_simulation(record["uuid"], f'Generating a missing sample [{dataset[i]["name"]}]')
                else:
                    info_simulation(record["uuid"], f'Sending {dataset[i]["name"]} data', 1)
                    send_record(data=record)

                    if dataset_counter == 0 and catch_timestamp:
                        save_timestamp()
                        catch_timestamp = False

        # Send a session very X milliseconds
        sleep(0.3)


if __name__ == '__main__':

    connection_string = f'http://{INGESTION_SYSTEM_IP}:{INGESTION_SYSTEM_PORT}/record'
    info_simulation('', f'Connection to {connection_string}', 2)
    info_simulation('', f'Testing mode: {TESTING_MODE}\n', 2)

    dataset_to_send = read_dataset()
    dataset_length = len(dataset_to_send[0]['records'])

    if TESTING_MODE:
        j = 0
        # while j < DATASET_TO_SEND:
        while True:
            info_simulation('', f'Sending Dataset #{j + 1}', 0)

            # In order to flush the queue at the Ingestion System it is necessary wait some minutes every 3 dataset
            if j == 3:
                print('Waiting...')
                sleep(300)

            send_dataset(dataset=dataset_to_send, maximum_dataset_length=dataset_length, dataset_counter=j)
            j += 1
    else:
        send_dataset(dataset=dataset_to_send, maximum_dataset_length=dataset_length, dataset_counter=-1)
