import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from keras.models import Sequential, Model, load_model
from keras.layers import Flatten, Dense, Embedding, Conv1D, MaxPooling1D
from keras.utils import pad_sequences

from sklearn.metrics import confusion_matrix
from numpy.random import seed

from cf_matrix import make_confusion_matrix

COMMENTS = [
    604,
    612,
    618,
    621,
    648
]
RANDOM_STATE = 33
LANGUAGES = ['Java', 'C#', 'C++']
SMELLS = [
    {'name': 'HarmfulCode', 'suffix': 'hm', 'padding_tokens': 53995},
]

# Third case, harmful code vs bug without smells:
# {'name': 'HarmfulVsBug', 'suffix': 'hb', 'padding_tokens': 53995},

# Second case, harmful code vs clean code:
# {'name': 'HarmfulCode', 'suffix': 'hm', 'padding_tokens': 53995},

# First case, all bugfixes:
# {'name': 'MultifacetedAbstraction', 'suffix': 'ma', 'padding_tokens': 53995},
# {'name': 'UnnecessaryAbstraction', 'suffix': 'ua', 'padding_tokens': 53995},
# {'name': 'InsufficientModularization', 'suffix': 'im', 'padding_tokens': 53995},
# {'name': 'WideHierarchy', 'suffix': 'wh', 'padding_tokens': 53995},
# {'name': 'ComplexMethod', 'suffix': 'cm', 'padding_tokens': 53995},
# {'name': 'LongMethod', 'suffix': 'lm', 'padding_tokens': 53995},

# Original, Moabson:
# {'name': 'GodClass', 'suffix': 'gc', 'padding_tokens': 17000},
# {'name': 'ShotgunSurgery', 'suffix': 'ss', 'padding_tokens': 17000},
# {'name': 'FeatureEnvy', 'suffix': 'fe', 'padding_tokens': 17000},
# {'name': 'DivergentChange', 'suffix': 'dv', 'padding_tokens': 17000},
# {'name': 'FeatureEnvy+DivergentChange', 'suffix': 'fe+dv', 'padding_tokens': 17000},
# {'name': 'LongMethod+ShotgunSurgery+FeatureEnvy+DivergentChange', 'suffix': 'lm+ss+fe+dv', 'padding_tokens': 17000},

MAIN_DIR = 'content'
TRAIN_DIR = os.path.join(MAIN_DIR, 'code_smells_datasets', 'train')
TEST_DIR = os.path.join(MAIN_DIR, 'code_smells_datasets', 'test')
MODELS_DIR = os.path.join(MAIN_DIR, 'models')
RESULTS_DIR = os.path.join(MAIN_DIR, 'results')
DATA_FILE = os.path.join(RESULTS_DIR, 'data.csv')


def to_array_int(token_str):
    return list(map(int, filter(len, token_str.split(' '))))


def padding_tokens(values, size):
    return pad_sequences(values, maxlen=size, padding='post', truncating='post')


def remove_comments(tokens):
    return list(filter(lambda value: value not in COMMENTS, tokens))


def pre_process_token_str(token_str):
    result = {}
    try:
        if type(token_str) == list:
            return remove_comments(token_str)
        result = remove_comments(to_array_int(token_str))
    except:
        print(token_str)
    return result


def init_data():
    return {
        'model': [],
        'dataset': [],
        'smell_name': [],
        'model_language': [],
        'target_language': [],
        'n_test_samples': [],
        'n_train_samples': [],
        'accuracy': [],
        'precision': [],
        'recall': [],
        'f1': [],
        'tn': [],
        'fp': [],
        'fn': [],
        'tp': []
    }


def append_data_file(data):
    pd.DataFrame(data).to_csv(DATA_FILE, index=False, mode='a', header=not os.path.exists(DATA_FILE))


def select_samples(smell_csv, n_samples):
    dataset = pd.DataFrame(columns=['smell', 'tokens'])

    positive = smell_csv.query('smell == 1').sample(n_samples, random_state=RANDOM_STATE)
    negative = smell_csv.query('smell == 0').sample(n_samples, random_state=RANDOM_STATE)

    samples = pd.concat([positive, negative], axis=0)

    dataset['tokens'] = samples['tokens']
    dataset['smell'] = samples['smell']

    return dataset


