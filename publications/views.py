from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Publication, Author, Translator, FormOfPublication, Genre, Church, SpecialOccasion, Owner, City, Language, \
    IllustrationLayoutType, UploadedFile, Keyword, FileCategory, ImageContent
from django.views.generic import TemplateView, ListView
from django.db.models import Q
import random
import string
from .forms import PublicationForm, NewCrispyForm, KeywordForm,\
    AuthorForm, TranslatorForm, FormOfPublicationForm, GenreForm, ChurchForm, LanguageForm, CityForm, SpecialOccasionForm, \
    OwnerForm, IllustrationLayoutTypeForm, UploadedFileForm, CityForm, FileCategoryForm, ImageContentForm
from django.db.models.query import QuerySet
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
import re
from django_countries import countries
from django.utils import timezone
import datetime
import json
from django.urls import reverse
from django.core import serializers
from countries_plus.models import Country
from django.core.paginator import Paginator
from googletrans import Translator as GTranslator
from googletrans import LANGUAGES
from urllib.parse import urlencode
from collections import OrderedDict
from django import template
from django.db.models import Count
from django.db.models.functions import Lower
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pdb
import pytz
from PIL import Image
from django.db.models import OuterRef, Subquery

utc=pytz.UTC


register = template.Library()

countries_dict = dict([(y.lower(), x) for (x,y) in countries])
#languages_dict = dict([(x.lower(), y) for (x,y) in countries])
countries_list = [y for (x,y) in countries]
translator = GTranslator()

@login_required(login_url='/accounts/login/')
def process_file(request, pk=None):
    obj, created = UploadedFile.objects.get_or_create(pk=pk)
    post_mutable = {'image_title': request.POST['image_title'], 'filecategory': request.POST['filecategory'], \
                    'image_contents': request.POST['image_contents']}

    '''
    my_filter_qs = Q()
    for id in request.POST['publication'] :
        my_filter_qs = my_filter_qs | Q(id=id)
    if not my_filter_qs:
        post_mutable['publication'] = None
    else:
        post_mutable['publication'] = Publication.objects.filter(my_filter_qs)
    '''

    form = UploadedFileForm(post_mutable or None, request.FILES or None, instance=obj)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)

    return HttpResponse(status=500)

@login_required(login_url='/accounts/login/')
def view_input_update(request):
    if request.method == 'GET':
        if 'input' in request.GET:
            input = request.GET['input']
            language = translator.detect(input).lang
            return HttpResponse(LANGUAGES[language])
    return HttpResponse('ERROR')


'''
@register.simple_tag
@login_required(login_url='/accounts/login/')
def url_replace(request, field, value, direction=''):
    dict_ = request.GET.copy()

    if field == 'order_by' and field in dict_.keys():
      if dict_[field].startswith('-') and dict_[field].lstrip('-') == value:
        dict_[field] = value
      elif dict_[field].lstrip('-') == value:
        dict_[field] = "-" + value
      else:
        dict_[field] = direction + value
    else:
      dict_[field] = direction + value

    return urlencode(OrderedDict(sorted(dict_.items())))
'''

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
    #success_url = '/publication/show/'

    def get_success_url(self):
        """Detect the submit button used and act accordingly"""
        if 'next' in self.request.POST:
            return '/publication/show/'
        elif 'save' in self.request.POST:
            return '/publication/' + str(self.object.id) + '/edit/'

