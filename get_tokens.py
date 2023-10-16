import csv
import sys
import subprocess

csv.field_size_limit(sys.maxsize)

# Set the string bellow to the path to a tokenizer executable file in Linux
TOKENIZER_BIN = r"/home/orestesmkb/Documents/tokenizer/src/tokenizer"

# File names to run on tokenizer
FILE_NAMES = ['bug', 'harmful', 'clean', 'bug_without_smells', 'not_bug_with_smells']


def get_tokens(language, file):
    # This function reads a text file and returns the correspondent tokens for the text contained in the file
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
    # This function creates temporary code text files for the get_tokens function
    try:
        with open('experiment.tmp', 'w+') as file:
            file.write(code_text)
            return 'experiment.tmp'
    except Exception as e:
        print('Unexpected Error on Create Tmp File', e)
        return None


# Loop all files
for file in FILE_NAMES:
    # Input file path
    tokenizer_file_path = 'csv files\\tokenizer data\\' + file + '_tokenizer_data.csv'
    # Open csv with data to create tokens and save them all in a new file
    with open(tokenizer_file_path, encoding="utf-8", newline='') as csvfile1:
        reader = csv.DictReader(csvfile1)

        # Output file path
        tokenized_file_path = 'csv files\\tokenized\\' + file + '_tokenized.csv'
        with open(tokenized_file_path, 'w', encoding="utf-8", newline='') as csvfile2:
            fieldnames = ['id', 'language', 'text', 'smells', 'tokens']
            writer = csv.DictWriter(csvfile2, fieldnames=fieldnames)
            writer.writeheader()

            # Loop to write all rows
            for row in reader:
                csv_id = row['id']
                csv_language = row['language']
                csv_text = row['text']
                csv_smells = row['smells']

                temp_file = create_tmp_file(csv_text)
                result_tokens = get_tokens(csv_language, temp_file)
                writer.writerow({'id': csv_id, 'language': csv_language, 'text': csv_text, 'smells': csv_smells,
                                 'tokens': result_tokens})
