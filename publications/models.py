from django.db import models
from enum import Enum
from django import forms
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from countries_plus.models import Country
from time import gmtime, strftime
import datetime
from django.utils import timezone
import os
from django.core.files.storage import default_storage


MINIMUM_YEAR = 1850
MINIMUM_YEAR_PUBLICATION = 1970
MAX_CHARS = 100
MAX_CHARS_NEW_A = 35

MAX_CHARS_NEW = 50

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
    description = models.CharField(max_length=1000, blank=True)
	
    def __str__(self):
        return self.name
 
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
        return self.name

class Author(models.Model):
    '''
    Manytomany field class with firstname and lastname as charfields.
    Year of birth as integer between 1850 and current year.
    '''
    name = models.CharField(max_length=100, blank=True)
    name_original_language = models.CharField(max_length=100, blank=True)
    extra_info = models.CharField(max_length=400, blank=True)
	
    def __str__(self):
        return self.name +  ' ' + self.name_original_language

    @property
    def get_truncated_name_new(self):
        x = self.name
        if len(x) > MAX_CHARS_NEW_A:
            x = x[:MAX_CHARS_NEW_A] + '...'
        return x

    @property
    def get_truncated_name_original_language_new(self):
        x = self.name_original_language
        if len(x) > MAX_CHARS_NEW_A:
            x = x[:MAX_CHARS_NEW_A] + '...'
        return x

    @property
    def get_truncated_extra_info_new(self):
        x = self.extra_info
        if len(x) > MAX_CHARS_NEW_A:
            x = x[:MAX_CHARS_NEW_A] + '...'
        return x


class Translator(models.Model):
    '''
    Manytomany field class with two fields firstname and lastname both charfields.
    '''
    name = models.CharField(max_length=100, blank=True)
    name_original_language = models.CharField(max_length=100, blank=True)
    extra_info = models.CharField(max_length=400, blank=True)
   
    def __str__(self):
        return self.name +  ' ' + self.name_original_language

    @property
    def get_truncated_name_new(self):
        x = self.name
        if len(x) > MAX_CHARS_NEW_A:
            x = x[:MAX_CHARS_NEW_A] + '...'
        return x

    @property
    def get_truncated_name_original_language_new(self):
        x = self.name_original_language
        if len(x) > MAX_CHARS_NEW_A:
            x = x[:MAX_CHARS_NEW_A] + '...'
        return x

    @property
    def get_truncated_extra_info_new(self):
        x = self.extra_info
        if len(x) > MAX_CHARS_NEW_A:
            x = x[:MAX_CHARS_NEW_A] + '...'
        return x
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
    authors = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_churches_list', null=True, blank=True)
    
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

    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)

    coordinates_requested = models.BooleanField(default=False)
    coordinates_known = models.BooleanField(default=False)

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
    description = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.name

