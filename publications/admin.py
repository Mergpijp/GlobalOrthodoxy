from django.contrib import admin

from .models import Publication, Genre

#class MembershipInline(admin.TabularInline):
#    model = Group.members.through

#class PublicationAdmin(admin.TabularInline):
#	model = Publication

#class GenreAdmin(admin.ModelAdmin):
#	inlines = [PublicationAdmin,]

#admin.site.register(Genre, GenreAdmin)
#admin.site.register(Publication)

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
#admin.site.register(PublicationAdmin)
#admin.site.register(GemreAdmin)