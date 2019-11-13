from django.db import models
from enum import Enum
from django import forms
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator

class LanguageDirection(Enum):
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
    name = models.CharField(max_length=30)
	
    def __str__(self):
        return 'Genre: ' + self.name
 
def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)    
    
class Publication(models.Model):
    title = models.CharField(max_length=100)
    language = models.CharField(max_length=30)
    year = models.IntegerField(('year'), validators=[MinValueValidator(1970), max_value_current_year])
    found_at = models.CharField(max_length=30)
    genre = models.ManyToManyField(Genre)
    #genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    usage = models.CharField(max_length=200)
    
    def __str__(self):
        return 'title: ' + self.title + ', language: ' + self.language + ', year: ' + str(self.year)\
                + ', found at: ' + self.found_at + ', usage: ' + self.usage
class Language(models.Model):
    direction = models.CharField(max_length=1, choices=[(tag.value, tag) for tag in LanguageDirection], default='R')

class Author(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    year_of_birth = models.DateField()

class Location(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=2, choices=[(tag.value, tag) for tag in LocationType], default='CI')
    
class Document(models.Model):
    type = models.CharField(max_length=1, choices=[(tag.value, tag) for tag in DocumentType], default='P')
    publication = models.OneToOneField(Publication, on_delete=models.CASCADE, primary_key=True)
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=30)
    location_on_disk = models.CharField(max_length=150)
    

def year_choices():
    return [(r,r) for r in range(1970, datetime.date.today().year+1)]

class MyForm(forms.ModelForm):
    year = forms.TypedChoiceField(coerce=int, choices=year_choices, initial=current_year)
    
	
