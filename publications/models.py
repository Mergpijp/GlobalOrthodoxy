from django.db import models
from enum import Enum
from django import forms
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django_countries.fields import CountryField
from django_countries import countries
#from django_select2.forms import ModelSelect2Widget
#from smart_selects.db_fields import GroupedForeignKey
from smart_selects.db_fields import ChainedForeignKey


MINIMUM_YEAR = 1850
MINIMUM_YEAR_PUBLICATION = 1970


class FormOfPublication(Enum):
    PUBLISHED_PAPER = "P"
    SELF_PUBLISHED_PAPER = "S"
    TEXT_ON_WEBSITE = "T"
    OTHER = "O"
    NONE = None
    
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
    name = models.CharField(max_length=100, blank=True)
	
    def __str__(self):
        return 'Genre: ' + self.name
 
def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year()+1)(value)  
    				
class Language(models.Model):
    name = models.CharField(max_length=100, blank=True)
    direction = models.CharField(max_length=1, choices=[(tag.value, tag) for tag in WritingDirection], default='R')
    def __str__(self):
        return 'name: ' + self.name + ' direction: ' + str(self.direction)
class Author(models.Model):
    firstname = models.CharField(max_length=100, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
    year_of_birth = models.IntegerField(('year_of_birth'), blank=True, null=True, validators=[MinValueValidator(MINIMUM_YEAR), max_value_current_year])
	
    def __str__(self):
        return 'firstname: ' + self.firstname + ' lastname: ' + self.lastname + ' date of birth: ' + str(self.year_of_birth)

class Translator(models.Model):
    firstname = models.CharField(max_length=100, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
   
    def __str__(self):
        return 'firstname: ' + self.firstname + ' lastname: ' + self.lastname

class Location(models.Model):
    name = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=2, choices=[(tag.value, tag) for tag in LocationType], default='CI')
    
    def __str__(self):
        return self.name
     
class Owner(models.Model):
    name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class IllustrationLayoutType(models.Model):
    name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class SpecialOccasion(models.Model):
    name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class Church(models.Model):
    name = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name_plural = "churches"
    def __str__(self):
        return self.name

def year_choices():
    return [(r,r) for r in range(MINIMUM_YEAR, datetime.date.today().year+1)]

class MyForm(forms.ModelForm):
    year = forms.TypedChoiceField(coerce=int, choices=year_choices, initial=current_year)

'''
class Country(models.Model):
    name = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name_plural = "countries"
    def __str__(self):
        return self.name
'''
        
class Country(models.Model):
    #country = CountryField(choices=list(countries))
    country = CountryField(blank=True, null=True)
    def __unicode__(self):
        return self.country
        
    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name
        
class City(models.Model):
    name = models.CharField(max_length=255, blank=True)
    #country = models.ForeignKey('Country', related_name="cities", on_delete=models.CASCADE, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    #country = models.OneToOneField(Country, on_delete=models.CASCADE, blank=True, null=True)
    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name  
        
class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.description  

class Publication(models.Model):
    title_original = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription = models.CharField(max_length=300, blank=True)
    title_subtitle_European = models.CharField(max_length=300, blank=True)
    title_translation = models.CharField(max_length=300, blank=True)
    author = models.ManyToManyField(Author)
    translator = models.ManyToManyField(Translator)
    form_of_publication = models.CharField(max_length=1, choices=[(tag.value, tag) for tag in FormOfPublication], blank=True)
    printed_by = models.CharField(max_length=100, blank=True)
    published_by = models.CharField(max_length=100, blank=True)
    publication_date = models.DateField(blank=True, null=True)
    #publication_country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    publication_country = CountryField(blank=True, null=True)
    #publication_country = models.OneToOneField(Country, on_delete=models.CASCADE, blank=True, null=True)
    publication_city = ChainedForeignKey(
        City,
        chained_field="publication_country",
        chained_model_field="country",
        show_all=False,
        auto_choose=True,
        sort=True, 
        blank=True,
        null=True)
    
    publishing_organisation = models.CharField(max_length=100, blank=True)
    possible_donor = models.CharField(max_length=100, blank=True)
    affiliated_church = models.ManyToManyField(Church)
    language = models.ManyToManyField(Language)
    content_description = models.CharField(max_length=300, blank=True)
    content_genre = models.ManyToManyField(Genre)
    connected_to_special_occasion = models.ManyToManyField(SpecialOccasion)
    description_of_illustration = models.CharField(max_length=300, blank=True)
    image_details = models.CharField(max_length=300, blank=True)
    nr_of_pages = models.IntegerField(blank=True, null=True)
    collection_date = models.DateField(blank=True, null=True)
    collection_country = CountryField(blank=True)
    collection_venue_and_city = models.CharField(max_length=100, blank=True)
    copyrights = models.NullBooleanField()
    currently_owned_by = models.ManyToManyField(Owner)
    contact_info = models.CharField(max_length=300, blank=True)
    comments = models.CharField(max_length=200, blank=True)
    
    documents = models.ManyToManyField(Document, blank=True, null=True)
    #Fields that do not exist in excel sheet:
    venue = models.CharField(max_length=100, blank=True)
    illustration_and_layout_type = models.ManyToManyField(IllustrationLayoutType, blank=True, null=True)
   
    def __str__(self):
        return 'title: ' + self.title_translation +', publication date: ' + str(self.publication_date)\
                + ', collection venue: ' + self.collection_venue_and_city + ', comments: ' + self.comments


'''
class PublicationLanguage(models.Model): # table to store which publication has which language
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
'''
'''
class Document(models.Model):
    type = models.CharField(max_length=1, choices=[(tag.value, tag) for tag in DocumentType], default='P')
    publication = models.OneToOneField(Publication, on_delete=models.CASCADE, primary_key=True)
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=100)
    location_on_disk = models.CharField(max_length=150)    
'''
