from sklearn.model_selection import train_test_split
import pandas as pd
import csv
import ast
import os


def create_folders(folder_path='csv files', additional_folders=None):
    # This function will check if a folder exists, if it does not it will create one with the path from the input
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        if additional_folders is not None:
            for additional_folder in additional_folders:
                additional_folder_path = os.path.join(folder_path, additional_folder)
                os.mkdir(additional_folder_path)
        print("Folder %s created!" % folder_path)
    else:
        print("Folder %s already exists" % folder_path)


# check whether directory already exists and if it does not, create it
create_folders('csv files')

bug_fix_path = os.path.join('csv files', 'bug fix')
create_folders(bug_fix_path, ('all', 'train', 'test'))

harmful_clean_path = os.path.join('csv files', 'harmful-clean')
create_folders(harmful_clean_path, ('all', 'train', 'test'))

harmful_bug_path = os.path.join('csv files', 'harmful-bug')
create_folders(harmful_bug_path, ('all', 'train', 'test'))

case_A_path = os.path.join('csv files', 'case A - Smell to Bug')
create_folders(case_A_path, ('all', 'train', 'test'))

case_B_path = os.path.join('csv files', 'case B - Bug to Smell')
create_folders(case_B_path, ('all', 'train', 'test'))

# Get data from csv file
print(' ')
print('Largest token size:')
print(' ')

print('bug fix:')
df = pd.read_csv(r'csv files\bug_tokenized.csv')
split_tokens = df.tokens.str.split(' ')
print(split_tokens.str.len().max())

print('harmful code:')
df1 = pd.read_csv(r'csv files\harmful_tokenized.csv')
split_tokens = df1.tokens.str.split(' ')
print(split_tokens.str.len().max())

print('clean code:')
df2 = pd.read_csv(r'csv files\clean_tokenized.csv')
split_tokens = df2.tokens.str.split(' ')
print(split_tokens.str.len().max())

print('bug fix without smells:')
df3 = pd.read_csv(r'csv files\bug_without_smells_tokenized.csv')
split_tokens = df3.tokens.str.split(' ')
print(split_tokens.str.len().max())

print('not bug fix with smells:')
df4 = pd.read_csv(r'csv files\not_bug_with_smells_tokenized.csv')
split_tokens = df4.tokens.str.split(' ')
print(split_tokens.str.len().max())
print(' ')

# Check how many languages there are
languages = df['language'].unique()
smells = {}

