from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Publication, Author, Translator, Genre, Church, SpecialOccasion, Owner, City, Language, IllustrationLayoutType, Document
from django.views.generic import TemplateView, ListView
from django.db.models import Q
import random
import string
from .forms import PublicationForm, NewCrispyForm, AuthorForm, TranslatorForm, GenreForm, ChurchForm, LanguageForm, CityForm, SpecialOccasionForm, OwnerForm, IllustrationLayoutTypeForm, DocumentForm, CityForm
from django.db.models.query import QuerySet
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
import re
from django_countries import countries

class PublicationUpdate(UpdateView):
    template_name = 'publications/form_create.html'
    form_class = NewCrispyForm
    model = Publication
    success_url = '/publication/show/'

@login_required(login_url='/accounts/login/')
def PublicationDelete(request, pk):
    publication = Publication.objects.get(id=pk)
    publication.delete()
    return redirect('/publication/show')

class PublicationCreate(CreateView):
    template_name = 'publications/form_create.html'
    form_class = NewCrispyForm
    success_url = '/publication/show/'
    
@login_required(login_url='/accounts/login/')        
def render_search(request):
    form = PublicationForm()
    return render(request, 'publications/form_search.html', {'form': form})


countries_dict = dict([(y.lower(), x) for (x,y) in countries])

class SearchResultsView(ListView):
    model = Publication
    template_name = 'publications/show.html'
    context_object_name  = 'publications'
      
    def get_queryset(self): # new
        
        form = PublicationForm(self.request.GET)
        if not form.is_valid():
            form = PublicationForm()
            return render(self.request, 'publications/form_search.html', {'form': form})
        authors = self.request.GET.getlist('author')
        translators = self.request.GET.getlist('translator')
        authors = Author.objects.filter(pk__in=authors).all()
        translators = Translator.objects.filter(pk__in=translators).all()
        languages = self.request.GET.getlist('language')
        languages = Language.objects.filter(pk__in=languages).all()
        affiliated_churches = self.request.GET.getlist('affiliated_church')
        affiliated_churches = Church.objects.filter(pk__in=affiliated_churches).all()
        content_genres = self.request.GET.getlist('content_genre')
        content_genres = Genre.objects.filter(pk__in=content_genres).all()
        connected_to_special_occasions = self.request.GET.getlist('connected_to_special_occasion')
        connected_to_special_occasions = SpecialOccasion.objects.filter(pk__in=connected_to_special_occasions).all()
        currently_owned_by = self.request.GET.getlist('currently_owned_by')
        currently_owned_by = Owner.objects.filter(pk__in=currently_owned_by).all()
        copyrights = self.request.GET.get('copyrights')
        publications = Publication.objects.all()
        documents = self.request.GET.getlist('documents')
        documents = Document.objects.filter(pk__in=documents).all()
        city = self.request.GET.getlist('publication_city')
        print('....', city)
        if list(city) != ['']:
            city = City.objects.filter(pk__in=city).all()
        #else:
            #city = QuerySet()
        print(publications)

        exclude = ['csrfmiddlewaretoken','search']
        in_variables = [('author', authors), ('translator', translators), ('language',languages), ('affiliated_church', affiliated_churches) \
        , ('content_genre', content_genres), ('connected_to_special_occasion', connected_to_special_occasions), ('currently_owned_by', currently_owned_by), \
        ('documents', documents), ('publication_city', city)]
        special_case = ['copyrights']
       
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            if query_string.lower() in countries_dict.keys():
                query_string = countries_dict[query_string.lower()]
            entry_query = get_query(query_string, ['title_original', 'title_subtitle_transcription', 'title_subtitle_European', 'title_translation', 'author__firstname', 'author__lastname', \
                  'form_of_publication', 'printed_by', 'published_by', 'publication_date', 'publication_country', 'publication_city__name', 'publishing_organisation', 'translator__firstname', \
                  'translator__lastname', 'language__name', 'affiliated_church__name', 'content_genre__name', 'connected_to_special_occasion__name', 'possible_donor', 'content_description', 'description_of_illustration', \
                  'image_details', 'nr_of_pages', 'collection_date', 'collection_country', 'collection_venue_and_city', 'contact_info', 'currently_owned_by__name', 'documents__description', \
                  'comments'])

            print('&&&&&&', query_string)
            publications = publications.filter(entry_query)
            print(publications)
            publications = publications.distinct()
            return publications
       
        for field_name in self.request.GET:
            get_value = self.request.GET.get(field_name)
            #if get_value == 'publication_country':
            #    continue
            #print('||||||', get_value)
            #if field_name == 'publication_country':
            #    continue
            if get_value != "" and not field_name in exclude and not field_name in [i[0] for i in in_variables] and\
               not field_name in special_case:
                print('******', field_name)
                publications = publications.filter(**{field_name+'__icontains':get_value})
                #publications = publications.filter(title__icontains, 'ein')
        
        for field_name, list_object in in_variables:
            #print('------>',var)
            #publications = publications.filter(**{'author__in':authors})
            #print('9999',publications)
            print('****', list_object)
            #if field_name == 'publication_city':
            #    continue
            if list_object:
                print('------', field_name)
                if list(list_object) != ['']:
                    
                    publications = publications.filter(**{field_name+'__in': list_object})


        if str(copyrights) != "unknown" and str(copyrights) != "None":
            val = False
            if str(copyrights):
                val = True
            print('11111', str(copyrights))
            publications = publications.filter(copyrights=val)

        #publications = publications.filter(publication_city__in=City))
        #print(publications)
        publications = publications.distinct()
        return publications

class AuthorCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = AuthorForm
    success_url = '/author/show/'

