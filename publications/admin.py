from django.contrib import admin

from .models import Publication, Genre, Language, Author, Location, Document

class GenreInline(admin.TabularInline):
    model = Publication.genre.through

class GenreAdmin(admin.ModelAdmin):
    inlines = [
        GenreInline,
    ]

class PublicationAdmin(admin.ModelAdmin):
    inlines = [
        GenreInline,
    ]
    exclude = ('genre',)

admin.site.register(Publication, PublicationAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Language)
admin.site.register(Author)
admin.site.register(Location)
admin.site.register(Document)