def process(data, dataset_id, dataset, x, y, smell, languages, target_language, model_name2, model_n_sample_val=None):
    fig = plt.figure(figsize=(20, 5))
    # Initial subplot coordinates
    i = 131

    for model_language in languages:
        if type(model_n_sample_val) == dict:
            model_n_sample = model_n_sample_val[smell['name']]
            model_n_sample = model_n_sample[model_language]
        else:
            model_n_sample = model_n_sample_val

        model_name = '{}_{}_{}_{}'.format(model_language, model_name2, model_n_sample, smell['suffix'])
        model_path = os.path.join(MODELS_DIR, model_name)

        if not os.path.exists(model_path):
            print('model not found: {}'.format(model_path))
            continue

        print('loading model: {}, dataset_id: {}'.format(model_name, dataset_id))

        pre_trained_model = load_model(model_path)

        loss, accuracy = pre_trained_model.evaluate(padding_tokens(x.values, smell['padding_tokens']), y, verbose=0)

        data['model'].append(model_name)
        data['n_train_samples'].append(model_n_sample)
        data['dataset'].append(dataset_id)
        data['smell_name'].append(smell['name'])
        data['model_language'].append(model_language)
        data['target_language'].append(target_language)
        data['n_test_samples'].append(len(x))
        data['accuracy'].append(accuracy)

        predictions = pre_trained_model.predict(padding_tokens(x.values, smell['padding_tokens']))
        output_name = 'model_{}_dataset_{}'.format(model_name, dataset_id)

        try:
            cf_matrix = confusion_matrix(y, (predictions > 0.5).astype("int32"))
            tn, fp, fn, tp = cf_matrix.ravel()
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            f1 = 2 * (precision * recall) / (precision + recall)

            data['precision'].append(precision)
            data['recall'].append(recall)
            data['f1'].append(f1)
            data['tn'].append(tn)
            data['fp'].append(fp)
            data['fn'].append(fn)
            data['tp'].append(tp)

            fig.add_subplot(i)
            plt.title('{}: {} to {}'.format(smell['name'], model_language, target_language))

            make_confusion_matrix(cf_matrix,
                                  group_names=['TN', 'FP', 'FN', 'TP'],
                                  categories=['No', 'Yes'],
                                  sum_stats=False)

            dataset.loc[:, 'predict_value'] = predictions
            dataset.loc[:, 'predict_class'] = (predictions > 0.5).astype("int32")
        except Exception as e:
            print(e)
            data['precision'].append(0)
            data['recall'].append(0)
            data['f1'].append(0)
            print('Fail to build MF')

        dataset.to_csv(os.path.join(RESULTS_DIR, 'predictions', output_name))

        # Update subplot coordinates
        i = i + 1

    plt.savefig(os.path.join(RESULTS_DIR, 'confusion_matrix', 'model_{}_dataset_{}.png'.format(model_name, dataset_id)))
    plt.close()


def perceptron(padding):
    np.random.seed(RANDOM_STATE)
    model = Sequential()
    model.add(Embedding(20000, 8, input_length=padding))
    model.add(Flatten())
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model


def train_all_samples(languages, dataset_name, smell, model_function, model_name, model_n=None):
    for language in languages:

        print('training model: {} {} {} {}'.format(language, smell['name'], dataset_name, model_name))

        dataset_path = os.path.join(TRAIN_DIR, '{}_{}_{}.csv'.format(language, smell['name'], dataset_name))

        if not os.path.exists(dataset_path):
            print('train dataset not found: {} {}'.format(smell['name'], language))
            continue

        dataset = pd.read_csv(dataset_path, index_col=False, dtype={'tokens': str})

        dataset['tokens'] = dataset['tokens'].map(lambda value: pre_process_token_str(value))

        x = dataset.iloc[:, -1]
        y = dataset.iloc[:, -2]

        x_train = padding_tokens(x.values, smell['padding_tokens'])
        y_train = y

        model = model_function(smell['padding_tokens'])

        model.fit(x_train, y_train, epochs=100, verbose=0)

        model.save(os.path.join(MODELS_DIR, '{}_{}_{}_{}'.format(language, model_name, len(x), smell['suffix'])))

        model_n[smell['name']].update({language: len(x)})

    return model_n


def transfer_learning(model_languages, target_language, model_name, model_n_sample):
    print('transfer learning: {} {}'.format(model_languages, target_language))

    data = init_data()

    for smell in SMELLS:
        print(smell['name'])
        for test in os.listdir(TEST_DIR):
            if test.startswith(target_language):
                dataset_path = os.path.join(TEST_DIR, test)
                dataset = pd.read_csv(os.path.join(dataset_path), index_col=False)

                dataset['tokens'] = dataset['tokens'].map(lambda value: pre_process_token_str(value))

                x = dataset.iloc[:, -1]
                y = dataset.iloc[:, -2]

                process(data, test, dataset, x, y, smell, model_languages, target_language, model_name, model_n_sample)

    return data


