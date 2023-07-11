import csv
import re

import pandas as pd

import psycopg2
from psycopg2 import Error
from tqdm.auto import tqdm

# Removing data frame to check if iterating over it slows down the code
df = pd.read_csv('projects_patches.csv')
print(df)

bug_fix_tuple = ()
smells_results_tuple = ()

counter_success = 0

# Connect to an existing database
connection = psycopg2.connect(user="postgres",
                              password="1234",
                              dbname="metrics")
# Create a cursor to perform database operations
cursor = connection.cursor()


def if_not_exist_create_column(table_name, column_name, data_type):
    psql_exist_query = "SELECT EXISTS (SELECT 1 FROM information_schema.columns " \
                       "WHERE table_name = %s AND column_name = %s)"
    cursor.execute(psql_exist_query, (table_name, column_name))
    exists_smells_column = cursor.fetchone()

    if not exists_smells_column[0]:
        psql_alter_query = "ALTER TABLE public.class ADD COLUMN (%s) (%s)"
        cursor.execute(psql_alter_query, (column_name, data_type))
        connection.commit()


try:

    # Opening the csv file as a dictionary
    with open('projects_patches.csv', mode='r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        # Loop for all rows in the csv file
        for row in tqdm(csv_reader):
            project_csv = row['project']
            file_path_csv = row['file_path']

            # Fetch classes if it's the same project name and file path as in the csv row
            postgreSQL_select_Query = "SELECT * FROM public.class WHERE project = %s AND position(%s in file)>0"
            cursor.execute(postgreSQL_select_Query, (project_csv, file_path_csv))
            classes = cursor.fetchall()

            # Loop for all classes in the database with the same project as the current csv row
            for case in tqdm(classes):
                split_paths = case[1].split('/', 6)
                path = split_paths[-1]

                # Fetch methods if it's the same class id as the id of the class in case
                class_id = case[0]
                postgreSQL_select_Query = "SELECT * FROM public.method WHERE class_id = %s"
                cursor.execute(postgreSQL_select_Query, (class_id,))
                methods = cursor.fetchall()

                # Findall to get only the numbers from all hunks, but separates in different tuples inside the list
                hunks = re.findall("@@ -(.*),(.*) [+](.*),(.*) @@", row['patch'])

                # Create or reset default bug fix flag
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

                for hunk in hunks:
                    # get line number from class and compare with hunk intervals
                    class_line_number = case[7]
                    first_start = int(hunk[0])
                    first_end = int(hunk[0]) + int(hunk[1])
                    second_start = int(hunk[2])
                    second_end = int(hunk[2]) + int(hunk[3])

                    # Check if line number in class table from database is within hunk intervals
                    if first_start <= class_line_number <= first_end or second_start <= class_line_number <= second_end:

                        # Change bug_fix flag if line number is within hunk intervals
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

                if counter_success >= 1000:
                    # Removed data frame
                    # df['bug_fix'] = pd.Series(bug_fix_tuple)
                    # df['smells'] = pd.Series(smells_results)
                    # print(df)
                    raise Exception('Assigned counter limit reached')
                if bug_fix_flag:
                    counter_success += 1

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
        print('Successful cases:')
        print(counter_success)
