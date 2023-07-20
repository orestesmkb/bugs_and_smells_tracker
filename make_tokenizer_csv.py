import csv

import psycopg2
from psycopg2 import Error

# This scrip generates a csv file with all necessary data to generate tokens via tokenizer on Linux

# Connect to an existing database
connection = psycopg2.connect(user='postgres',
                              password='1234',
                              dbname='metrics')
# Create a cursor to perform database operations
cursor = connection.cursor()

# Fetch classes if it's the same project name and file path as in the csv row
postgreSQL_select_Query = "SELECT * FROM public.class WHERE bug_fix = %s"
cursor.execute(postgreSQL_select_Query, ('true',))
bugs = cursor.fetchall()

try:

    with open('tokenizer_data.csv', 'w', encoding="utf-8", newline='') as csvfile:
        fieldnames = ['id', 'language', 'text', 'smells']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for bug in bugs:
            db_id = bug[0]
            db_language = bug[2]
            db_content = bug[8]
            db_smells = bug[13]
            if db_id < 0 or db_language == '' or db_content == '' or db_smells == {}:
                continue
            writer.writerow({'id': db_id, 'language': db_language, 'text': db_content, 'smells': db_smells})

except (Exception, Error) as error:
    print('Error while connecting to PostgreSQL', error)

finally:
    if connection:
        cursor.close()
        connection.close()
