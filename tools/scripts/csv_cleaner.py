import pandas as pd

def clean_csv(filepath):
    """Removes duplicate rows and handles missing values in a CSV file."""
    df = pd.read_csv(filepath)
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    df.to_csv(filepath, index=False)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clean a CSV file.')
    parser.add_argument('filepath', type=str, help='The path to the CSV file.')

    args = parser.parse_args()
    clean_csv(args.filepath)
