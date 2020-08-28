from django.db import models
from enum import Enum
from django import forms
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from countries_plus.models import Country
from time import gmtime, strftime
import datetime
from django.utils import timezone

MINIMUM_YEAR = 1850
MINIMUM_YEAR_PUBLICATION = 1970

class FormOfPublication(models.Model):
    ''''
    Manytomany field that contains only a character field of a name.
    '''
    name = models.CharField(max_length=100, blank=True)
	
    def __str__(self):
        return self.name

class WritingDirection(Enum):
    '''
    Enum class for lnaguage writing direction
    '''
    Left = "Left"
    Right = "Right"

'''
class BookType(Enum):
    O = "Original"
    T = "Translated"
'''

class LocationType(Enum):
    '''
    Location enum with three different values.
    CITY, COUNTRY, AREA
    '''
    CITY  = "CI"
    COUNTRY = "CO"
    AREA = "AR"

class DocumentType(Enum):
    '''
    Document type enum with four values:
    PDF, webpage, image, video.
    '''
    PDF = "P"
    WEBPAGE = "W"
    IMAGE = "I"
    VIDEO = "V"

class Genre(models.Model):
    '''
    Manytomany field class. Contains only a charfield.
    '''
    name = models.CharField(max_length=100, blank=True)
	
    def __str__(self):
        return 'Genre: ' + self.name
 
def current_year():
    '''
    get current year
    '''
    return datetime.date.today().year

def max_value_current_year(value):
    '''
    Get the max value of the current year plus one
    '''
    return MaxValueValidator(current_year()+1)(value)  
    				
class Language(models.Model):
    '''
    Manytomany field class. Contains name as charfield and direction as charfield but is under the hood a enum,
    '''
    name = models.CharField(max_length=100, blank=True)
    direction = models.CharField(max_length=5, choices=[(tag.name, tag.value) for tag in WritingDirection])
    def __str__(self):
        return 'name: ' + self.name

class Author(models.Model):
    '''
    Manytomany field class with firstname and lastname as charfields.
    Year of birth as integer between 1850 and current year.
    '''
    name = models.CharField(max_length=100, blank=True)
    name_original_language = models.CharField(max_length=100, blank=True)
    extra_info = models.CharField(max_length=400, blank=True)
	
    def __str__(self):
        return 'name: ' + self.name +  'name original language: ' + self.name_original_language

class Translator(models.Model):
    '''
    Manytomany field class with two fields firstname and lastname both charfields.
    '''
    name = models.CharField(max_length=100, blank=True)
    name_original_language = models.CharField(max_length=100, blank=True)
    extra_info = models.CharField(max_length=400, blank=True)
   
    def __str__(self):
        return 'name: ' + self.name +  'name original language: ' + self.name_original_language

class Location(models.Model):
    '''
    Manytomany field class with two fields name and type both are charfields.
    '''
    name = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=2, choices=[(tag.value, tag) for tag in LocationType], default='CI')
    
    def __str__(self):
        return self.name
     
class Owner(models.Model):
    '''
    Manytomany field class with just one charfield name
    '''
    name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class IllustrationLayoutType(models.Model):
    '''
    Manytomany field class with just one charfield name
    '''
    name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class SpecialOccasion(models.Model):
    '''
    Manytomany field class with just one charfield name
    '''
    name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class Church(models.Model):
    '''
    Manytomany field class with just one charfield name
    '''
    name = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name_plural = "churches"
    def __str__(self):
        return self.name

def year_choices():
    '''
    Get all years between 1850 and current year plus one.
    '''
    return [(r,r) for r in range(MINIMUM_YEAR, datetime.date.today().year+1)]

class MyForm(forms.ModelForm):
    year = forms.TypedChoiceField(coerce=int, choices=year_choices, initial=current_year)


