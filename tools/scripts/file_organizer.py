from pathlib import Path
import shutil


def organize_files(directory: str, *, destination: str | None = None, dry_run: bool = True) -> list[tuple[Path, Path]]:
    """Organize files into subdirectories based on extension.

    Args:
        directory: Source directory to organise.
        destination: Optional destination root. Defaults to ``directory``.
        dry_run: If ``True`` (default) the function only reports planned moves.

    Returns:
        List of (source, target) pairs representing moves performed or planned.
    """

    source_dir = Path(directory)
    target_root = Path(destination) if destination else source_dir
    moves: list[tuple[Path, Path]] = []

    for item in source_dir.iterdir():
        if not item.is_file():
            continue

        extension = item.suffix.lower().lstrip('.') or 'no_extension'
        target_dir = target_root / extension
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / item.name
        counter = 1
        while target_path.exists():
            target_path = target_dir / f"{item.stem}_{counter}{item.suffix}"
            counter += 1

        moves.append((item, target_path))
        if not dry_run:
            shutil.move(str(item), str(target_path))

    return moves


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Group files by extension with optional dry run.')
    parser.add_argument('directory', type=str, help='Directory to organise.')
    parser.add_argument('--destination', type=str, help='Optional destination directory root.')
    parser.add_argument('--execute', action='store_true', help='Perform the moves. Defaults to dry-run preview.')

    args = parser.parse_args()
    planned_moves = organize_files(args.directory, destination=args.destination, dry_run=not args.execute)

    for src, dest in planned_moves:
        action = 'MOVE' if args.execute else 'PLAN'
        print(f"{action}: {src} -> {dest}")
