from PIL import Image
import os

def save_image(image: Image, directory: str) -> int:
    """
    Saves the given image to the specified directory and returns the file ID.
    """
    existing_files = os.listdir(directory)
    file_id = len(existing_files)
    image_path = os.path.join(directory, f"{file_id}.png")
    image.save(image_path)
    return file_id
