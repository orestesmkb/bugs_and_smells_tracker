import csv
import pandas as pd
import psycopg2
from psycopg2 import Error

# Connect to an existing database
connection = psycopg2.connect(user='postgres',
                              password='1234',
                              dbname='metrics')
# Create a cursor to perform database operations
cursor = connection.cursor()

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


for language in languages:
    print(' ')
    print(language)
    lang_df = df[df["language"] == language]
    projects = lang_df['project'].unique()
    for project in projects:
        print(project + ':')
        # Get amount for each language
        project_size = len(lang_df[lang_df["project"] == project])
        print(project_size)
