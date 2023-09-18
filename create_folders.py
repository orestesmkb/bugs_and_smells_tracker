import os


def create_folders(folder_path='csv files', additional_folders=None):
    # This function will check if a folder exists, if it does not it will create one with the path from the input
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        if additional_folders is not None:
            for additional_folder in additional_folders:
                additional_folder_path = os.path.join(folder_path, additional_folder)
                os.mkdir(additional_folder_path)
        print("Folder %s created!" % folder_path)
    else:
        print("Folder %s already exists" % folder_path)
