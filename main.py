import re

import pandas as pd

import psycopg2
from psycopg2 import Error

df = pd.read_csv('projects_patches.csv')

# print(df)
# print(df['project'].unique())

try:
    # Connect to an existing database
    connection = psycopg2.connect(user="postgres",
                                  password="1234",
                                  dbname="metrics")
    # Create a cursor to perform database operations
    cursor = connection.cursor()

    for index, row in df.iterrows():
        project_csv = row['project']
        file_path_csv = row['file_path']

        # Fetch result
        postgreSQL_select_Query = "SELECT * FROM class WHERE project = %s"
        cursor.execute(postgreSQL_select_Query, (project_csv,))
        record = cursor.fetchall()
        for path in record:
            split_paths = path[1].split('/', 6)
            split_path = split_paths[-1]
            if file_path_csv in split_path:
                hunk = re.findall("@@ (.*) @@", row['patch'])
                print(path)
                print(hunk)

    # Add smells result column IF IT DOES NOT EXIST
    # postgreSQL_alter_Query = "ALTER TABLE public.class ADD COLUMN smells jsonb"
    # cursor.execute(postgreSQL_alter_Query)
    # connection.commit()

    # Fetch result
    postgreSQL_select_Query = "SELECT * FROM public.class"
    cursor.execute(postgreSQL_select_Query)
    record = cursor.fetchone()

    # Get metrics for code smells
    metrics = record[9]
    smell_LCOM = metrics['PercentLackOfCohesion']
    smell_NOF = metrics['CountDeclClassVariable'] + metrics['CountDeclInstanceVariable']
    smell_NOM = metrics['CountDeclMethod']
    smell_NOPM = metrics['CountDeclMethodPublic']
    smell_WMC = metrics['SumCyclomaticModified']
    smell_NC = metrics['CountClassDerived']
    smell_LOC = metrics['CountLine']
    smell_CC = metrics['Cyclomatic']

    # Create original smells results with false as default before testing
    smells_results = {
        'MultifacetedAbstraction': False,
        'UnnecessaryAbstraction': False,
        'InsufficientModularization': False,
        'WideHierarchy': False,
        'LongMethod': False,
        'ComplexMethod': False
    }

    # Individual test for each smell
    if smell_LCOM >= 80 and smell_NOF >= 7 and smell_NOM >= 7:
        smells_results['MultifacetedAbstraction'] = True
    if smell_NOF >= 5 and smell_NOM == 0:
        smells_results['UnnecessaryAbstraction'] = True
    if smell_NOPM >= 20 or smell_NOM >= 30 or smell_WMC >= 100:
        smells_results['InsufficientModularization'] = True
    if smell_NC >= 10:
        smells_results['WideHierarchy'] = True
    if smell_LOC >= 100:
        smells_results['LongMethod'] = True
    if smell_CC >= 8:
        smells_results['ComplexMethod'] = True

    postgreSQL_alter_Query = "UPDATE TABLE public.class SET smells %s"
    cursor.execute(postgreSQL_alter_Query, (smells_results,))
    connection.commit()

    print(smells_results)

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
