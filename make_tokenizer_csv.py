import csv
import pandas as pd
import psycopg2
from psycopg2 import Error

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

    with open('bug_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for bug in bugs:
            db_id = bug[0]
            db_language = bug[2]
            db_content = bug[8]
            db_smells = bug[13]
            db_project = bug[3]
            if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                continue
            writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells, 'project': db_project})

    with open('not_bug_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        # Get data from csv file
        df = pd.read_csv('bug_tokenizer_data.csv')
        # Check how many languages there are
        languages = df['language'].unique()

        for language in languages:
            # Get amount for each language
            lang_size = len(df[df["language"] == language])

            # Fetch all cases that are not a bug fix for each language
            postgreSQL_select_Query = "SELECT * FROM public.class WHERE bug_fix = %s and language = %s"
            cursor.execute(postgreSQL_select_Query, ('false', language))
            not_bugs = cursor.fetchall()
            count = 0

            for case in not_bugs:
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
                        break
            else:
                print('Not enough cases for ' + language + ', only ' + str(count) + ' total cases.')

except (Exception, Error) as error:
    print('Error while connecting to PostgreSQL', error)

finally:
    if connection:
        cursor.close()
        connection.close()