class ImageContentCategory(models.Model):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class UploadedFile(models.Model):
    '''
    Manytomany field class with three fields.
    A charfield, filefield and DateTimeField.
    The DateTimeField will be automatically added.
    '''
    image_title = models.CharField(max_length=255, blank=True)
    filecategory = models.ForeignKey(FileCategory, on_delete=models.CASCADE, related_name="filecategory", null=True, blank=True)
    image_contents = models.CharField(max_length=1000, blank=True)
    image_content_category = models.ForeignKey(ImageContentCategory, on_delete=models.CASCADE, related_name="image_content_category", null=True, blank=True)
    file = models.FileField(upload_to='files/%Y/%m/%d/%H/%M/%S/%f/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    main_color = models.CharField(max_length=255, blank=True)
    secondary_color = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.image_title

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def chunks(self):
        if not default_storage.exists(self.file.name):
            return ''
        chunks = [c for c in self.file.chunks()]
        return chunks

    def size(self):
        if not default_storage.exists(self.file.name):
            return 0
        return self.file.size
    class Meta:
        ordering = ('filecategory__order_index',)

    @property
    def get_truncated_image_title_new(self):
        x = self.image_title
        if len(x) > MAX_CHARS_NEW_A:
            x = x[:MAX_CHARS_NEW_A] + '...'
        return x

    @property
    def get_truncated_filecategory_new(self):
        if self.filecategory:
            x = self.filecategory.name
            if len(x) > MAX_CHARS_NEW_A:
                x = x[:MAX_CHARS_NEW_A] + '...'
            return x
        return ''

    @property
    def get_truncated_image_contents_new(self):
        x = self.image_contents
        if len(x) > MAX_CHARS_NEW_A:
            x = x[:MAX_CHARS_NEW_A] + '...'
        return x

CHOICES = (
    (None, "Unknown"),
    (True, "Yes"),
    (False, "No")
)

CURRENCIES = ['unknown', 'EUR: Euro', 'GBP: Pound sterling', \
              'SEK: Swedish krona', \
              'NLD: Dutch gulden', 'AUS: Austrian Schiling','GRM: German Mark',\
              'MAL: Maltese Lira', 'BEF: Belgian Franc', 'GRD: Greek Drachma', 'CYP: Cypriot Pound', 'IRP: Irish Pound', \
              'PTE: Portugese Escudo', 'ESK: Estonian Kroon', 'ITL: Italian Lira', 'SLK: Slovak Koruna', 'FNM: Finnish Markka',\
              'LAL: Latvian Lats', 'SLT: Slovenian Tolar', 'FRF: French Franc', 'LIL: Lituanian Litas', 'SPP: Spanish Peseta',\
              'LXF: Luxembourgian Franc', 'ALL: Albanian Lek', 'BAM: Bosnia and Herzegovina convertible mark',\
              'BGN: Bulgarian Lev', 'HRK: Croatian Kuna', 'CZK: Czech Koruna', 'DKK: Danish Krone',\
              'HUF: Hungarian Forint', 'ISK: Icelandic Krona', 'CHF: Swiss Franc', 'MDL: Moldovan Leu', 'MKD: Second Macedonian Denar',\
              'NOK: Norwegian Krone', 'PLN: Polish Zloty', 'RON: Romanian Leu', 'RSD: Serbian Dinar',\
              'SEK: Swedish Kronar', 'CHF: Swiss Franc', 'TRY: Turkish Lira', 'UAH: Ukrainian Hryvnia', \
              'USD: United States Dollar', 'CAD: Canadian Dollar', 'AUD: Australian Dollar', 'EGP: Egyptian pound',\
              'LBP: Libanese pound', 'ETB: Ethopian birr', 'ERN: Eritrean nakfa', 'ILS: Israeli shekel', 'AMD: Armenian dram', \
              'GEL: Geogrian Lari', 'BYN: Belarusian Ruble', 'RUB: Russian Ruble']

CURRENCY_CHOICES = [(str(i), CURRENCIES[i]) for i in range(0, len(CURRENCIES))]


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

    title = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription = models.CharField(max_length=300, blank=True)
    title_translation = models.CharField(max_length=300, blank=True)
    title2 = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription2 = models.CharField(max_length=300, blank=True)
    title_translation2 = models.CharField(max_length=300, blank=True)
    title3 = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription3 = models.CharField(max_length=300, blank=True)
    title_translation3 = models.CharField(max_length=300, blank=True)
    title4 = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription4 = models.CharField(max_length=300, blank=True)
    title_translation4 = models.CharField(max_length=300, blank=True)
    title5 = models.CharField(max_length=300, blank=True)
    title_subtitle_transcription5 = models.CharField(max_length=300, blank=True)
    title_translation5 = models.CharField(max_length=300, blank=True)
    pdf_url = models.URLField(max_length=500, blank=True)
    authors = models.ManyToManyField(Author)
    translators = models.ManyToManyField(Translator)
    form_of_publication = models.ManyToManyField(FormOfPublication)
    editor = models.CharField(max_length=100, blank=True)
    ISBN_number = models.CharField(max_length=100, blank=True)
    printed_by = models.CharField(max_length=100, blank=True)
    published_by = models.CharField(max_length=100, blank=True)
    publication_year = models.IntegerField(blank=True, null=True)
    publication_country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    publication_city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    publishing_organisation = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=25, choices=CURRENCY_CHOICES, default='0')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_periodical = models.BooleanField(default=False)
    start_year = models.IntegerField(blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)
    ongoing = models.NullBooleanField(choices=CHOICES)
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
    collection_venue_and_city = models.CharField('Collection venue', max_length=100, blank=True)
    collection_context = models.TextField(max_length=800, blank=True)
    copyrights = models.NullBooleanField()
    currently_owned_by = models.ManyToManyField(Owner)
    contact_telephone_number = models.CharField(max_length=100, blank=True)
    contact_email = models.CharField(max_length=100, blank=True)
    contact_website = models.URLField(max_length=200, blank=True)
    keywords = models.ManyToManyField(Keyword)
    uploadedfiles = models.ManyToManyField(UploadedFile, blank=True, null=True)
    general_comments = models.TextField(max_length=3000, blank=True)
    team_comments = models.TextField(max_length=3000, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_stub = models.BooleanField(default=False)
    created_by = models.ForeignKey('auth.User', related_name='publications', on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    collection_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='collection_city', null=True, blank=True)

    #Fields that do not exist in excel sheet:
    venue = models.CharField(max_length=100, blank=True)
    illustration_and_layout_type = models.ManyToManyField(IllustrationLayoutType, blank=True, null=True)
    #create_countries()
   
    def __str__(self):
        return 'title: ' + self.title +',  title_subtitle_transcription ' + self.title_subtitle_transcription\
                + ', title_translation: ' + self.title_translation

    @property
    def get_truncated_title(self):
        x = self.title
        if len(x) > MAX_CHARS:
            x = x[:MAX_CHARS] + '...'
        return x

    @property
    def get_truncated_title_translation(self):
        x = self.title_translation
        if len(x) > MAX_CHARS:
            x = x[:MAX_CHARS] + '...'
        return x

    @property
    def get_truncated_title_new(self):
        x = self.title
        if len(x) > MAX_CHARS_NEW:
            x = x[:MAX_CHARS_NEW] + '...'
        return x

    @property
    def get_truncated_title_translation_new(self):
        x = self.title_translation
        if len(x) > MAX_CHARS_NEW:
            x = x[:MAX_CHARS_NEW] + '...'
        return x

    @property
    def get_truncated_title_subtitle_transcription(self):
        x = self.title_subtitle_transcription
        if len(x) > MAX_CHARS:
            x = x[:MAX_CHARS] + '...'
        return x

    @property
    def get_truncated_author_name(self):
        authors = self.authors
        x = ', '.join([author.name for author in authors.all()])
        if len(x) > MAX_CHARS:
            x = x[:MAX_CHARS] + '...'
        return x

    @property
    def get_truncated_author_name_original_language(self):
        authors = self.authors
        x = ', '.join([author.name_original_language for author in authors.all()])
        if len(x) > MAX_CHARS:
            x = x[:MAX_CHARS] + '...'
        return x

    @property
    def get_truncated_author_extra_info(self):
        authors = self.authors
        x = ', '.join([author.extra_info for author in authors.all()])
        if len(x) > MAX_CHARS:
            x = x[:MAX_CHARS] + '...'
        return x

    @property
    def get_truncated_translator_name(self):
        translators = self.translators
        x = ', '.join([translator.name for translator in translators.all()])
        if len(x) > MAX_CHARS:
            x = x[:MAX_CHARS] + '...'
        return x

    @property
    def get_truncated_translator_name_original_language(self):
        translators = self.translators
        x = ', '.join([translator.name_original_language for translator in translators.all()])
        if len(x) > MAX_CHARS:
            x = x[:MAX_CHARS] + '...'
        return x


    @property
    def get_truncated_translator_extra_info(self):
        translators = self.translators
        x = ', '.join([translator.extra_info for translator in translators.all()])
        if len(x) > MAX_CHARS:
            x = x[:MAX_CHARS] + '...'
        return x






