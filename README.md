# Python project: Bugs and Smells Tracker

## Install the requirements

- pip install -r requirements.txt

## main.py script:
In this repository the main file opens a "project_patches.csv", with the following header "project,commit,file_path,patch", 
and compares its data with a local PostgreSQL database. It checks if the file path from the csv is contained within the database, 
if so it verifies if there are any smells in the code and saves a jsonb to the database, then it checks if the line number 
from that class and its methods are contained in the hunk intervals from the csv patch, marking it in the database as a bug fix.

## get_tokens_csv.py script:
This script generates temporary files, based on a csv file, to generate tokens from the code text, it requires [tokenizer](https://github.com/moabson/tokenizer) to run.

## make_tokenizer_csv.py script:
This script will get all relevant data from the PostgreSQL database and save it in a csv file. This was necessary to run the
get_tokens.py script in a Linux virtual machine.

## make_train_test.py script:
This script receives a csv file and, for each language and code smell, it does an 80/20 split, creating train and test files.

## plot_test.py script:
This script has all the code needed to run transfer-learning-experiments, however only the RQ3: Plot function is not commented.