@login_required(login_url='/accounts/login/')
def PublicationDelete(request, pk):
    '''
    Deletes a publication 
    argument pk int value of the id of the to be deleted publication
    redirect to main publication page (Show)
    '''
    publication = Publication.objects.get(id=pk)
    #publication.delete()
    publication.is_deleted = True
    publication.save()
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
    #success_url = '/publication/show/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Detect the submit button used and act accordingly"""
        if 'next' in self.request.POST:
            return '/publication/show/'
        elif 'save' in self.request.POST:
            return '/publication/' + str(self.object.id) + '/edit/'

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
    s = re.sub('(sh|š)', '(sh|š)', s)
    s = re.sub('(s|ṣ)', '(s|ṣ)', s)
    s = re.sub('(d|ḍ)', '(d|ḍ)', s)
    s = re.sub('(th|ṯ)', '(th|ṯ)', s)
    s = re.sub('(t|ṭ)', '(t|ṭ)', s)
    s = re.sub('(z|ẓ)', '(z|ẓ)', s)
    s = re.sub('(g|h|ġ)', '(g|h|ġ)', s)
    s = re.sub('(g|j)', '(g|j)', s)
    s = re.sub('(kh|ḵ)', '(kh|ḵ)', s)
    s = re.sub('(ā|aa|a)', '(ā|aa|a)', s)
    s = re.sub('(á|a|aa|ae)', '(á|a|aa|ae)', s)
    s = re.sub('(ī|ee|i|ie)', '(ī|ee|i|ie)', s)
    s = re.sub('(ū|u|ou|oo|o|oe)', '(ū|u|ou|oo|o|oe)', s)
    s = re.sub("(3|')", "(3|')", s)
    s = re.sub('(ah|a)', '(ah|a)', s)
    s = re.sub('(dh|th|ḏ)', '(dh|th|ḏ)', s)
    s = re.sub('(ḥ|h)', '(ḥ|h)', s)
    #s = re.match("G[a-b].*", s)
    #x = re.compile(re.escape(s), re.IGNORECASE)
    #s = re.sub(x, s, s)
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
    #template_name = 'publications/show.html'
    context_object_name = 'publications'
    publications = Publication.objects.filter(is_deleted=False)
    paginate_by = 10
    #ordering = 'title_original'

    def get_template_names(self):
        if self.request.path == '/publication/overview/':
            return ['publications/overview.html']
        return ['publications/show.html']


    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

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
        is_a_translation =  self.request.GET.get('is_a_translation')

        publications = Publication.objects.filter(is_deleted=False)
        #publications = Publication.objects.filter(is_deleted=False).values('id').distinct()
        #publications = publications.filter(is_deleted=False)
        uploadedfiles = self.request.GET.getlist('uploadedfiles')
        uploadedfiles = UploadedFile.objects.filter(pk__in=uploadedfiles).all()
        keywords = self.request.GET.getlist('keywords')
        keywords = Keyword.objects.filter(pk__in=keywords).all()
        translated_from = self.request.GET.getlist('translated_From')
        translated_from = Language.objects.filter(pk__in=translated_from).all()
        city = self.request.GET.getlist('publication_city')
        country = self.request.GET.getlist('publication_country')
        collection_country = self.request.GET.getlist('collection_country')
        filecategory = self.request.GET.getlist('filecategory')
        filecategory = FileCategory.objects.filter(pk__in=filecategory).all()

        if list(collection_country) != ['']:
            collection_country = Country.objects.filter(pk__in=city).all()

        if list(country) != ['']:
            country = Country.objects.filter(pk__in=country).all()

        print('....', city)
        if list(city) != ['']:
            city = City.objects.filter(pk__in=city).all()

        print(publications)

        exclude = ['csrfmiddlewaretoken','search', 'order_by', 'direction']
        in_variables = [('author', authors), ('translator', translators), ('form_of_publication', form_of_publications), ('language',languages), ('affiliated_church', affiliated_churches) \
        , ('content_genre', content_genres), ('connected_to_special_occasion', connected_to_special_occasions), ('currently_owned_by', currently_owned_by),\
        ('uploadedfiles', uploadedfiles), ('publication_country', country), ('publication_city', city), ('collection_country', collection_country), \
        ('keywords', keywords), ('translated_from',translated_from), ('uploadedfiles__filecategory', filecategory),
                    ]
        special_case = ['copyrights', 'page', 'is_a_translation']

        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            if query_string.lower() in countries_dict.keys():
                query_string = countries_dict[query_string.lower()]


            search_fields = ['title_original', 'title_subtitle_transcription', 'title_translation', 'author__name', 'author__name_original_language', 'author__extra_info', \
                  'form_of_publication__name', 'editor', 'printed_by', 'published_by', 'publication_year', 'publication_country__name', 'publication_city__name', 'publishing_organisation', 'translator__name', 'translator__name_original_language', 'translator__extra_info', \
                  'language__name', 'language__direction', 'affiliated_church__name', 'extra_info', 'content_genre__name', 'connected_to_special_occasion__name', 'donor', 'content_description', 'description_of_illustration', \
                  'nr_of_pages', 'uploadedfiles__filecategory__name', 'uploadedfiles__uploaded_at', 'uploadedfiles__image_contents__name', \
                  'uploadedfiles__image_title', 'general_comments', 'team_comments', 'other_comments', 'keywords__name', 'is_a_translation', 'ISBN_number', 'translated_from__name', 'translated_from__direction', \
                  'title_original2', 'title_subtitle_transcription2', 'title_translation2', 'title_original3', 'title_subtitle_transcription3', 'title_translation3', \
                  'title_original4', 'title_subtitle_transcription4', 'title_translation4', 'title_original5', 'title_subtitle_transcription5', 'title_translation5', \
                  'currency', 'price', 'collection_context']

            if self.request.user.is_authenticated:
                search_fields.extend(['collection_date', 'collection_country__name', 'collection_venue_and_city', 'contact_telephone_number', 'contact_email', 'contact_website', 'currently_owned_by__name'])

            arabic_query = translator.translate(query_string, dest='ar').text
            query_string = to_searchable(query_string)
            #arabic_query = to_searchable(arabic_query)
            entry_query = get_query(query_string, search_fields)

            arabic_query = get_query(arabic_query, search_fields)
            print('&&&&&&', query_string)
            #publications = publications.filter(entry_query)
            #pdb.set_trace()
            publications = publications.filter(Q(entry_query) | Q(arabic_query))
            print(publications)
            ordering = self.get_ordering()
            if ordering is not None and ordering != "":
                publications = publications.order_by(ordering)
            publications = publications.distinct()

            #context['publications'] = publications
            return publications

        for field_name in self.request.GET:
            get_value = self.request.GET.get(field_name)
            if get_value != "" and not field_name in exclude and not field_name in [i[0] for i in in_variables] and\
               not field_name in special_case:
                print('******', field_name)
                arabic_query = translator.translate(get_value, dest='ar').text
                get_value = to_searchable(get_value)
                get_value = get_query(get_value, [field_name])
                arabic_query = get_query(arabic_query, [field_name])
                print('444444444', get_value)
                publications = publications.filter(Q(get_value) | Q(arabic_query))
                print('55555555555', publications)
                #publications = publications.filter(Q(**{field_name+'__regex':get_value}) | Q(**{field_name+'__icontains':arabic_query}) )

        for field_name, list_object in in_variables:
            print('****', list_object)
            if list_object:
                print('------', field_name)
                if list(list_object) != ['']:

                    publications = publications.filter(**{field_name+'__in': list_object})

        if str(copyrights) != "unknown" and str(copyrights) != "None":
            val = False
            if str(copyrights) == "yes":
                val = True
            print('11111', str(copyrights))
            publications = publications.filter(copyrights=val)

        print('666666', publications)

        if str(is_a_translation) != "unknown" and str(is_a_translation) != "None":
            val = False
            if str(is_a_translation) == "yes":
                val = True
            print('11111', str(is_a_translation))
            publications = publications.filter(is_a_translation=val)

        #publications = publications.distinct('id')
        print('777777', publications)
        #publications = Publication.objects.values_list('id', flat=True).distinct()
        #print(list(publications))
        #publications = Publication.objects.filter(id__in=publications)
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            if ordering == "author_name" or ordering == "-author_name":
                if ordering == "author_name":
                    author_subquery = Author.objects.filter(publication=OuterRef('pk')).order_by('name').values('name')
                else:
                    author_subquery = Author.objects.filter(publication=OuterRef('pk')).order_by('-name').values('name')
                publications = Publication.objects.annotate(author_name=Subquery(author_subquery)).order_by(ordering)
            elif ordering == "author_name_original_langauge" or ordering == "-author_name_original_langauge":
                if ordering == "author_name_original_langauge":
                    author_subquery = Author.objects.filter(publication=OuterRef('pk')).order_by('name_original_language').values('name_original_langauge')
                else:
                    author_subquery = Author.objects.filter(publication=OuterRef('pk')).order_by('-name_original_language').values('name_original_language')
                publications = Publication.objects.annotate(author_name_original_language=Subquery(author_subquery)).order_by(ordering)
            elif ordering == "author_extra_info" or ordering == "-author_extra_info":
                if ordering == "author_extra_info":
                    author_subquery = Author.objects.filter(publication=OuterRef('pk')).order_by('extra_info').values('extra_info')
                else:
                    author_subquery = Author.objects.filter(publication=OuterRef('pk')).order_by('-extra_info').values('extra_info')
                publications = Publication.objects.annotate(author_extra_info=Subquery(author_subquery)).order_by(ordering)
            elif ordering == "translator_name" or ordering == "-translator_name":
                if ordering == "translator_name":
                    translator_subquery = Translator.objects.filter(publication=OuterRef('pk')).order_by('name').values(
                        'name')
                else:
                    translator_subquery = Translator.objects.filter(publication=OuterRef('pk')).order_by('-name').values(
                        'name')
                publications = Publication.objects.annotate(translator_name=Subquery(translator_subquery)).order_by(ordering)
            elif ordering == "translator_name_original_language" or ordering == "-translator_name_original_language":
                if ordering == "translator_name_original_langauge":
                    translator_subquery = Translator.objects.filter(publication=OuterRef('pk')).order_by('name_original_language').values(
                        'name_original_language')
                else:
                    translator_subquery = Translator.objects.filter(publication=OuterRef('pk')).order_by('-name_original_language').values(
                        'name_original_language')
                publications = Publication.objects.annotate(translator_original_language=Subquery(translator_subquery)).order_by(ordering)
            elif ordering == "translator_extra_info" or ordering == "-translator_extra_info":
                if ordering == "translator_extra_info":
                    translator_subquery = Translator.objects.filter(publication=OuterRef('pk')).order_by('extra_info').values(
                        'extra_info')
                else:
                    translator_subquery = Translator.objects.filter(publication=OuterRef('pk')).order_by('-extra_info').values(
                        'extra_info')
                publications = Publication.objects.annotate(translator_extra_info=Subquery(translator_subquery)).order_by(ordering)
            elif ordering == "language_name" or ordering == "-language_name":
                if ordering == "language_name":
                    language_subquery = Language.objects.filter(publication=OuterRef('pk')).order_by('name').values(
                        'name')
                else:
                    language_subquery = Language.objects.filter(publication=OuterRef('pk')).order_by('-name').values(
                        'name')
                publications = Publication.objects.annotate(language_name=Subquery(language_subquery)).order_by(ordering)
            elif ordering == "content_genre_name" or ordering == "-content_genre_name":
                if ordering == "content_genre_name":
                    content_genre_subquery = Genre.objects.filter(publication=OuterRef('pk')).order_by('name').values(
                        'name')
                else:
                    content_genre_subquery = Genre.objects.filter(publication=OuterRef('pk')).order_by('-name').values(
                        'name')
                publications = Publication.objects.annotate(content_genre_name=Subquery(content_genre_subquery)).order_by(ordering)
            else:
                publications = publications.order_by(ordering)
        return publications

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        q = self.request.GET.get('q')
        if q is not None and q != "":
            context['q'] = q
        else:
            context['q'] = ''

        cover_images = []
        for pub in context['publications']:
            min = 9
            length = len(cover_images)
            inside = False
            for uploadedfile in pub.uploadedfiles.all():
                if uploadedfile.filecategory and uploadedfile.filecategory.list_view_priority:
                    compare = int(uploadedfile.filecategory.list_view_priority)
                    if compare < min:
                        min = compare
                        if inside:
                            cover_images = cover_images[:-1]
                        inside = True
                        cover_images.append(uploadedfile.file)
            if length == len(cover_images):
                date = datetime.datetime.now()
                date = date.replace(tzinfo=utc)
                inside = False
                for uploadedfile in pub.uploadedfiles.all():
                    if uploadedfile.uploaded_at and uploadedfile.uploaded_at < date and uploadedfile.file:
                        try:
                            im = Image.open(uploadedfile.file)
                            date = uploadedfile.uploaded_at
                            if inside:
                                cover_images = cover_images[:-1]
                            cover_images.append(uploadedfile.file)
                            inside = True
                        except IOError:
                            continue
            if length == len(cover_images):
                cover_images.append(None)
        print(context['publications'])
        context['publications'] = zip(context['publications'], cover_images)
        return context

