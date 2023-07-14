import subprocess

import psycopg2
from psycopg2 import Error

TOKENIZER_BIN = r"C:\Users\orest\IdeaProjects\tokenizer\src\tokenizer"


def get_tokens(language, file):
    tokens = ''
    cmd = [TOKENIZER_BIN, '-l', language, file]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    try:
        output, error = process.communicate()
        tokens = output.decode('utf8')
        tokens = tokens.replace('\t', ' ')
        tokens = tokens.replace('\n', '')
    except Exception as e:
        print('Unexpected Error on Get Tokens', e)

    return tokens


def create_tmp_file(code_text):
    try:
        with open('experiment.tmp', 'w+') as file:
            file.write(code_text)
            return 'experiment.tmp'
    except Exception as e:
        print('Unexpected Error on Create Tmp File', e)
        return None


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
    for bug in bugs:
        db_content = bug[8]
        temp_file = create_tmp_file(db_content)
        db_language = bug[2]
        result_tokens = get_tokens(db_language, temp_file)

except (Exception, Error) as error:
    print('Error while connecting to PostgreSQL', error)

finally:
    if connection:
        cursor.close()
        connection.close()
