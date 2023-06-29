## Python script for the Bugs and Smells Tracker

This script checks if the paths in a "projects_patches.csv" file are contained in a local PostgreSQL database, if so it 
marks that row as a bug fix commit and checks for code smells based on metrics contained in the database, 
adding another row with a jsonb that specifies which type of smells it contains.

# Install the requirements

- pip install -r requirements.txt
