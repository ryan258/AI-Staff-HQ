import os
from PIL import Image

def resize_images(directory, width, height):
    """Resizes all images in a directory to a specified width and height."""
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(directory, filename)
            with Image.open(filepath) as img:
                resized_img = img.resize((width, height))
                resized_img.save(filepath)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Resize images in a directory.')
    parser.add_argument('directory', type=str, help='The directory containing the images.')
    parser.add_argument('width', type=int, help='The new width of the images.')
    parser.add_argument('height', type=int, help='The new height of the images.')

    args = parser.parse_args()
    resize_images(args.directory, args.width, args.height)
