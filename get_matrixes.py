import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from cf_matrix import make_confusion_matrix


def plot_cf_matrix(max_df, last):

    # fig, ax = plt.subplots(2, 2)
    plt.figure(figsize=(5, 5))

    tn = max_df.iloc[0]['tn']
    fp = max_df.iloc[0]['fp']
    fn = max_df.iloc[0]['fn']
    tp = max_df.iloc[0]['tp']
    model_language = max_df.iloc[0]['model_language']
    target_language = max_df.iloc[0]['target_language']
    smell_name = max_df.iloc[0]['smell_name']
    model = max_df.iloc[0]['model']
    dataset = max_df.iloc[0]['dataset']
    cf_matrix = np.array([[tn, fp], [fn, tp]])

    make_confusion_matrix(cf_matrix,
                          group_names=['TN', 'FP', 'FN', 'TP'],
                          categories=['No', 'Yes'],
                          sum_stats=False)

    if last:
        plt.title('{}: {} to {}'.format('All Smells', model_language, target_language))
        plt.savefig(os.path.join('resultados paper', 'gerais', 'model_{}_dataset_{}.png'.format(model, dataset)))
    else:
        plt.title('{}: {} to {}'.format(smell_name, model_language, target_language))
        plt.savefig(os.path.join('resultados paper', 'model_{}_dataset_{}.png'.format(model, dataset)))
    plt.close()


df = pd.read_csv('data.csv')
df.drop(df[df.model_language == df.target_language].index, inplace=True)
model_languages = df['model_language'].unique()
smells = df['smell_name'].unique()

for language in model_languages:
    lang_df = df.loc[df['model_language'] == language]
    target_languages = lang_df['target_language'].unique()

    for lang2 in target_languages:
        lang_df2 = lang_df.loc[lang_df['target_language'] == lang2]

        all_tn = 0
        all_fp = 0
        all_fn = 0
        all_tp = 0

        for smell in smells:
            smell_df = lang_df2.loc[lang_df2['smell_name'] == smell]
            max_f1 = smell_df[smell_df['f1'] == smell_df['f1'].max()]
            if max_f1.empty:
                continue

            tn = max_f1.iloc[0]['tn']
            all_tn = all_tn + tn
            fp = max_f1.iloc[0]['fp']
            all_fp = all_fp + fp
            fn = max_f1.iloc[0]['fn']
            all_fn = all_fn + fn
            tp = max_f1.iloc[0]['tp']
            all_tp = all_tp + tp

            plot_cf_matrix(max_f1, False)

        else:
            max_f1 = lang_df2[lang_df2['f1'] == lang_df2['f1'].max()]
            max_f1['tn'] = all_tn
            max_f1['fp'] = all_fp
            max_f1['fn'] = all_fn
            max_f1['tp'] = all_tp
            plot_cf_matrix(max_f1, True)
