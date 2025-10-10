from pathlib import Path

from PIL import Image


SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')


def resize_images(directory: str, width: int, height: int, *, output_dir: str | None = None, keep_aspect: bool = True) -> None:
    """Resize images in ``directory`` and write results to ``output_dir`` (default: ./resized).

    Originals are left untouched unless ``output_dir`` equals ``directory``. When keeping aspect ratio,
    the image fits within the requested box while preserving proportions.
    """

    source_dir = Path(directory)
    destination_dir = Path(output_dir) if output_dir else source_dir / 'resized'
    destination_dir.mkdir(parents=True, exist_ok=True)

    for filepath in source_dir.iterdir():
        if not filepath.is_file() or filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        with Image.open(filepath) as img:
            if keep_aspect:
                resized = img.copy()
                resized.thumbnail((width, height))
            else:
                resized = img.resize((width, height))

            destination = destination_dir / filepath.name
            if destination.exists():
                destination = destination_dir / f"{destination.stem}_resized{destination.suffix}"
            resized.save(destination)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Safely resize images in a directory.')
    parser.add_argument('directory', type=str, help='Directory containing images to resize.')
    parser.add_argument('width', type=int, help='Target width in pixels.')
    parser.add_argument('height', type=int, help='Target height in pixels.')
    parser.add_argument('--output-dir', type=str, help='Destination directory (default: <directory>/resized).')
    parser.add_argument('--stretch', action='store_true', help='Disable aspect-ratio preservation and stretch to exact dimensions.')

    args = parser.parse_args()
    resize_images(args.directory, args.width, args.height, output_dir=args.output_dir, keep_aspect=not args.stretch)
