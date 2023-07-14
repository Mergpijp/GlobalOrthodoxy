from django.core.management.base import BaseCommand, CommandError
from publications.models import UploadedFile
from extcolors import extract_from_path
from PIL import UnidentifiedImageError

class Command(BaseCommand):
    help = 'Goes over all uploaded files and detects their colors'

    def handle(self, *args, **options):

        for file in UploadedFile.objects.all():

            try:
                colors = extract_from_path(file.file.path, tolerance=12, limit=2)[0]
            except (ValueError, FileNotFoundError, UnidentifiedImageError) as e:
                continue

            colors = [f'#{color[0][0]:02x}{color[0][1]:02x}{color[0][2]:02x}' for color in colors]

            file.main_color = colors[0]
            file.secondary_color = colors[1]

            print(f'File {file.id} has colors {colors[0]} and {colors[1]}')

            file.save()
