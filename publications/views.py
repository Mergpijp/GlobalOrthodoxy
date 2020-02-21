from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Publication, Author, Translator, FormOfPublication, Genre, Church, SpecialOccasion, Owner, City, Language, IllustrationLayoutType, UploadedFile, Keyword
from django.views.generic import TemplateView, ListView
from django.db.models import Q
import random
import string
from .forms import PublicationForm, NewCrispyForm, KeywordForm,\
    AuthorForm, TranslatorForm, FormOfPublicationForm, GenreForm, ChurchForm, LanguageForm, CityForm, SpecialOccasionForm, OwnerForm, IllustrationLayoutTypeForm, UploadedFileForm, CityForm
from django.db.models.query import QuerySet
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
import re
from django_countries import countries
from django.utils import timezone
import json
from django.core import serializers
from countries_plus.models import Country
from django.core.paginator import Paginator
from googletrans import Translator as GTranslator
from googletrans import LANGUAGES

countries_dict = dict([(y.lower(), x) for (x,y) in countries])
#languages_dict = dict([(x.lower(), y) for (x,y) in countries])
countries_list = [y for (x,y) in countries]
translator = GTranslator()


def view_input_update(request):
    if request.method == 'GET':
        if 'input' in request.GET:
            input = request.GET['input']
            language = translator.detect(input).lang
            return HttpResponse(LANGUAGES[language])
    return HttpResponse('ERROR')

class PublicationUpdate(UpdateView):
    '''
    Inherits UpdateView
    Uses edit/create template and the edit/create NewCrispyForm
    Uses Publication as model
    redirects to main page of Publication (publication show) 
    '''
    template_name = 'publications/form_create.html'
    form_class = NewCrispyForm
    model = Publication
    success_url = '/publication/show/'

@login_required(login_url='/accounts/login/')
def PublicationDelete(request, pk):
    '''
    Deletes a publication 
    argument pk int value of the id of the to be deleted publication
    redirect to main publication page (Show)
    '''
    publication = Publication.objects.get(id=pk)
    publication.delete()
    return redirect('/publication/show')

class PublicationCreate(CreateView):
    '''
    inherits CreateView
    Uses template for creating/updating.
    Uses standard edit/new form (NewCrispyForm)
    redirect to publication main page (publication show)
    '''
    template_name = 'publications/form_create.html'
    form_class = NewCrispyForm
    success_url = '/publication/show/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class PublicationDetailView(DetailView):
    '''
    Inherits DetailView
    Detailview for publication
    Usess now in template thus the function get_context_data
    '''
    model = Publication
    
    def get_context_data(self, **kwargs):
        self.object = []
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context 
        
@login_required(login_url='/accounts/login/')        
def render_search(request):
    '''
    Initialize the home page with a form to search publications
    '''
    form = PublicationForm()
    return render(request, 'publications/form_search.html', {'form': form})

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def to_searchable(s):
    s.replace('sh', 'š')
    s.replace('s', 'ṣ')
    s.replace('d', 'ḍ')
    s.replace('th', 'ṯ')
    s.replace('t', 'ṭ')
    s.replace('ẓ', 'z')


    return s