class AuthorShow(ListView):
    model = Author
    template_name = 'publications/author_show.html'
    context_object_name = 'authors'

@login_required(login_url='/accounts/login/')
def AuthorDelete(request, pk):
    author = Author.objects.get(id=pk)
    author.delete()
    return redirect('/author/show')

class AuthorUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = AuthorForm
    model = Author
    success_url = '/author/show/'
        
class TranslatorCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = TranslatorForm
    success_url = '/translator/show/'

class TranslatorShow(ListView):
    model = Translator
    template_name = 'publications/translator_show.html'
    context_object_name = 'translators'

@login_required(login_url='/accounts/login/')
def TranslatorDelete(request, pk):
    translator = Translator.objects.get(id=pk)
    translator.delete()
    return redirect('/translator/show')

class TranslatorUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = TranslatorForm
    model = Translator
    success_url = '/translator/show/'

class CityCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = CityForm
    success_url = '/city/show/'

class CityShow(ListView):
    model = City
    template_name = 'publications/city_show.html'
    context_object_name = 'cities'

@login_required(login_url='/accounts/login/')
def CityDelete(request, pk):
    city = City.objects.get(id=pk)
    city.delete()
    return redirect('/city/show')

class CityUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = CityForm
    model = City
    success_url = '/city/show/'
    
        
class GenreCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = GenreForm
    success_url = '/genre/show/'

class GenreShow(ListView):
    model = Genre
    template_name = 'publications/genre_show.html'
    context_object_name = 'genres'

@login_required(login_url='/accounts/login/')
def GenreDelete(request, pk):
    genre = Genre.objects.get(id=pk)
    genre.delete()
    return redirect('/genre/show')

class GenreUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = GenreForm
    model = Genre
    success_url = '/genre/show/'
        
class ChurchCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = ChurchForm
    success_url = '/church/show/'

class ChurchShow(ListView):
    model = Church
    template_name = 'publications/church_show.html'
    context_object_name = 'churches'

@login_required(login_url='/accounts/login/')
def ChurchDelete(request, pk):
    church = Church.objects.get(id=pk)
    church.delete()
    return redirect('/church/show')

class ChurchUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = ChurchForm
    model = Church
    success_url = '/church/show/'
      
class LanguageCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = LanguageForm
    success_url = '/language/show/'
    
class LanguageShow(ListView):
    model = Language
    template_name = 'publications/language_show.html'
    context_object_name = 'languages'
    
@login_required(login_url='/accounts/login/')
def LanguageDelete(request, pk):
    language = Language.objects.get(id=pk)
    language.delete()
    return redirect('/language/show')

 
class LanguageUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = LanguageForm
    model = Language
    success_url = '/language/show/'
    
class SpecialOccasionCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = SpecialOccasionForm
    success_url = '/special_occasion/show/'
    
class SpecialOccasionShow(ListView):
    model = SpecialOccasion
    template_name = 'publications/specialoccasion_show.html'
    context_object_name = 'specialoccasions'
    
@login_required(login_url='/accounts/login/')
def SpecialOccasionDelete(request, pk):
    special_occasion = SpecialOccasion.objects.get(id=pk)
    special_occasion.delete()
    return redirect('/special_occasion/show')

class SpecialOccasionUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = SpecialOccasionForm
    model = SpecialOccasion
    success_url = '/special_occasion/show/'   

class OwnerCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = OwnerForm
    success_url = '/owner/show/'
    
class OwnerShow(ListView):
    model = Owner
    template_name = 'publications/owner_show.html'
    context_object_name = 'owners'
    
@login_required(login_url='/accounts/login/')
def OwnerDelete(request, pk):
    owner = Owner.objects.get(id=pk)
    owner.delete()
    return redirect('/owner/show')

class OwnerUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = OwnerForm
    model = Owner
    success_url = '/owner/show/'  

class DocumentCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = DocumentForm
    success_url = '/document/show/'   
    
class DocumentShow(ListView):
    model = Document
    template_name = 'publications/document_show.html'
    context_object_name = 'documents'
    
@login_required(login_url='/accounts/login/')
def DocumentDelete(request, pk):
    document = Document.objects.get(id=pk)
    document.delete()
    return redirect('/document/show')

class DocumentUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = DocumentForm
    model = Document
    success_url = '/document/show/'  

class IllustrationLayoutTypeCreate(CreateView):
    template_name = 'publications/form.html'
    form_class = IllustrationLayoutTypeForm
    success_url = '/illustration_layout_type/show/'
    
class IllustrationLayoutTypeShow(ListView):
    model = IllustrationLayoutType
    template_name = 'publications/illustration_layout_type_show.html'
    context_object_name = 'IllustrationLayoutTypes'
    
@login_required(login_url='/accounts/login/')
def IllustrationLayoutTypeDelete(request, pk):
    illustration_layout_type = IllustrationLayoutType.objects.get(id=pk)
    illustration_layout_type.delete()
    return redirect('/illustration_layout_type/show')

class IllustrationLayoutTypeUpdate(UpdateView):
    template_name = 'publications/form.html'
    form_class = IllustrationLayoutTypeForm
    model = IllustrationLayoutType
    success_url = '/illustration_layout_type/show/'  

def normalize_query(query_string,
    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
    normspace=re.compile(r'\s{2,}').sub):

    '''
    Splits the query string in invidual keywords, getting rid of unecessary spaces and grouping quoted words together.
    Example:
    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    '''

    return [normspace(' ',(t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):

    '''
    Returns a query, that is a combination of Q objects. 
    That combination aims to search keywords within a model by testing the given search fields.
    '''

    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query    
         