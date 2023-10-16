from create_folders import create_folders
import csv
import psycopg2
from psycopg2 import Error

# check whether directory already exists and if it does not, create it
create_folders('csv files', ('tokenizer data', 'tokenized'))

# This scrip generates a csv file with all necessary data to generate tokens via tokenizer

# Connect to an existing database
connection = psycopg2.connect(user='postgres',
                              password='1234',
                              dbname='metrics')
# Create a cursor to perform database operations
cursor = connection.cursor()

try:

    # Fetch all cases that are a bug fix
    postgreSQL_select_Query = "SELECT * FROM public.class WHERE bug_fix = %s"
    cursor.execute(postgreSQL_select_Query, ('true',))
    cases = cursor.fetchall()

    with open('csv files\\tokenizer data\\bug_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        counter = 0

        for case in cases:
            db_id = case[0]
            db_language = case[2]
            db_content = case[8]
            db_smells = case[13]
            db_project = case[3]
            # If there are any invalid values in that row skip it
            if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                continue
            counter += 1
            writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells, 'project': db_project})
        else:
            print(' ')
            print('All bug fix cases sorted, ' + str(counter) + ' total cases.')

    with open('csv files\\tokenizer data\\harmful_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        counter = 0

        for case in cases:
            db_id = case[0]
            db_language = case[2]
            db_content = case[8]
            db_smells = case[13]
            db_project = case[3]
            # If there are any invalid values in that row skip it
            if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                continue
            # If there are no smells in row, skip it
            if not any(db_smells.values()):
                continue
            writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells, 'project': db_project})
            counter += 1
        else:
            print(' ')
            print('All harmful cases sorted, ' + str(counter) + ' total cases.')

    with open('csv files\\tokenizer data\\bug_without_smells_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        counter = 0

        for case in cases:
            db_id = case[0]
            db_language = case[2]
            db_content = case[8]
            db_smells = case[13]
            db_project = case[3]
            # If there are any invalid values in that row skip it
            if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                continue
            # If there are smells in row, skip it
            if any(db_smells.values()):
                continue
            writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells, 'project': db_project})
            counter += 1
        else:
            print(' ')
            print('All bug fix without smells cases sorted, ' + str(counter) + ' total cases.')

    # Fetch all cases that are not a bug fix for each language
    postgreSQL_select_Query = "SELECT * FROM public.class WHERE bug_fix = %s"
    cursor.execute(postgreSQL_select_Query, ('false',))
    cases = cursor.fetchall()

    with open('csv files\\tokenizer data\\clean_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        counter = 0

        for case in cases:
            db_id = case[0]
            db_language = case[2]
            db_content = case[8]
            db_smells = case[13]
            db_project = case[3]
            # If there are any invalid values in that row skip it
            if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                continue
            # If there are smells in row, skip it
            if any(db_smells.values()):
                continue
            writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells, 'project': db_project})
            counter += 1
        else:
            print(' ')
            print('All clean code cases sorted, ' + str(counter) + ' total cases.')

    with open('csv files\\tokenizer data\\not_bug_with_smells_tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells', 'project']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        count = 0

        for case in cases:
            db_id = case[0]
            db_language = case[2]
            db_content = case[8]
            db_smells = case[13]
            db_project = case[3]
            # If there are any invalid values in that row skip it
            if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                continue
            # If there are no smells in row, skip it
            if not any(db_smells.values()):
                continue
            writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells, 'project': db_project})
            count += 1
        else:
            print(' ')
            print('All non bug fix with smells cases sorted, ' + str(count) + ' total cases.')

except (Exception, Error) as error:
    print(' ')
    print('Error while connecting to PostgreSQL', error)

finally:
    if connection:
        cursor.close()
        print(' ')
        print('PostgreSQL connection is closed')
        connection.close()
