from django.db import models
from enum import Enum
from django import forms
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django_countries.fields import CountryField

MINIMUM_YEAR = 1850
MINIMUM_YEAR_PUBLICATION = 1970

class WritingDirection(Enum):
    LEFT = "L"
    RIGHT = "R"

class LocationType(Enum):
    CITY  = "CI"
    COUNTRY = "CO"
    AREA = "AR"

class DocumentType(Enum):
    PDF = "P"
    WEBPAGE = "W"
    IMAGE = "I"
    VIDEO = "V"

class Genre(models.Model):
    name = models.CharField(max_length=100)
	
    def __str__(self):
        return 'Genre: ' + self.name
 
def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year()+1)(value)  
    				
class Language(models.Model):
    name = models.CharField(max_length=100)
    direction = models.CharField(max_length=1, choices=[(tag.value, tag) for tag in WritingDirection], default='R')

class Author(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    year_of_birth = models.IntegerField(('year_of_birth'),blank=True, null=True, validators=[MinValueValidator(MINIMUM_YEAR), max_value_current_year])
	
    def __str__(self):
        return 'firstname: ' + self.firstname + ' lastname: ' + self.lastname + ' date of birth: ' + str(self.year_of_birth)

class Location(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=2, choices=[(tag.value, tag) for tag in LocationType], default='CI')
    
    def __str__(self):
        return self.name
     
class Owner(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class IllustrationLayoutType(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class SpecialOccasion(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Church(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

def year_choices():
    return [(r,r) for r in range(MINIMUM_YEAR, datetime.date.today().year+1)]

class MyForm(forms.ModelForm):
    year = forms.TypedChoiceField(coerce=int, choices=year_choices, initial=current_year)

class Publication(models.Model):
    title_subtitle_european = models.CharField(max_length=300)
    title_translation = models.CharField(max_length=300)
    title_subtitle_transcription = models.CharField(max_length=300)
    author = models.ManyToManyField(Author)
    printed_by = models.CharField(max_length=100)
    published_by = models.CharField(max_length=100)
    publication_date = models.DateField()
    country = CountryField()
    venue = models.CharField(max_length=100)
    church = models.ManyToManyField(Church)
    language = models.ManyToManyField(Language)
    genre = models.ManyToManyField(Genre)
    special_occasion = models.ManyToManyField(SpecialOccasion)
    illustration_and_layout = models.ManyToManyField(IllustrationLayoutType)
    nr_of_pages = models.IntegerField()
    collection_date = models.DateField()
    collection_country = CountryField()
    collection_venue = models.CharField(max_length=100)
    copyrights = models.NullBooleanField()
    currently_owned_by = models.ManyToManyField(Owner)
    comments = models.CharField(max_length=200)
    
    def __str__(self):
        return 'title: ' + self.title_translation +', publication date: ' + str(self.publication_date)\
                + ', collection venue: ' + self.collection_venue + ', comments: ' + self.comments

class Document(models.Model):
    type = models.CharField(max_length=1, choices=[(tag.value, tag) for tag in DocumentType], default='P')
    publication = models.OneToOneField(Publication, on_delete=models.CASCADE, primary_key=True)
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=100)
    location_on_disk = models.CharField(max_length=150)    
	