class SearchResultsView(ListView):
    '''
    ListView of the initial search page.
    The function get_queryset works for the search bar and the search form home page.
    The search bar typically uses q for query otherwise a id for list search.
    Use a countries_dict to convert for example Netherlands to NL so that search succeeds.
    If a normal field is searched use __icontains if a list element is searched use: __in.
    '''
    model = Publication
    template_name = 'publications/show.html'
    context_object_name = 'publications'
    publications = Publication.objects.all()
    #paginator = Paginator(publications, 25)
    paginate_by = 10
      
    def get_queryset(self): 
        
        #form = PublicationForm(self.request.GET)
        authors = self.request.GET.getlist('author')
        translators = self.request.GET.getlist('translator')
        authors = Author.objects.filter(pk__in=authors).all()
        translators = Translator.objects.filter(pk__in=translators).all()
        form_of_publications = self.request.GET.getlist('form_of_publication')
        form_of_publications = FormOfPublication.objects.filter(pk__in=form_of_publications).all()
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
        uploadedfiles = self.request.GET.getlist('uploadedfiles')
        uploadedfiles = UploadedFile.objects.filter(pk__in=uploadedfiles).all()
        keywords = self.request.GET.getlist('keywords')
        keywords = Keyword.objects.filter(pk__in=keywords).all()

        translated_from = self.request.GET.getlist('translated_From')
        city = self.request.GET.getlist('publication_city')
        country = self.request.GET.getlist('publication_country')
        collection_country = self.request.GET.getlist('collection_country')

        if list(collection_country) != ['']:
            collection_country = Country.objects.filter(pk__in=city).all()

        if list(country) != ['']:
            country = Country.objects.filter(pk__in=city).all()

        if list(translated_from) != ['']:
            translated_from = Country.objects.filter(pk__in=translated_from).all()

        print('....', city)
        if list(city) != ['']:
            city = City.objects.filter(pk__in=city).all()

        print(publications)

        exclude = ['csrfmiddlewaretoken','search']
        in_variables = [('author', authors), ('translator', translators), ('form_of_publication', form_of_publications), ('language',languages), ('affiliated_church', affiliated_churches) \
        , ('content_genre', content_genres), ('connected_to_special_occasion', connected_to_special_occasions), ('currently_owned_by', currently_owned_by), \
        ('uploadedfiles', uploadedfiles), ('publication_country', country), ('publication_city', city), ('collection_country', collection_country), ('keywords', keywords), ('translated_from',translated_from)]
        special_case = ['copyrights', 'page']
       
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            if query_string.lower() in countries_dict.keys():
                query_string = countries_dict[query_string.lower()]
            search_fields = ['title_original', 'title_subtitle_transcription', 'title_subtitle_European', 'title_translation', 'author__name', 'author__year_of_birth', \
                  'form_of_publication__name', 'printed_by', 'published_by', 'publication_date', 'publication_country__name', 'publication_city__name', 'publishing_organisation', 'translator__name', \
                  'language__name', 'language__direction', 'affiliated_church__name', 'content_genre__name', 'connected_to_special_occasion__name', 'possible_donor', 'content_description', 'description_of_illustration', \
                  'image_details', 'nr_of_pages', 'collection_date', 'collection_country__name', 'collection_venue_and_city', 'contact_telephone_number', 'contact_email', 'contact_website', \
                  'currently_owned_by__name', 'uploadedfiles__description', 'uploadedfiles__uploaded_at', 'comments', 'keywords__name', 'is_translated', 'ISBN_number', 'translated_from__name']
            entry_query = get_query(query_string, search_fields)
            arabic_query = translator.translate(query_string, dest='ar').text
            arabic_query = get_query(arabic_query, search_fields)
            print('&&&&&&', query_string)
            #publications = publications.filter(entry_query)
            publications = publications.filter(Q(entry_query) | Q(arabic_query))
            print(publications)
            publications = publications.distinct()
            return publications
       
        for field_name in self.request.GET:
            get_value = self.request.GET.get(field_name)
            if get_value != "" and not field_name in exclude and not field_name in [i[0] for i in in_variables] and\
               not field_name in special_case:
                print('******', field_name)
                arabic_query = translator.translate(get_value, dest='ar').text
                publications = publications.filter(Q(**{field_name+'__icontains':get_value}) | Q(**{field_name+'__icontains':arabic_query}) )
        
        for field_name, list_object in in_variables:
            print('****', list_object)
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

        publications = publications.distinct()
        return publications

class KeywordCreate(CreateView):
    '''
    Inherits CreateView uses a standard form for keywords.
    redirects to the author main page (show).
    '''
    template_name = 'publications/form.html'
    form_class = KeywordForm
    success_url = '/keyword/show/'

class KeywordShow(ListView):
    '''
    Inherits ListView shows author mainpage (keyword_show)
    Uses context_object_name authors for all keywords.
    '''
    model = Keyword
    template_name = 'publications/keyword_show.html'
    context_object_name = 'keywords'
    paginate_by = 10

@login_required(login_url='/accounts/login/')
def KeywordDelete(request, pk):
    '''
    Arguments: request, pk
    Selects keyword object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    keyword = Keyword.objects.get(id=pk)
    keyword.delete()
    return redirect('/keyword/show')

class KeywordUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses KeywordForm as layout. And model Keyword.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = KeywordForm
    model = Keyword
    success_url = '/keyword/show/'

class AuthorCreate(CreateView):
    '''
    Inherits CreateView uses a standard form for Authors.
    redirects to the author main page (show).
    '''
    template_name = 'publications/form.html'
    form_class = AuthorForm
    success_url = '/author/show/'

class AuthorShow(ListView):
    '''
    Inherits ListView shows author mainpage (author_show)
    Uses context_object_name authors for all authors.
    '''
    model = Author
    template_name = 'publications/author_show.html'
    context_object_name = 'authors'
    paginate_by = 10

@login_required(login_url='/accounts/login/')
def AuthorDelete(request, pk):
    '''
    Arguments: request, pk
    Selects author object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    author = Author.objects.get(id=pk)
    author.delete()
    return redirect('/author/show')

class AuthorUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses AuthorForm as layout. And model Author.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = AuthorForm
    model = Author
    success_url = '/author/show/'
        
class TranslatorCreate(CreateView):
    '''
    Inherits CreateView. Uses TranslatorForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = TranslatorForm
    success_url = '/translator/show/'

class TranslatorShow(ListView):
    '''
    Inherits ListView.
    Uses Translator as model.
    Uses translator_show.html as template_name.
    Set context_object_name to translators.
    '''
    model = Translator
    template_name = 'publications/translator_show.html'
    context_object_name = 'translators'
    paginate_by = 10

@login_required(login_url='/accounts/login/')
def TranslatorDelete(request, pk):
    '''
    Arguments: request, pk
    Selects translator object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    translator = Translator.objects.get(id=pk)
    translator.delete()
    return redirect('/translator/show')

class TranslatorUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses TranslatorForm as layout. And model Translator.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = TranslatorForm
    model = Translator
    success_url = '/translator/show/'
    
class FormOfPublicationCreate(CreateView):
    '''
    Inherits CreateView. Uses FormOfPublicationForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = FormOfPublicationForm
    success_url = '/form_of_publication/show/'

class FormOfPublicationShow(ListView):
    '''
    Inherits ListView.
    Uses FormOfPublication as model.
    Uses form_of_publication_show.html as template_name.
    Set context_object_name to form_of_publications.
    '''
    model = FormOfPublication
    template_name = 'publications/form_of_publication_show.html'
    context_object_name = 'form_of_publications'
    paginate_by = 10

@login_required(login_url='/accounts/login/')
def FormOfPublicationDelete(request, pk):
    '''
    Arguments: request, pk
    Selects form_of_publication object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    form_of_publication = FormOfPublication.objects.get(id=pk)
    form_of_publication.delete()
    return redirect('/form_of_publication/show')

class FormOfPublicationUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses FormOfPublicationForm as layout. And model FormOfPublication.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = FormOfPublicationForm
    model = FormOfPublication
    success_url = '/form_of_publication/show/'

class CityCreate(CreateView):
    '''
    Inherits CreateView. Uses CityForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = CityForm
    success_url = '/city/show/'

class CityShow(ListView):
    '''
    Inherits ListView.
    Uses City as model.
    Uses city_show.html as template_name.
    Set context_object_name to cities.
    '''
    model = City
    template_name = 'publications/city_show.html'
    context_object_name = 'cities'
    paginate_by = 10

@login_required(login_url='/accounts/login/')
def CityDelete(request, pk):
    '''
    Arguments: request, pk
    Selects city object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    city = City.objects.get(id=pk)
    city.delete()
    return redirect('/city/show')

class CityUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses CityForm as layout. And model City.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = CityForm
    model = City
    success_url = '/city/show/'
    
        
class GenreCreate(CreateView):
    '''
    Inherits CreateView. Uses GenreForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = GenreForm
    success_url = '/genre/show/'

class GenreShow(ListView):
    '''
    Inherits ListView.
    Uses Genre as model.
    Uses genre_show.html as template_name.
    Set context_object_name to genres.
    '''
    model = Genre
    template_name = 'publications/genre_show.html'
    context_object_name = 'genres'
    paginate_by = 10

@login_required(login_url='/accounts/login/')
def GenreDelete(request, pk):
    '''
    Arguments: request, pk
    Selects genre object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    genre = Genre.objects.get(id=pk)
    genre.delete()
    return redirect('/genre/show')

class GenreUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses GenreForm as layout. And model Genre.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = GenreForm
    model = Genre
    success_url = '/genre/show/'
        
class ChurchCreate(CreateView):
    '''
    Inherits CreateView. Uses ChurchForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = ChurchForm
    success_url = '/church/show/'

class ChurchShow(ListView):
    '''
    Inherits ListView.
    Uses Church as model.
    Uses church_show.html as template_name.
    Set context_object_name to churches.
    '''
    model = Church
    template_name = 'publications/church_show.html'
    context_object_name = 'churches'
    paginate_by = 10

@login_required(login_url='/accounts/login/')
def ChurchDelete(request, pk):
    '''
    Arguments: request, pk
    Selects church object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    church = Church.objects.get(id=pk)
    church.delete()
    return redirect('/church/show')

class ChurchUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses ChurchForm as layout. And model Church.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = ChurchForm
    model = Church
    success_url = '/church/show/'
      
