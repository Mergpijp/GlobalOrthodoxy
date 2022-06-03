from globalorthodoxy.settings import MEDIA_ROOT
from django.core.management.base import BaseCommand, CommandError
from os import walk
from PIL import Image
from os.path import isfile, join

class Command(BaseCommand):
    help = 'Looks for missing small images and adds them'

    def handle(self, *args, **options):

        SMALL_FILE_SIZE = 400

        for root, subdirs, files in walk(MEDIA_ROOT):

            for file_path in files:

                file_path = join(root,file_path)

                if not file_path.lower().endswith('.jpg') and not file_path.lower().endswith('.png'):
                    continue

                if 'small' in file_path:
                    continue

                small_file_path = file_path.replace('.jpg', '_small.jpg').replace('.png', '_small.png')

                if isfile(small_file_path):
                    continue

                print(file_path, small_file_path)

                if '.png' in file_path.lower():
                    file_type = 'PNG'
                else:
                    file_type = 'JPEG'

                try:
                    image = Image.open(file_path)
                except PermissionError:
                    print('Permission denied to', file_path)
                    continue

                try:
                    image.thumbnail((SMALL_FILE_SIZE, SMALL_FILE_SIZE), Image.ANTIALIAS)
                except OSError:
                    print('Could not create thumbnail for', file_path)
                    continue

                image.save(small_file_path, file_type)
