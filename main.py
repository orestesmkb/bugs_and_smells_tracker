import re
import json

import time
from tqdm.auto import tqdm

import pandas as pd

import psycopg2
from psycopg2 import Error

start = time.time()

df = pd.read_csv('projects_patches.csv')

counter_success = 0
counter_total = 0

# Connect to an existing database
connection = psycopg2.connect(user='postgres',
                              password='1234',
                              dbname='metrics')
# Create a cursor to perform database operations
cursor = connection.cursor()


def if_not_exist_create_column(table_name, column_name, data_type):
    psql_exist_query = 'SELECT EXISTS (SELECT 1 FROM information_schema.columns ' \
                       'WHERE table_name = %s AND column_name = %s)'
    cursor.execute(psql_exist_query, (table_name, column_name))
    exists_smells_column = cursor.fetchone()

    if not exists_smells_column[0]:
        psql_alter_query = 'ALTER TABLE %s ADD COLUMN %s %s'
        cursor.execute(psql_alter_query, (table_name, column_name, data_type))
        connection.commit()


try:
    # Check if smells column exists and create it if it does not exist yet
    # if_not_exist_create_column('class', 'smells', 'jsonb')
    # Check if bug_fix column exists and create it if it does not exist yet
    # if_not_exist_create_column('class', 'bug_fix', 'boolean')

    # psql_alter_query = 'ALTER TABLE public.class ADD COLUMN smells jsonb'
    # cursor.execute(psql_alter_query)
    # connection.commit()
    # psql_alter_query = 'ALTER TABLE public.class ADD COLUMN bug_fix boolean'
    # cursor.execute(psql_alter_query)
    # connection.commit()

    # Loop for all rows in the csv file
    for index, row in tqdm(df.iterrows()):
        counter_total += 1
        project_csv = row['project']
        file_path_csv = row['file_path']

        # Fetch classes if it's the same project name as in the csv row
        postgreSQL_select_Query = 'SELECT * FROM public.class WHERE project = %s'
        cursor.execute(postgreSQL_select_Query, (project_csv,))
        classes = cursor.fetchall()

        # Loop for all classes in the database with the same project as the current csv row
        for case in classes:
            split_paths = case[1].split('/', 6)
            path = split_paths[-1]

            # Set or reset bug fix flag as false for each case
            bug_fix_flag = False

            # Create or reset default smells results with all false as default before testing
            smells_results = {
                'MultifacetedAbstraction': False,
                'UnnecessaryAbstraction': False,
                'InsufficientModularization': False,
                'WideHierarchy': False,
                'LongMethod': False,
                'ComplexMethod': False
            }

            # Check if the file path in the csv row is contained in the current csv row path
            if file_path_csv in path:
                # Fetch methods if it's the same class id as the id of the class in case
                class_id = case[0]
                postgreSQL_select_Query = 'SELECT * FROM public.method WHERE class_id = %s'
                cursor.execute(postgreSQL_select_Query, (class_id,))
                methods = cursor.fetchall()

                # Findall to get only the numbers from all hunks, but separates in different tuples inside the list
                hunks = re.findall("@@ -(.*),(.*) [+](.*),(.*) @@", row['patch'])

                for hunk in hunks:
                    # get line number from class and compare with hunk intervals
                    class_line_number = case[7]
                    first_start = int(hunk[0])
                    first_end = int(hunk[0]) + int(hunk[1])
                    second_start = int(hunk[2])
                    second_end = int(hunk[2]) + int(hunk[3])

                    # Check if line number in class table from database is within hunk intervals
                    if first_start <= class_line_number <= first_end or second_start <= class_line_number <= second_end:

                        # Set bug fix flag as true if line number within intervals
                        bug_fix_flag = True

                        # Get metrics for code smells
                        class_metrics = case[9]
                        smell_LCOM = class_metrics['PercentLackOfCohesion']
                        smell_NOF = class_metrics['CountDeclClassVariable'] + class_metrics['CountDeclInstanceVariable']
                        smell_NOM = class_metrics['CountDeclMethod']
                        smell_NOPM = class_metrics['CountDeclMethodPublic']
                        smell_WMC = class_metrics['SumCyclomaticModified']
                        smell_NC = class_metrics['CountClassDerived']

                        # Individual test for each smell
                        if smell_LCOM >= 80 and smell_NOF >= 7 and smell_NOM >= 7:
                            smells_results['MultifacetedAbstraction'] = True
                        if smell_NOF >= 5 and smell_NOM == 0:
                            smells_results['UnnecessaryAbstraction'] = True
                        if smell_NOPM >= 20 or smell_NOM >= 30 or smell_WMC >= 100:
                            smells_results['InsufficientModularization'] = True
                        if smell_NC >= 10:
                            smells_results['WideHierarchy'] = True

                        for method in methods:
                            method_line_number = method[7]

                            # Check if line number in method table from database is also within hunk intervals
                            if first_start <= method_line_number <= first_end \
                                    or second_start <= method_line_number <= second_end:

                                # # Update method table marking as a bug fix commit
                                # method_id = method[0]
                                # postgreSQL_alter_Query = "UPDATE public.method SET bug_fix = %s WHERE id = %s"
                                # cursor.execute(postgreSQL_alter_Query, (True, method_id))
                                # connection.commit()

                                method_metrics = method[9]

                                if 'CountLine' in method_metrics:
                                    smell_LOC = method_metrics['CountLine']
                                else:
                                    smell_LOC = 0
                                if 'Cyclomatic' in method_metrics:
                                    smell_CC = method_metrics['Cyclomatic']
                                else:
                                    smell_CC = 0

                                if smell_LOC >= 100:
                                    smells_results['LongMethod'] = True
                                if smell_CC >= 8:
                                    smells_results['ComplexMethod'] = True

                # Update class table marking as a bug fix commit
                postgreSQL_alter_Query = 'UPDATE public.class SET bug_fix = %s WHERE id = %s'
                cursor.execute(postgreSQL_alter_Query, (bug_fix_flag, class_id))
                connection.commit()

                # Update database with the test for smells results
                postgreSQL_alter_Query = 'UPDATE public.class SET smells = %s WHERE id = %s'
                cursor.execute(postgreSQL_alter_Query, (json.dumps(smells_results), class_id))
                connection.commit()

            # If it is a bug fix mark as a success
            if bug_fix_flag:
                counter_success += 1
            if counter_success >= 1000:
                raise Exception('Assigned counter limit reached')

except (Exception, Error) as error:
    print('Error while connecting to PostgreSQL', error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print('PostgreSQL connection is closed')
        print('Time elapsed in seconds:')
        end = time.time()
        print(end - start)
        print('Successful cases:')
        print(counter_success)
        print('Total cases:')
        print(counter_total)
