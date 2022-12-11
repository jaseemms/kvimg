from kivy.utils import platform
from plyer import storagepath


def get_permissions():
	
	if platform == 'android':
		from android.permissions import request_permissions, Permission
		request_permissions([Permission.READ_EXTERNAL_STORAGE])

def get_picture_directory(storage_path='internal'):

	if platform == 'android':

		if storage_path == 'internal':
			return storagepath.get_external_storage_dir()

		elif storage_path == 'external':
			try:
				return storagepath.get_sdcard_dir()
			except:
				return None

	elif platform == 'linux':

		if storage_path == 'internal':
			return storagepath.get_pictures_dir()

		else:
			return None

	else:
		return None
