import csv
import pandas as pd
import psycopg2
from psycopg2 import Error
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

# This scrip generates a csv file with all necessary data to generate tokens via tokenizer

# Connect to an existing database
connection = psycopg2.connect(user='postgres',
                              password='1234',
                              dbname='metrics')
# Create a cursor to perform database operations
cursor = connection.cursor()

# Fetch all cases that are a bug fix
postgreSQL_select_Query = "SELECT * FROM public.class WHERE bug_fix = %s"
cursor.execute(postgreSQL_select_Query, ('true',))
bugs = cursor.fetchall()

try:

    with open('csv files\\bug_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        count = 0

        for bug in bugs:
            db_id = bug[0]
            db_language = bug[2]
            db_content = bug[8]
            db_smells = bug[13]
            db_project = bug[3]
            if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                continue
            count += 1
            writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells, 'project': db_project})
        else:
            print(' ')
            print('All bug fix cases sorted, ' + str(count) + ' total cases saved.')
            print(count)

    with open('csv files\\harmful_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        count = 0

        for bug in bugs:
            db_id = bug[0]
            db_language = bug[2]
            db_content = bug[8]
            db_smells = bug[13]
            db_project = bug[3]
            if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                continue
            if not any(db_smells.values()):
                continue
            count += 1
            writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells, 'project': db_project})
        else:
            print(' ')
            print('All harmful cases sorted, ' + str(count) + ' total cases saved.')
            print(count)

    with open('csv files\\clean_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        # Get data from csv file
        df = pd.read_csv('csv files\\harmful_tokenizer_data.csv')
        # Check how many languages there are
        languages = df['language'].unique()

        print(' ')
        print('Attempting to get same amount of clean cases based on amount of harmful cases:')
        print(' ')

        for language in languages:
            # Get amount for each language
            lang_size = len(df[df["language"] == language])

            # Fetch all cases that are not a bug fix for each language
            postgreSQL_select_Query = "SELECT * FROM public.class WHERE bug_fix = %s and language = %s"
            cursor.execute(postgreSQL_select_Query, ('false', language))
            clean = cursor.fetchall()
            count = 0

            for case in clean:
                smells = case[13]
                if any(smells.values()):
                    continue
                else:
                    db_id = case[0]
                    db_language = case[2]
                    db_content = case[8]
                    db_smells = case[13]
                    db_project = case[3]
                    if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                        continue
                    writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells, 'project': db_project})
                    count += 1
                    if count == lang_size:
                        print('Amount of cases for ' + language + ' reached, ' + str(count) + ' total cases saved.')
                        break
            else:
                print('Not enough cases for ' + language + ', only ' + str(count) + ' total cases saved.')

except (Exception, Error) as error:
    print(' ')
    print('Error while connecting to PostgreSQL', error)

finally:
    if connection:
        cursor.close()
        print(' ')
        print('PostgreSQL connection is closed')
        connection.close()
