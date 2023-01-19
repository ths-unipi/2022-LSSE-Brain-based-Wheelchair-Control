from sklearn.model_selection import train_test_split


class LearningSessionSetSplitter:

    def __init__(self, config):
        self.segregation_system_config = config

    def generate_training_validation_testing_set(self, dataset):
        # train_test_split function can split the dataset only in two part, so it's needed to execute it
        # again to obtain three sets
        training_size = self.segregation_system_config['training_set_size']
        validation_size = self.segregation_system_config['validation_set_size']
        testing_size = self.segregation_system_config['testing_set_size']

        testing_size = testing_size / (1 - training_size)
        validation_size = 1 - testing_size

        training, res = train_test_split(dataset, train_size=training_size)
        if testing_size < validation_size:
            testing, validation = train_test_split(res, train_size=testing_size, test_size=validation_size)
        else:
            validation, testing = train_test_split(res, train_size=validation_size, test_size=testing_size)

        # return the final dataset composed by the splitted dataset
        return {'training': training, 'validation': validation, 'testing': testing}