# Separate in individual Data Frames for each language
for language in languages:
    lang_df = df.loc[df['language'] == language]
    lang_df1 = df1.loc[df1['language'] == language]
    lang_df2 = df2.loc[df2['language'] == language]
    lang_df3 = df3.loc[df3['language'] == language]
    lang_df4 = df4.loc[df4['language'] == language]
    print(' ')
    print('[' + language + ']')
    print('bug fix cases:')
    print(len(lang_df))
    print('harmful code cases:')
    print(len(lang_df1))
    print('clean code cases:')
    print(len(lang_df2))
    print('bug without smells code cases:')
    print(len(lang_df3))
    print('Not bug fix with smells code cases:')
    print(len(lang_df4))

    first_row = True

    # TODO: Turn the file saving into a function

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

    # TODO: Turn these 3 into a function
    file_name3 = language + '_' + 'BugWithoutSmells' + '.csv'

    # Open file inside new directory
    with open((harmful_bug_path + '\\all\\' + file_name3), 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smell', 'tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in lang_df3.iterrows():
            csv_id3 = row['id']
            text3 = row['text']
            tokens3 = row['tokens']
            smells3 = ast.literal_eval(row['smells'])
            if any(smells3.values()):
                print('Error: row in data for bug without smells code with at least one smell')
                break
            smell_val3 = 0

            writer.writerow(
                {'id': csv_id3, 'language': language, 'text': text3, 'smell': smell_val3, 'tokens': tokens3})

    # Open file inside new directory
    with open((case_A_path + '\\all\\' + file_name3), 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smell', 'tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in lang_df3.iterrows():
            csv_id3 = row['id']
            text3 = row['text']
            tokens3 = row['tokens']
            smells3 = ast.literal_eval(row['smells'])
            if any(smells3.values()):
                print('Error: row in data for bug without smells code with at least one smell')
                break
            smell_val3 = 1

            writer.writerow(
                {'id': csv_id3, 'language': language, 'text': text3, 'smell': smell_val3, 'tokens': tokens3})

    # Open file inside new directory
    with open((case_B_path + '\\all\\' + file_name3), 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smell', 'tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in lang_df3.iterrows():
            csv_id3 = row['id']
            text3 = row['text']
            tokens3 = row['tokens']
            smells3 = ast.literal_eval(row['smells'])
            if any(smells3.values()):
                print('Error: row in data for bug without smells code with at least one smell')
                break
            smell_val3 = 1

            writer.writerow(
                {'id': csv_id3, 'language': language, 'text': text3, 'smell': smell_val3, 'tokens': tokens3})

    # TODO: Turn these 2 into a function
    file_name4 = language + '_' + 'NotBugWithSmells' + '.csv'

    # Open file inside new directory
    with open((case_A_path + '\\all\\' + file_name4), 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smell', 'tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in lang_df4.iterrows():
            csv_id4 = row['id']
            text4 = row['text']
            tokens4 = row['tokens']
            smells4 = ast.literal_eval(row['smells'])
            if not any(smells4.values()):
                print('Error: row in data for non bug fix with smells code with no smells')
                break
            smell_val4 = 1

            writer.writerow(
                {'id': csv_id4, 'language': language, 'text': text4, 'smell': smell_val4, 'tokens': tokens4})

    # Open file inside new directory
    with open((case_B_path + '\\all\\' + file_name4), 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smell', 'tokens']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in lang_df4.iterrows():
            csv_id4 = row['id']
            text4 = row['text']
            tokens4 = row['tokens']
            smells4 = ast.literal_eval(row['smells'])
            if not any(smells4.values()):
                print('Error: row in data for non bug fix with smells code with no smells')
                break
            smell_val4 = 1

            writer.writerow(
                {'id': csv_id4, 'language': language, 'text': text4, 'smell': smell_val4, 'tokens': tokens4})

    # TODO: Analyse if this can also be a a part of the function for the cases above
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
    # TODO: Turn this into a function
    harmful_name = language + '_' + 'Harmful'
    open_path = harmful_clean_path + '\\all\\' + harmful_name + '.csv'
    harmful_df = pd.read_csv(open_path)

    clean_name = language + '_' + 'Clean'
    open_path = harmful_clean_path + '\\all\\' + clean_name + '.csv'
    clean_df = pd.read_csv(open_path)

    # Check witch case is smaller and use its length
    if len(harmful_df) < len(clean_df):
        clean_df_harmful_vs_clean = clean_df[clean_df.index < len(harmful_df)]
        harmful_df_harmful_vs_clean = harmful_df
    else:
        harmful_df_harmful_vs_clean = harmful_df[harmful_df.index < len(clean_df)]
        clean_df_harmful_vs_clean = clean_df

    train1hc, test1hc = train_test_split(clean_df_harmful_vs_clean, test_size=0.2)
    train2hc, test2hc = train_test_split(harmful_df_harmful_vs_clean, test_size=0.2)

    bug_without_smells_name = language + '_' + 'BugWithoutSmells'
    open_path = harmful_bug_path + '\\all\\' + bug_without_smells_name + '.csv'
    bug_without_smells_df = pd.read_csv(open_path)

    # TODO: Turn this into a function
    # Check witch case is smaller and use its length
    if len(harmful_df) < len(bug_without_smells_df):
        bug_without_smells_df_harmful_vs_bug = bug_without_smells_df[bug_without_smells_df.index < len(harmful_df)]
        harmful_df_harmful_vs_bug = harmful_df
    else:
        harmful_df_harmful_vs_bug = harmful_df[harmful_df.index < len(bug_without_smells_df)]
        bug_without_smells_df_harmful_vs_bug = bug_without_smells_df

    train1hb, test1hb = train_test_split(harmful_df_harmful_vs_bug, test_size=0.2)
    train2hb, test2hb = train_test_split(bug_without_smells_df_harmful_vs_bug, test_size=0.2)

    not_bug_with_smells_name = language + '_' + 'NotBugWithSmells'
    open_path = case_A_path + '\\all\\' + not_bug_with_smells_name + '.csv'
    not_bug_with_smells_df = pd.read_csv(open_path)

    bug_without_smells_name = language + '_' + 'BugWithoutSmells'
    open_path = case_A_path + '\\all\\' + bug_without_smells_name + '.csv'
    bug_without_smells_df = pd.read_csv(open_path)

    # Check witch case is smaller and use its length
    if len(not_bug_with_smells_df) < len(bug_without_smells_df):
        bug_without_smells_df_case_a = bug_without_smells_df[bug_without_smells_df.index < len(not_bug_with_smells_df)]
        not_bug_with_smells_df_case_a = not_bug_with_smells_df
        clean_df_ca = clean_df[clean_df.index < len(not_bug_with_smells_df)]
    else:
        not_bug_with_smells_df_case_a = not_bug_with_smells_df[not_bug_with_smells_df.index < len(bug_without_smells_df)]
        bug_without_smells_df_case_a = bug_without_smells_df
        clean_df_ca = clean_df[clean_df.index < len(bug_without_smells_df)]

    train1A, test1B = train_test_split(not_bug_with_smells_df_case_a, test_size=0.2)
    train1B, test1A = train_test_split(bug_without_smells_df_case_a, test_size=0.2)
    train2B, test2B = train_test_split(clean_df_ca, test_size=0.2)
    train2A, test2A = train_test_split(clean_df_ca, test_size=0.2)

    concat_trainA = pd.concat([train1A, train2A])
    concat_testA = pd.concat([test1A, test2A])

    file_name = language + '_' + 'SmellToBug'
    header = ['id', 'language', 'text', 'smell', 'tokens']
    train_path = case_A_path + '\\train\\' + file_name + '_Train_1.csv'
    concat_trainA.to_csv(train_path, header=header, encoding='utf-8', index=False)
    test_path = case_A_path + '\\test\\' + file_name + '_Test_1.csv'
    concat_testA.to_csv(test_path, header=header, encoding='utf-8', index=False)

    concat_trainB = pd.concat([train1B, train2B])
    concat_testB = pd.concat([test1B, test2B])

    file_name = language + '_' + 'BugToSmell'
    header = ['id', 'language', 'text', 'smell', 'tokens']
    train_path = case_B_path + '\\train\\' + file_name + '_Train_1.csv'
    concat_trainB.to_csv(train_path, header=header, encoding='utf-8', index=False)
    test_path = case_B_path + '\\test\\' + file_name + '_Test_1.csv'
    concat_testB.to_csv(test_path, header=header, encoding='utf-8', index=False)

    concat_train1 = pd.concat([train1hc, train2hc])
    concat_test1 = pd.concat([test1hc, test2hc])

    file_name = language + '_' + 'HarmfulVsClean'
    header = ['id', 'language', 'text', 'smell', 'tokens']
    train_path = harmful_clean_path + '\\train\\' + file_name + '_Train_1.csv'
    concat_train1.to_csv(train_path, header=header, encoding='utf-8', index=False)
    test_path = harmful_clean_path + '\\test\\' + file_name + '_Test_1.csv'
    concat_test1.to_csv(test_path, header=header, encoding='utf-8', index=False)

    concat_train2 = pd.concat([train1hb, train2hb])
    concat_test2 = pd.concat([test1hb, test2hb])

    file_name = language + '_' + 'HarmfulVsBug'
    header = ['id', 'language', 'text', 'smell', 'tokens']
    train_path = harmful_bug_path + '\\train\\' + file_name + '_Train_1.csv'
    concat_train2.to_csv(train_path, header=header, encoding='utf-8', index=False)
    test_path = harmful_bug_path + '\\test\\' + file_name + '_Test_1.csv'
    concat_test2.to_csv(test_path, header=header, encoding='utf-8', index=False)

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
