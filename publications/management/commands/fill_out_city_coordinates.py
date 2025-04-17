from publications.models import City
from django.core.management.base import BaseCommand, CommandError
from os import walk
from PIL import Image
from os.path import isfile, join
from time import sleep

class Command(BaseCommand):
    help = 'Looks for missing city coordinates and adds them'

    def handle(self, *args, **options):

        from geopy.geocoders import GeoNames

        for city in City.objects.all():

            #if city.coordinates_requested:
            #    continue

            gn = GeoNames(username='fourcornersRU')
            coordinates = gn.geocode(f'{city.name}, {city.country.name}')
            
            city.coordinates_requested = True

            if coordinates is None:
                print('No coordinates found for', city.name, 'in', city.country.name)
                city.save()
                continue

            coordinates = coordinates[-1]
            city.x = coordinates[0]
            city.y = coordinates[1]
            city.coordinates_known = True
            city.save()

            print('Coordinates found for', city.name, 'in', city.country.name, 'are', city.x, city.y)
            sleep(1)