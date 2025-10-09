import os
import shutil

def organize_files(directory):
    """Organizes files in a directory into subdirectories based on file type."""
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            file_extension = filename.split('.')[-1]
            if file_extension:
                subdirectory = os.path.join(directory, file_extension)
                os.makedirs(subdirectory, exist_ok=True)
                shutil.move(os.path.join(directory, filename), os.path.join(subdirectory, filename))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Organize files in a directory.')
    parser.add_argument('directory', type=str, help='The directory to organize.')

    args = parser.parse_args()
    organize_files(args.directory)
