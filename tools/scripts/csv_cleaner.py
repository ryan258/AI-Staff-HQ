from pathlib import Path
import shutil

import pandas as pd


def clean_csv(filepath: str, output: str | None = None, drop_na: bool = True) -> Path:
    """Clean a CSV file by removing duplicates and (optionally) rows with missing values.

    A backup of the source file is created automatically when writing in place.

    Args:
        filepath: Location of the CSV to clean.
        output: Optional destination path. If omitted the file is updated in place.
        drop_na: Whether to drop rows containing NA values. Defaults to ``True``.

    Returns:
        Path to the written CSV file.
    """

    source = Path(filepath)
    destination = Path(output) if output else source

    df = pd.read_csv(source)
    df = df.drop_duplicates()
    if drop_na:
        df = df.dropna()

    if destination == source:
        backup = source.with_suffix(source.suffix + ".bak")
        shutil.copy2(source, backup)
        destination = source
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(destination, index=False)
    return destination


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clean a CSV file safely.')
    parser.add_argument('filepath', type=str, help='Path to the CSV file to clean.')
    parser.add_argument('--output', type=str, help='Optional destination CSV. Defaults to in-place update with backup.')
    parser.add_argument('--keep-null', action='store_true', help='Retain rows with null values instead of dropping them.')

    args = parser.parse_args()
    clean_csv(args.filepath, output=args.output, drop_na=not args.keep_null)
