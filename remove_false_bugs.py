import re
import pandas as pd

import psycopg2
from psycopg2 import Error

from tqdm.auto import tqdm

df = pd.read_csv('projects_patches.csv')
print('Total cases in "project_patches.csv":')
print(len(df))

counter_success = 0
counter_removal = 0

# Connect to an existing database
connection = psycopg2.connect(user='postgres',
                              password='1234',
                              dbname='metrics')
# Create a cursor to perform database operations
cursor = connection.cursor()

try:
    # Loop for all rows in the csv file
    for index, row in tqdm(df.iterrows()):

        file_path_csv = row['file_path']

        # Fetch classes if it's the same project name and file path as in the csv row
        postgreSQL_select_Query = 'SELECT * FROM public.class WHERE bug_fix = %s AND position(%s in file)>0'
        cursor.execute(postgreSQL_select_Query, (True, file_path_csv))
        classes = cursor.fetchall()

        # Loop for all classes in the database with the same project as the current csv row
        for case in tqdm(classes):

            # Set or reset bug fix flag as false for each case
            bug_fix_flag = False

            # Fetch methods if it's the same class id as the id of the class in case
            class_id = case[0]

            # Findall to get only the numbers from all hunks, but separates in different tuples inside the list
            hunks = re.findall("@@ -(.*),(.*) [+](.*),(.*) @@", row['patch'])

            for hunk in hunks:
                # get line number from class and compare with hunk intervals
                class_line_number = case[7]
                hunk_start = int(hunk[0])
                hunk_end = int(hunk[0]) + int(hunk[1])

                # Check if line number in class table from database is within hunk intervals
                if hunk_start <= class_line_number <= hunk_end:

                    # Set bug fix flag as true if line number within intervals
                    bug_fix_flag = True

            # Update class table marking as a bug fix commit
            postgreSQL_alter_Query = 'UPDATE public.class SET bug_fix = %s WHERE id = %s'
            cursor.execute(postgreSQL_alter_Query, (bug_fix_flag, class_id))
            connection.commit()

            # If it is a bug fix mark as a success
            if not bug_fix_flag:
                counter_removal += 1
            else:
                counter_success += 1

except (Exception, Error) as error:
    print('Error while connecting to PostgreSQL', error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print('PostgreSQL connection is closed')
        print('Removed cases:')
        print(counter_removal)
        print('Bug fix cases:')
        print(counter_success)
