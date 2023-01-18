import json
import os

from src.learning_session_store import LearningSessionStore

if __name__ == '__main__':
    with open(os.path.join(os.path.abspath('.'), 'dataset.json')) as f:
        dataset = json.load(f)

    training = []
    for session in dataset['training'][0:1]:
        session = [session['uuid']] + session['features']['alpha'] + session['features']['beta'] + \
                  session['features']['delta'] + session['features']['theta'] + \
                  [session['features']['environment'], session['command_thought']]
        training.append(tuple(session))

    db = LearningSessionStore()
    db.insert_dataset(training, 'training_set')