class LanguageCreate(CreateView):
    '''
    Inherits CreateView. Uses LanguageForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = LanguageForm
    success_url = '/language/show/'
    
class LanguageShow(ListView):
    '''
    Inherits ListView.
    Uses Language as model.
    Uses language_show.html as template_name.
    Set context_object_name to languages.
    '''
    model = Language
    template_name = 'publications/language_show.html'
    context_object_name = 'languages'
    paginate_by = 10
    
@login_required(login_url='/accounts/login/')
def LanguageDelete(request, pk):
    '''
    Arguments: request, pk
    Selects language object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    language = Language.objects.get(id=pk)
    language.delete()
    return redirect('/language/show')

 
class LanguageUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses LanguageForm as layout. And model Language.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = LanguageForm
    model = Language
    success_url = '/language/show/'
    
class SpecialOccasionCreate(CreateView):
    '''
    Inherits CreateView. Uses SpecialOccasionForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = SpecialOccasionForm
    success_url = '/special_occasion/show/'
    
class SpecialOccasionShow(ListView):
    '''
    Inherits ListView.
    Uses SpecialOccasion as model.
    Uses specialoccasion_show.html as template_name.
    Set context_object_name to specialoccasions.
    '''
    model = SpecialOccasion
    template_name = 'publications/specialoccasion_show.html'
    context_object_name = 'specialoccasions'
    paginate_by = 10
    
@login_required(login_url='/accounts/login/')
def SpecialOccasionDelete(request, pk):
    '''
    Arguments: request, pk
    Selects special_occasion object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    special_occasion = SpecialOccasion.objects.get(id=pk)
    special_occasion.delete()
    return redirect('/special_occasion/show')

class SpecialOccasionUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses SpecialOccasionForm as layout. And model SpecialOccasion.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = SpecialOccasionForm
    model = SpecialOccasion
    success_url = '/special_occasion/show/'   

class OwnerCreate(CreateView):
    '''
    Inherits CreateView. Uses OwnerForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = OwnerForm
    success_url = '/owner/show/'
    
class OwnerShow(ListView):
    '''
    Inherits ListView.
    Uses Owner as model.
    Uses owner_show.html as template_name.
    Set context_object_name to owners.
    '''
    model = Owner
    template_name = 'publications/owner_show.html'
    context_object_name = 'owners'
    paginate_by = 10
    
@login_required(login_url='/accounts/login/')
def OwnerDelete(request, pk):
    '''
    Arguments: request, pk
    Selects owner object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    owner = Owner.objects.get(id=pk)
    owner.delete()
    return redirect('/owner/show')

class OwnerUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses OwnerForm as layout. And model Owner.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = OwnerForm
    model = Owner
    success_url = '/owner/show/'  

class UploadedFileCreate(CreateView):
    '''
    Inherits CreateView. Uses UploadedFileForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = UploadedFileForm
    success_url = '/uploadedfile/show/'   
    
class UploadedFileShow(ListView):
    '''
    Inherits ListView.
    Uses UploadedFile as model.
    Uses uploadedfile_show.html as template_name.
    Set context_object_name to uploadedfiles.
    '''
    model = UploadedFile
    template_name = 'publications/uploadedfile_show.html'
    context_object_name = 'uploadedfiles'
    paginate_by = 10
    
@login_required(login_url='/accounts/login/')
def UploadedFileDelete(request, pk):
    '''
    Arguments: request, pk
    Selects uploadedfile object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    uploadedfile = UploadedFile.objects.get(id=pk)
    uploadedfile.delete()
    return redirect('/uploadedfile/show')

class UploadedFileUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses UploadedFileForm as layout. And model UploadedFileForm.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = UploadedFileForm
    model = UploadedFile
    success_url = '/uploadedfile/show/'  

class IllustrationLayoutTypeCreate(CreateView):
    '''
    Inherits CreateView. Uses IllustrationLayoutTypeForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = IllustrationLayoutTypeForm
    success_url = '/illustration_layout_type/show/'
    
class IllustrationLayoutTypeShow(ListView):
    '''
    Inherits ListView.
    Uses IllustrationLayoutType as model.
    Uses illustration_layout_type_show.html as template_name.
    Set context_object_name to IllustrationLayoutTypes.
    '''
    model = IllustrationLayoutType
    template_name = 'publications/illustration_layout_type_show.html'
    context_object_name = 'IllustrationLayoutTypes'
    paginate_by = 10
    
@login_required(login_url='/accounts/login/')
def IllustrationLayoutTypeDelete(request, pk):
    '''
    Arguments: request, pk
    Selects illustration_layout_type object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    illustration_layout_type = IllustrationLayoutType.objects.get(id=pk)
    illustration_layout_type.delete()
    return redirect('/illustration_layout_type/show')

class IllustrationLayoutTypeUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses IllustrationLayoutTypeForm as layout. And model IllustrationLayoutType.
    redirects to local main page. (show)
    '''
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
         