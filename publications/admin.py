from django.contrib import admin

from django import forms
#from django_select2.forms import ModelSelect2Widget
from .models import Publication, Genre, Language, Author, Location, UploadedFile, Church, Owner, SpecialOccasion, IllustrationLayoutType, Translator, City
from .forms import NewCrispyForm
from . import models

class GenreInline(admin.TabularInline):
    model = Publication.content_genre.through

class AuthorInline(admin.TabularInline):
    model = Publication.author.through

class ChurchInline(admin.TabularInline):
    model = Publication.affiliated_church.through
    
class OwnerInline(admin.TabularInline):
    model = Publication.currently_owned_by.through

class SpecialOccasionInline(admin.TabularInline):
    model = Publication.connected_to_special_occasion.through

class IllustrationLayoutTypeInline(admin.TabularInline):
    model = Publication.illustration_and_layout_type.through

class LanguageInline(admin.TabularInline):
    model = Publication.language.through    

class TranslatorInline(admin.TabularInline):
    model = Publication.translator.through

class AuthorAdmin(admin.ModelAdmin):
    inline = [
        AuthorInline,
    ]
    
class TranslatorAdmin(admin.ModelAdmin):
    inline = [
        TranslatorInline,
    ]

class GenreAdmin(admin.ModelAdmin):
    inlines = [
        GenreInline,
    ]

class ChurchAdmin(admin.ModelAdmin):
    inlines = [
        ChurchInline,
    ]

class SpecialOccasionAdmin(admin.ModelAdmin):
    inlines = [
        SpecialOccasionInline,
    ]
    
class OwnerAdmin(admin.ModelAdmin):
    inlines = [
        OwnerInline,
    ]
    
class IllustrationLayoutTypeAdmin(admin.ModelAdmin):
    inlines = [
        IllustrationLayoutTypeInline,
    ]
class LanguageAdmin(admin.ModelAdmin):
    inlines = [
        LanguageInline,
    ]
  
class PublicationAdmin(admin.ModelAdmin):
    #form = AdminCrispyForm
    #add_form_template = "admin/form.html"
    
    inlines = [
        GenreInline,
        AuthorInline,
        ChurchInline,
        OwnerInline,
        SpecialOccasionInline,
        IllustrationLayoutTypeInline,
        LanguageInline,
        TranslatorInline,
    ]
    exclude = ('content_genre', 'author', 'affiliated_church', 'currently_owned_by', 'connected_to_special_occasion', 'illustration_and_layout', 'language', 'translator',)

admin.site.register(Publication, PublicationAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Church, ChurchAdmin)
admin.site.register(Owner, OwnerAdmin)
admin.site.register(SpecialOccasion, SpecialOccasionAdmin)
admin.site.register(IllustrationLayoutType, IllustrationLayoutTypeAdmin)
admin.site.register(Translator, TranslatorAdmin)
admin.site.register(Location)
admin.site.register(UploadedFile)
admin.site.register(City)