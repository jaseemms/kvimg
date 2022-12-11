from glob import iglob
from kivy.uix.label import Label
from kivy.logger import Logger
from PIL import Image

from platform_based import get_picture_directory

image_formats = (".jpeg", ".jpg", ".png")


def get_image_iterator(storage_path="internal"):

	home_directory = get_picture_directory(storage_path=storage_path)

	search_pattern = f"{home_directory}/**/*.*"

	Logger.info(f"Search pattern : {search_pattern}")

	image_iterator = iglob(search_pattern, recursive=True)

	return image_iterator


def get_image_bytes(image_path):

	image = Image.open(image_path)
	img_width, img_height = image.size
	crop_size = min(image.size)
	
	image = image.crop((
		(img_width - crop_size) // 2,
        (img_height - crop_size) // 2,
        (img_width + crop_size) // 2,
        (img_height + crop_size) // 2
    ))

	image.thumbnail((90,90))
	image = image.rotate(180)
	image = image.transpose(Image.FLIP_LEFT_RIGHT)
	image_bytes = image.tobytes()

	return image_bytes, image.size

