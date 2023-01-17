import os
import random

from pandas import read_csv
from requests import post

INGESTION_SYSTEM_IP = 'localhost'
INGESTION_SYSTEM_PORT = 5000
OPERATIVE_MODE = 'development'

if __name__ == '__main__':
    calendar = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_calendar.csv'))
    headset = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_headset.csv'))
    settings = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_setting.csv'))

    # Labels are sent only in development operative mode
    if OPERATIVE_MODE == 'development':
        labels = read_csv(os.path.join(os.path.abspath('..'), 'data', 'brainControlledWheelchair_labels.csv'))
        sets = [calendar, headset, labels, settings]
    else:
        sets = [calendar, headset, settings]

    while len(sets) > 0:
        set_index = random.randint(0, (len(sets) - 1))

        # Send record to Ingestion System
        connection_string = f'http://{INGESTION_SYSTEM_IP}:{INGESTION_SYSTEM_PORT}/record'
        record = sets[set_index].loc[0].to_dict()
        response = post(connection_string, json=record)

        sets[set_index].drop(0, inplace=True)
        sets[set_index].reset_index(drop=True, inplace=True)

        if sets[set_index].empty:
            print(f'set index {set_index} | {sets[set_index].empty}')
            sets.pop(set_index)
