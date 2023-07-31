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
create_folder('csv files')
bug_fix_path = r'csv files\bug fix'
create_folder(bug_fix_path)
create_folder(bug_fix_path + '\\all')
create_folder(bug_fix_path + '\\train')
create_folder(bug_fix_path + '\\test')
harmful_clean_path = r'csv files\harmful-clean'
create_folder(harmful_clean_path)
create_folder(harmful_clean_path + '\\all')
create_folder(harmful_clean_path + '\\train')
create_folder(harmful_clean_path + '\\test')

# Get data from csv file
df = pd.read_csv(r'csv files\bug_tokenized_file.csv')
df1 = pd.read_csv(r'csv files\harmful_tokenized_file.csv')
df2 = pd.read_csv(r'csv files\clean_tokenized_file.csv')
# Check how many languages there are
languages = df['language'].unique()
smells = {}

# Separate in individual Data Frames for each language
for language in languages:
    lang_df = df.loc[df['language'] == language]
    lang_df1 = df1.loc[df1['language'] == language]
    lang_df2 = df2.loc[df2['language'] == language]
    print(' ')
    print(language)
    print('bug fix cases:')
    print(len(lang_df))
    print(' ')
    print('harmful code cases:')
    print(len(lang_df1))
    print('')
    print('clean code cases:')
    print(len(lang_df2))
    first_row = True

    # TODO: Too much repetition on the harmful/clean code, maybe could become a function

    file_name1 = language + '_' + 'Harmful' + '.csv'

    # Open file inside new directory
    with open((harmful_clean_path + '\\all\\' + file_name1), 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smell', 'tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in lang_df1.iterrows():
            csv_id1 = row['id']
            text1 = row['text']
            tokens1 = row['tokens']
            smells1 = ast.literal_eval(row['smells'])
            if not any(smells1.values()):
                print('Error: row in data for harmful code without at least one smell')
                break
            smell_val1 = 1

            writer.writerow(
                {'id': csv_id1, 'language': language, 'text': text1, 'smell': smell_val1, 'tokens': tokens1})

    file_name2 = language + '_' + 'Clean' + '.csv'

    # Open file inside new directory
    with open((harmful_clean_path + '\\all\\' + file_name2), 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smell', 'tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in lang_df2.iterrows():
            csv_id2 = row['id']
            text2 = row['text']
            tokens2 = row['tokens']
            smells2 = ast.literal_eval(row['smells'])
            if any(smells2.values()):
                print('Error: row in data for clean code with at least one smell')
                break
            smell_val2 = 0

            writer.writerow(
                {'id': csv_id2, 'language': language, 'text': text2, 'smell': smell_val2, 'tokens': tokens2})

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
            with open((bug_fix_path + '\\all\\' + file_name), mode, encoding="utf-8", newline='') as csvfile:
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
    # TODO: Turn this into a function?
    harmful_name = language + '_' + 'Harmful'
    open_path = harmful_clean_path + '\\all\\' + harmful_name + '.csv'
    harmful_df = pd.read_csv(open_path)
    train1, test1 = train_test_split(harmful_df, test_size=0.2)

    clean_name = language + '_' + 'Clean'
    open_path = harmful_clean_path + '\\all\\' + clean_name + '.csv'
    clean_df = pd.read_csv(open_path)
    train2, test2 = train_test_split(clean_df, test_size=0.2)

    train = pd.concat([train1, train2])
    test = pd.concat([test1, test2])

    print(train)
    print(test)

    file_name = language + '_' + 'HarmfulCode'
    header = ['id', 'language', 'text', 'smell', 'tokens']
    train_path = harmful_clean_path + '\\train\\' + file_name + '_Train_1.csv'
    train.to_csv(train_path, header=header, encoding='utf-8', index=False)
    test_path = harmful_clean_path + '\\test\\' + file_name + '_Test_1.csv'
    test.to_csv(test_path, header=header, encoding='utf-8', index=False)

    for smell in smells:
        # Get data from csv file
        file_name = language + '_' + smell
        open_path = bug_fix_path + '\\all\\' + file_name + '.csv'
        open_df = pd.read_csv(open_path)
        train, test = train_test_split(open_df, test_size=0.2)
        header = ['id', 'language', 'text', 'smell', 'tokens']
        train_path = bug_fix_path + '\\train\\' + file_name + '_Train_1.csv'
        train.to_csv(train_path, header=header, encoding='utf-8', index=False)
        test_path = bug_fix_path + '\\test\\' + file_name + '_Test_1.csv'
        test.to_csv(test_path, header=header, encoding='utf-8', index=False)
