import pandas as pd
import csv
import ast
import os

path = 'CSVs'

# check whether directory already exists and if it does not, create it
if not os.path.exists(path):
    os.mkdir(path)
    print("Folder %s created!" % path)
else:
    print("Folder %s already exists" % path)

# Get data from csv file
df = pd.read_csv('tokenized_file.csv')
# Check how many languages there are
languages = df['language'].unique()

# Separate in individual Data Frames for each language
for language in languages:
    lang_df = df.loc[df['language'] == language]
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
            with open((path + '/' + file_name), mode, encoding="utf-8", newline='') as csvfile:
                fieldnames = ['id', 'language', 'text', 'smell', 'tokens']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header only if it's the first row
                if first_row:
                    writer.writeheader()

                # Check if each smell exist in that row and set format for jupyter notebooks
                if smells[smell]:
                    smell_val = 1
                else:
                    smell_val = 0

                writer.writerow({'id': csv_id, 'language': language, 'text': text, 'smell': smell_val, 'tokens': tokens})
