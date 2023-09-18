import csv
import sys
import subprocess

csv.field_size_limit(sys.maxsize)

# Bellow is the path to tokenizer executable file in Ubuntu
TOKENIZER_BIN = r"/home/orestesmkb/Documents/tokenizer/src/tokenizer"


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


# Open csv with data to create tokens and save them all in a new file
with open('tokenizer_data.csv', encoding="utf-8", newline='') as csvfile1:
    reader = csv.DictReader(csvfile1)

    with open('tokenized.csv', 'w', encoding="utf-8", newline='') as csvfile2:
        fieldnames = ['id', 'language', 'text', 'smells', 'tokens']
        writer = csv.DictWriter(csvfile2, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            csv_id = row['id']
            csv_language = row['language']
            csv_text = row['text']
            csv_smells = row['smells']

            temp_file = create_tmp_file(csv_text)
            result_tokens = get_tokens(csv_language, temp_file)
            writer.writerow({'id': csv_id, 'language': csv_language, 'text': csv_text, 'smells': csv_smells,
                             'tokens': result_tokens})