def train_n_samples(languages, n_samples, dataset_name, smell, model_function, model_name):
    for language in languages:
        for n in n_samples:
            name = '{}_{}_{}_{}'.format(language, model_name, n * 2, smell['suffix'])
            model_path = os.path.join(MODELS_DIR, name)

            if os.path.exists(model_path):
                continue

            print('training model (n samples): {} {} {} {} {}'.format(language, smell['name'], n * 2, dataset_name,
                                                                      model_name))

            dataset_path = os.path.join(TRAIN_DIR, '{}_{}_{}.csv'.format(language, smell['name'], dataset_name))

            if not os.path.exists(dataset_path):
                continue

            dataset = pd.read_csv(dataset_path)

            pos_smell_df = dataset.query('smell == 1')
            pos_size = len(pos_smell_df)
            neg_smell_df = dataset.query('smell == 0')
            neg_size = len(neg_smell_df)

            if pos_size < 2 * n or neg_size < 2 * n:
                print('Sample size too small, skipping')
                continue

            samples = select_samples(dataset, n)
            samples['tokens'] = samples['tokens'].map(lambda value: pre_process_token_str(value))

            x = samples.iloc[:, -1]
            y = samples.iloc[:, -2]

            x_train = padding_tokens(x.values, smell['padding_tokens'])
            y_train = y

            model = model_function(smell['padding_tokens'])

            model.fit(x_train, y_train, epochs=100, verbose=0)

            model.save(model_path)


def transfer_learning_n_samples(model_languages, target_language, dataset_name, smell, model_name):
    print('transfer learning (n samples): {} {} {}'.format(model_languages, target_language, smell['name']))

    data = init_data()

    for n in [4, 8, 16, 32, 64, 128, 256, 512]:
        tests = map(lambda t: t.format(target_language, smell['name'], dataset_name) + '.csv', [
            '{}_{}_{}',
        ])
        for test in tests:
            dataset_path = os.path.join(TEST_DIR, test)

            if not dataset_path:
                print('not exists', dataset_path)
                continue

            dataset = pd.read_csv(dataset_path, index_col=False)

            dataset['tokens'] = dataset['tokens'].map(lambda value: pre_process_token_str(value))

            x = dataset.iloc[:, -1]
            y = dataset.iloc[:, -2]

            process(data, test, dataset, x, y, smell, model_languages, target_language, model_name, n)

    return data


def cnn(padding):
    np.random.seed(RANDOM_STATE)
    model = Sequential()
    model.add(Embedding(20000, 8, input_length=padding))
    model.add(Conv1D(filters=32, kernel_size=8, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(10, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])

    return model


# TODO: Code starts here
# Training Percoptron models
model_n_dict = {}
for smell in SMELLS:
    model_n_dict.update({smell['name']: {}})
    model_n_size = train_all_samples(LANGUAGES, 'Train_1', smell, perceptron, 'perceptron1', model_n_dict)

# Transfer Learning
results = []

for target_language in LANGUAGES:
    results.append(transfer_learning(LANGUAGES, target_language, 'perceptron1', model_n_size))

# Saving the results of those models when evaluated using Test datasets
for result in results:
    append_data_file(result)

# RQ2:
dataset = pd.read_csv(os.path.join(RESULTS_DIR, 'data.csv'), index_col=False)
dataset = dataset.query("smell_name == 'ComplexMethod' and dataset.str.contains('ComplexMethod')", engine="python")
pd.set_option('display.max_rows', len(dataset) + 1)
dataset.sort_values(by=['f1'], ascending=True)

# RQ3: Training Perceptron models
for smell in SMELLS:
    train_n_samples(LANGUAGES, [2, 4, 8, 16, 32, 64, 128, 256], 'Train_1', smell, perceptron, 'perceptron1')

# Transfer Learning
results = []

for smell in SMELLS:
    for target_language in LANGUAGES:
        results.append(transfer_learning_n_samples(LANGUAGES, target_language, 'Test_1', smell, 'perceptron1'))

# Saving the results of those models when evaluated using Test datasets
for result in results:
    append_data_file(result)

# RQ4: Training CNN models
model_n_dict = {}
for smell in SMELLS:
    model_n_dict.update({smell['name']: {}})
    train_all_samples(LANGUAGES, 'Train_1', smell, cnn, 'cnn1', model_n_dict)

for smell in SMELLS:
    train_n_samples(LANGUAGES, [2, 4, 8, 16, 32, 64, 128, 256], 'Train_1', smell, cnn, 'cnn1')

# Transfer Learning
results = []

for smell in SMELLS:
    for target_language in LANGUAGES:
        results.append(transfer_learning_n_samples(LANGUAGES, target_language, 'Test_1', smell, 'cnn1'))

# Saving the results of those models when evaluated using Test datasets
for result in results:
    append_data_file(result)
