import pandas as pd

df = pd.read_csv('data.csv')

df = df[df['model'].str.contains('perceptron1')]

model_languages = df['model_language'].unique()

for language in model_languages:
    lang_df = df.loc[df['model_language'] == language]
    max_f1 = lang_df[lang_df['f1'] == lang_df['f1'].max()]
    max_f1.drop(['model', 'dataset', 'smell_name', 'target_language', 'n_test_samples', 'n_train_samples', 'tn', 'fp', 'tp','fn'], axis=1, inplace=True)
    print(max_f1.to_latex())
