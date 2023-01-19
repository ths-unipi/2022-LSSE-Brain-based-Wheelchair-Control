import os
import random
import time

from pandas import read_csv
from requests import post

INGESTION_SYSTEM_IP = 'localhost'
INGESTION_SYSTEM_PORT = 5000
MISSING_SAMPLES = [9, 10, 11]

if __name__ == '__main__':
    # Read records from the sample dataset
    calendar = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_calendar.csv'))
    headset = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_headset.csv'))
    settings = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_setting.csv'))
    labels = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_labels.csv'))
    label = labels[['LABELS', 'UUID']].rename(columns={'LABELS': 'label', 'UUID': 'uuid'})

    sets = [
        {
            'name': 'calendar',
            'records': calendar
        }, {
            'name': 'headset',
            'records': headset,
        }, {
            'name': 'labels',
            'records': label
        }, {
            'name': 'settings',
            'records': settings
        }]
    connection_string = f'http://{INGESTION_SYSTEM_IP}:{INGESTION_SYSTEM_PORT}/record'

    stop_sending = False
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
                    # Shuffle the headset eeg data
                    random.shuffle(headset_channels)

                    record = headset_channels.pop(0)
                    # Sending a record with a probability of 0.2
                    if random.random() < 0.2 and record["CHANNEL"] in MISSING_SAMPLES:
                        print(f'Generating a missing sample: {record["UUID"]},{record["CHANNEL"]}')
                    else:
                        print(f'Sending set headset: {record["UUID"]},{record["CHANNEL"]}')
                        response = post(connection_string, json=record)

            else:
                record = sets[i]['records'].loc[0].to_dict()
                sets[i]['records'].drop(0, inplace=True)
                sets[i]['records'].reset_index(drop=True, inplace=True)

                if random.random() < 0.01:
                    print(f'Generating a missing sample from the set: {sets[i]["name"]}')
                else:
                    if sets[i]["name"] == 'labels':
                        print(f'Sending set: {sets[i]["name"]} | RECORD : {record["uuid"]}')
                    else:
                        print(f'Sending set: {sets[i]["name"]} | RECORD : {record["UUID"]}')
                    response = post(connection_string, json=record)

        # Data sources send records every 3 seconds
        # time.sleep(3)
        print('============== END SESSION ==============\n')
