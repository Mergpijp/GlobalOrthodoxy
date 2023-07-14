from globalorthodoxy.settings import MEDIA_ROOT
from django.core.management.base import BaseCommand, CommandError
from os import walk, mkdir
from os.path import join
from shutil import copyfile

class Command(BaseCommand):
    help = 'Puts all images in one folder'

    def handle(self, *args, **options):

        EXPORT_DIR = '/vol/tensusers5/wstoop/fourcorners_export/'

        try:
            mkdir(EXPORT_DIR)
        except FileExistsError:
            pass

        for root, subdirs, files in walk(MEDIA_ROOT):

            for file_name in files:

                file_path = join(root,file_name)

                if 'small' in file_path:
                    continue

                try:
                    copyfile(join(root,file_name), join(EXPORT_DIR,file_name))
                except PermissionError:
                    pass