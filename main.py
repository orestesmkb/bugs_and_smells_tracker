import re
import json

import pandas as pd

import psycopg2
from psycopg2 import Error

df = pd.read_csv('projects_patches.csv')

try:
    # Connect to an existing database
    connection = psycopg2.connect(user="postgres",
                                  password="1234",
                                  dbname="metrics")
    # Create a cursor to perform database operations
    cursor = connection.cursor()

    # Check if smells column already exists
    postgreSQL_exist_Query = "SELECT EXISTS (SELECT 1 FROM information_schema.columns " \
                             "WHERE table_name='class' AND column_name='smells')"
    cursor.execute(postgreSQL_exist_Query)
    exists_smells_column = cursor.fetchone()

    # Add smells result column if it does not exist
    if not exists_smells_column[0]:
        postgreSQL_alter_Query = "ALTER TABLE public.class ADD COLUMN smells jsonb"
        cursor.execute(postgreSQL_alter_Query)
        connection.commit()

    # Check if bug column already exists
    postgreSQL_exist_Query = "SELECT EXISTS (SELECT 1 FROM information_schema.columns " \
                             "WHERE table_name='class' AND column_name='bug')"
    cursor.execute(postgreSQL_exist_Query)
    exists_bug_column = cursor.fetchone()

    # Add bug boolean column if it does not exist, may be redundant if will only check smells for confirmed bug solves
    if not exists_bug_column[0]:
        postgreSQL_alter_Query = "ALTER TABLE public.class ADD COLUMN bug boolean"
        cursor.execute(postgreSQL_alter_Query)
        connection.commit()

    # Both checks for column existence could be a single function (future changes? maybe use [IF NOT EXISTS] option)

    for index, row in df.iterrows():
        project_csv = row['project']
        file_path_csv = row['file_path']

        # Fetch result if it's the same project name
        postgreSQL_select_Query = "SELECT * FROM public.class WHERE project = %s"
        cursor.execute(postgreSQL_select_Query, (project_csv,))
        record = cursor.fetchall()
        for case in record:
            split_paths = case[1].split('/', 6)
            path = split_paths[-1]
            if file_path_csv in path:
                # Findall to get only the numbers from all hunks, but separates in different tuples inside the list
                hunks = re.findall("@@ -(.*),(.*) [+](.*),(.*) @@", row['patch'])
                for hunk in hunks:
                    line_number = case[7]
                    first_start = int(hunk[0])
                    first_end = int(hunk[0]) + int(hunk[1])
                    second_start = int(hunk[2])
                    second_end = int(hunk[2]) + int(hunk[3])
                    if first_start <= line_number <= first_end or second_start <= line_number <= second_end:
                        # Get metrics for code smells
                        metrics = case[9]
                        smell_LCOM = metrics['PercentLackOfCohesion']
                        smell_NOF = metrics['CountDeclClassVariable'] + metrics['CountDeclInstanceVariable']
                        smell_NOM = metrics['CountDeclMethod']
                        smell_NOPM = metrics['CountDeclMethodPublic']
                        smell_WMC = metrics['SumCyclomaticModified']
                        smell_NC = metrics['CountClassDerived']
                        smell_LOC = metrics['CountLine']  # Add method table here too?
                        smell_CC = metrics['AvgCyclomatic']  # Change for method table

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

                        # Update database with the test for smells results
                        postgreSQL_alter_Query = "UPDATE public.class SET smells = %s WHERE id = %s"
                        cursor.execute(postgreSQL_alter_Query, (json.dumps(smells_results), case[0]))
                        connection.commit()

                        # Update database marking as a bug fix commit
                        postgreSQL_alter_Query = "UPDATE public.class SET bug = %s WHERE id = %s"
                        cursor.execute(postgreSQL_alter_Query, (True, case[0]))
                        connection.commit()

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