class ThrashbinShow(ListView):
    '''
    Inherits ListView shows author mainpage (ThrashbinShow)
    Uses context_object_name authors for all keywords.
    '''
    model = Publication
    template_name = 'publications/thrashbin_show.html'
    context_object_name = 'publications'
    paginate_by = 10

    def get_queryset(self):
        publications = Publication.objects.filter(is_deleted=True)
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            publications = publications.order_by(ordering)
        return publications

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(ThrashbinShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

@login_required(login_url='/accounts/login/')
def ThrashbinRestore(request, pk):
    publication = Publication.objects.get(id=pk)
    publication.is_deleted = False
    publication.save()
    return redirect('/thrashbin/show')


class KeywordCreate(CreateView):
    '''
    Inherits CreateView uses a standard form for keywords.
    redirects to the keyword main page (show).
    '''
    template_name = 'publications/form.html'
    form_class = KeywordForm
    success_url = '/keyword/show/'

class KeywordShow(ListView):
    '''
    Inherits ListView shows author mainpage (keyword_show)
    Uses context_object_name keywords for all keywords.
    '''
    model = Keyword
    template_name = 'publications/keyword_show.html'
    context_object_name = 'keywords'
    paginate_by = 10

    def get_queryset(self):
        keywords = Keyword.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            keywords = keywords.order_by(ordering)
        return keywords

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(KeywordShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context


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

    def get_queryset(self):
        authors = Author.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            authors = authors.order_by(ordering)
        return authors

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(AuthorShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

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

    def get_queryset(self):
        translators = Translator.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            translators = translators.order_by(ordering)
        return translators

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(TranslatorShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

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

    def get_queryset(self):
        form_of_publications = FormOfPublication.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            form_of_publications = form_of_publications.order_by(ordering)
        return form_of_publications

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(FormOfPublicationShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

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

    def get_queryset(self):
        cities = City.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            cities = cities.order_by(ordering)
        return cities

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(CityShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context


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

    def get_queryset(self):
        genres = Genre.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            genres = genres.order_by(ordering)
        return genres

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(GenreShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

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

    def get_queryset(self):
        churches = Church.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            churches = churches.order_by(ordering)
        return churches

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(ChurchShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

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

    def get_queryset(self):
        languages = Language.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            languages = languages.order_by(ordering)
        return languages

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(LanguageShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

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

    def get_queryset(self):
        specialoccasions = SpecialOccasion.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            specialoccasions = specialoccasions.order_by(ordering)
        return specialoccasions

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(SpecialOccasionShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

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

    def get_queryset(self):
        owners = Owner.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            owners = owners.order_by(ordering)
        return owners

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(OwnerShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

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

    def get_queryset(self):
        uploadedfiles = UploadedFile.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            uploadedfiles = uploadedfiles.order_by(ordering)
        return uploadedfiles

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(UploadedFileShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

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


class FileCategoryCreate(CreateView):
    '''
    Inherits CreateView. Uses FileCategoryForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = FileCategoryForm
    success_url = '/filecategory/show/'


class FileCategoryShow(ListView):
    '''
    Inherits ListView.
    Uses Filecategory as model.
    Uses filecategory_show.html as template_name.
    Set context_object_name to filecategories.
    '''
    model = FileCategory
    template_name = 'publications/filecategory_show.html'
    context_object_name = 'filecategories'
    paginate_by = 10

    def get_queryset(self):
        filecategories = FileCategory.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            filecategories = filecategories.order_by(ordering)
        return filecategories

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(FileCategoryShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context


@login_required(login_url='/accounts/login/')
def FileCategoryDelete(request, pk):
    '''
    Arguments: request, pk
    Selects filecategory object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    filecategory = FileCategory.objects.get(id=pk)
    filecategory.delete()
    return redirect('/filecategory/show')


class FileCategoryUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses FilecategoryForm as layout. And model FileCategory.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = FileCategoryForm
    model = FileCategory
    success_url = '/filecategory/show/'

class ImageContentCreate(CreateView):
    '''
    Inherits CreateView. Uses ImageContentForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = ImageContentForm
    success_url = '/imagecontent/show/'


class ImageContentShow(ListView):
    '''
    Inherits ListView.
    Uses imagecontent as model.
    Uses imagecontent_show.html as template_name.
    Set context_object_name to imagecontents.
    '''
    model = ImageContent
    template_name = 'publications/imagecontent_show.html'
    context_object_name = 'imagecontents'
    paginate_by = 10

    def get_queryset(self):
        imagecontents = ImageContent.objects.all()
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            imagecontents = imagecontents.order_by(ordering)
        return imagecontents

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(ImageContentShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context


@login_required(login_url='/accounts/login/')
def ImageContentDelete(request, pk):
    '''
    Arguments: request, pk
    Selects imagecontent object by id equals pk.
    Deletes the object.
    redirects to main page. (show)
    '''
    imagecontent = ImageContent.objects.get(id=pk)
    imagecontent.delete()
    return redirect('/imagecontent/show')


class ImageContentUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses ImageContentForm as layout. And model ImageContent.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = ImageContentForm
    model = ImageContent
    success_url = '/imagecontent/show/'

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
            if(field_name == None or field_name == ""):
                continue
            q = Q(**{"%s__iregex" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    #pdb.set_trace()
    return query    
         