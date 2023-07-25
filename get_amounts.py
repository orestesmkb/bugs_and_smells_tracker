import pandas as pd
import psycopg2
from psycopg2 import Error

# Connect to an existing database
connection = psycopg2.connect(user='postgres',
                              password='1234',
                              dbname='metrics')
# Create a cursor to perform database operations
cursor = connection.cursor()

try:

    df2 = pd.read_csv('projects_patches.csv')
    projects1 = df2['project'].unique()
    print('PROJECT PATCHES CSV:')
    print(projects1)
    print(' ')

    # Fetch all cases that are a bug fix
    postgreSQL_select_Query = "SELECT DISTINCT project FROM public.class"
    cursor.execute(postgreSQL_select_Query)
    projects2 = cursor.fetchall()
    print('POSTGRESQL:')
    print(projects2)
    print(' ')

    df = pd.read_csv('bug_tokenizer_data.csv')
    languages = df['language'].unique()
    print('BUG TOKENIZER DATA CSV:')
    print(df['project'].unique())
    print(' ')
    print('Number of cases with bug fixes:')

    for language in languages:
        print(' ')
        print(language)
        lang_df = df[df["language"] == language]
        projects = lang_df['project'].unique()
        for project in projects:
            print(project + ':')
            project_size = len(lang_df[lang_df["project"] == project])
            print(project_size)

    print(' ')
    print('Number of cases with smells:')

    for language in languages:
        print(' ')
        print(language)
        lang_df = df[df["language"] == language]
        projects = lang_df['project'].unique()
        for project in projects:
            smells_sum = 0
            postgreSQL_select_Query = "SELECT * FROM public.class WHERE language = %s AND project = %s AND smells IS NOT NULL"
            cursor.execute(postgreSQL_select_Query, (language, project))
            cases = cursor.fetchall()
            for case in cases:
                smells = case[13]
                for value in smells.values():
                    if value:
                        smells_sum += 1
            print(project + ':')
            print(smells_sum)

except (Exception, Error) as error:
    print('Error while connecting to PostgreSQL', error)

finally:
    if connection:
        cursor.close()
        print('PostgreSQL connection is closed')
        connection.close()
