from sklearn.model_selection import train_test_split
import pandas as pd
import csv
import ast
import os


def create_folder(folder_path):
    # This function will check if a folder exists, if it does not it will create one with the path from the input
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        print("Folder %s created!" % folder_path)
    else:
        print("Folder %s already exists" % folder_path)


# check whether directory already exists and if it does not, create it
create_folder('all')
create_folder('train')
create_folder('test')

# Get data from csv file
df = pd.read_csv('tokenized_file.csv')
# Check how many languages there are
languages = df['language'].unique()

# Separate in individual Data Frames for each language
for language in languages:
    lang_df = df.loc[df['language'] == language]
    print(language)
    print(len(lang_df))
    first_row = True

    # Loop each row to get data
    for index, row in lang_df.iterrows():
        csv_id = row['id']
        text = row['text']
        tokens = row['tokens']
        smells = ast.literal_eval(row['smells'])

        # Create file for each smell type
        for smell in smells:
            file_name = language + '_' + smell + '.csv'

            # Overwrite file if it's the first row
            if first_row:
                mode = 'w'
            else:
                mode = 'a'

            # Open file inside new directory
            with open(('all/' + file_name), mode, encoding="utf-8", newline='') as csvfile:
                fieldnames = ['id', 'language', 'text', 'smell', 'tokens']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header only if it's the first row
                if first_row:
                    writer.writeheader()
                    first_row = False

                # Check if each smell exist in that row and set format for jupyter notebooks
                if smells[smell]:
                    smell_val = 1
                else:
                    smell_val = 0

                writer.writerow(
                    {'id': csv_id, 'language': language, 'text': text, 'smell': smell_val, 'tokens': tokens})

for language in languages:
    for smell in smells:
        # Get data from csv file
        file_name = language + '_' + smell
        open_path = 'all/' + file_name + '.csv'
        open_df = pd.read_csv(open_path)
        train, test = train_test_split(open_df, test_size=0.2)
        header = ['id', 'language', 'text', 'smell', 'tokens']
        train_path = 'train/' + file_name + '_Train_1.csv'
        train.to_csv(train_path, header=header, encoding='utf-8', index=False)
        test_path = 'test/' + file_name + '_Test_1.csv'
        test.to_csv(test_path, header=header, encoding='utf-8', index=False)