class City(models.Model):
    name = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey(Country, related_name='cities', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name  

class Keyword(models.Model):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class FileCategory(models.Model):
    order_index = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    list_view_priority = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class ImageContent(models.Model):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class UploadedFile(models.Model):
    '''
    Manytomany field class with three fields.
    A charfield, filefield and DateTimeField.
    The DateTimeField will be automatically added.
    '''
    description = models.CharField(max_length=255, blank=True)
    filecategory = models.ForeignKey(FileCategory, on_delete=models.CASCADE, related_name="filecategory", null=True, blank=True)
    imagecontents = models.ManyToManyField(ImageContent)
    file = models.FileField(upload_to='files/%Y/%m/%d/%H/%M/%S/%f/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('filecategory__order_index',)

CHOICES = (
    (None, "Unknown"),
    (True, "Yes"),
    (False, "No")
)

class ImageDetails(models.Model):
    '''
    Manytomany field class with three fields.
    three charfields.
    '''
    source_of_photo_or_illustration = models.CharField(max_length=100, blank=True)
    photographer = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.source_of_photo_or_illustration


class Publication(models.Model):
    '''
    Main class for Publications contains many charfields and several manytomany fields.
    '''

    title_original = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription = models.CharField(max_length=300, blank=True)
    title_translation = models.CharField(max_length=300, blank=True)
    title_original2 = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription2 = models.CharField(max_length=300, blank=True)
    title_translation2 = models.CharField(max_length=300, blank=True)
    title_original3 = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription3 = models.CharField(max_length=300, blank=True)
    title_translation3 = models.CharField(max_length=300, blank=True)
    title_original4 = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription4 = models.CharField(max_length=300, blank=True)
    title_translation4 = models.CharField(max_length=300, blank=True)
    title_original5 = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription5 = models.CharField(max_length=300, blank=True)
    title_translation5 = models.CharField(max_length=300, blank=True)
    author = models.ManyToManyField(Author)
    translator = models.ManyToManyField(Translator)
    form_of_publication = models.ManyToManyField(FormOfPublication)
    editor = models.CharField(max_length=100, blank=True)
    ISBN_number = models.CharField(max_length=100, blank=True)
    printed_by = models.CharField(max_length=100, blank=True)
    published_by = models.CharField(max_length=100, blank=True)
    publication_date = models.CharField(max_length=100, blank=True)
    publication_country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    publication_city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    publishing_organisation = models.CharField(max_length=100, blank=True)
    donor = models.CharField(max_length=100, blank=True)
    affiliated_church = models.ManyToManyField(Church)
    extra_info = models.CharField(max_length=400, blank=True)
    language = models.ManyToManyField(Language)
    is_a_translation = models.NullBooleanField(choices=CHOICES)
    translated_from = models.ForeignKey(Language,  on_delete=models.CASCADE, related_name='translated_from', null=True, blank=True)
    content_description = models.CharField(max_length=300, blank=True)
    content_genre = models.ManyToManyField(Genre)
    connected_to_special_occasion = models.ManyToManyField(SpecialOccasion)
    description_of_illustration = models.CharField(max_length=300, blank=True)
    nr_of_pages = models.IntegerField(blank=True, null=True)
    collection_date = models.CharField(max_length=100, blank=True)
    collection_country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='collections', null=True, blank=True)
    collection_venue_and_city = models.CharField(max_length=100, blank=True)
    copyrights = models.NullBooleanField()
    currently_owned_by = models.ManyToManyField(Owner)
    contact_telephone_number = models.CharField(max_length=100, blank=True)
    contact_email = models.CharField(max_length=100, blank=True)
    contact_website = models.CharField(max_length=100, blank=True)
    keywords = models.ManyToManyField(Keyword)
    uploadedfiles = models.ManyToManyField(UploadedFile, blank=True, null=True)
    general_comments = models.TextField(max_length=800, blank=True)
    team_comments = models.TextField(max_length=800, blank=True)
    other_comments = models.TextField(max_length=800, blank=True)
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey('auth.User', related_name='publications', on_delete=models.CASCADE, blank=True, null=True)


    #Fields that do not exist in excel sheet:
    venue = models.CharField(max_length=100, blank=True)
    illustration_and_layout_type = models.ManyToManyField(IllustrationLayoutType, blank=True, null=True)
    #create_countries()
   
    def __str__(self):
        return 'title_original: ' + self.title_original +',  title_subtitle_transcription ' + self.title_subtitle_transcription\
                + ', title_translation: ' + self.title_translation

