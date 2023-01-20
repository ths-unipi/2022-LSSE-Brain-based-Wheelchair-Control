import os
import random
from datetime import datetime

from pandas import read_csv, DataFrame
from requests import post

INGESTION_SYSTEM_IP = 'localhost'
INGESTION_SYSTEM_PORT = 5000
MISSING_SAMPLES = [9, 10, 11]
TESTING_MODE = True


def save_timestamp():
    # Save timestamp into a CSV
    current_time = datetime.now().strftime("%H:%M:%S.%f")
    df = DataFrame(current_time, columns=['Timestamp'])
    df.to_csv('timestamp.csv', index=False)


if __name__ == '__main__':
    # Read records from the sample dataset
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
            'name': 'labels',
            'records': set_labels
        }, {
            'name': 'settings',
            'records': set_settings
        }]
    connection_string = f'http://{INGESTION_SYSTEM_IP}:{INGESTION_SYSTEM_PORT}/record'

    stop_sending = False
    timestamp = True
    while not stop_sending:

        # Shuffle in order to create non-synchronized records
        random.shuffle(sets)

        print('============= START SESSION =============')
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
                        print(f'Generating a missing sample: {uuid},{channel}')
                    else:
                        print(f'Sending set headset: {uuid},{channel}')
                        post(connection_string, json=record)

                        if TESTING_MODE and timestamp:
                            save_timestamp()
                            timestamp = False

            else:
                record = sets[i]['records'].loc[0].to_dict()
                sets[i]['records'].drop(0, inplace=True)
                sets[i]['records'].reset_index(drop=True, inplace=True)

                if random.random() < 0.01:
                    print(f'Generating a missing sample from the set: {sets[i]["name"]}')
                else:
                    print(f'Sending set: {sets[i]["name"]} | RECORD : {record["uuid"]}')
                    post(connection_string, json=record)

                    if TESTING_MODE and timestamp:
                        save_timestamp()
                        timestamp = False

        print('============== END SESSION ==============\n')
