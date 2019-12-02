from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Publication, Author, Translator, Genre, Church, SpecialOccasion, Owner, City
from django.views.generic import TemplateView, ListView
from django.db.models import Q
import random
import string
from .forms import NameForm, PublicationForm
from django.db.models.query import QuerySet
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

'''
@login_required(login_url='/accounts/login/')
def my_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        ...
    else:
        # Return an 'invalid login' error message.
        ...
'''
@login_required(login_url='/accounts/login/')        
def get_name(request):
    # if this is a GET request we need to process the form data
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = PublicationForm(request.GET)
            
        # check whether it's valid:
        if form.is_valid():
            #print(form.cleaned_data)
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            print(form.cleaned_data)
            valid = False
            for key in form.cleaned_data.keys():
                if not isinstance(form.cleaned_data[key], QuerySet) and form.cleaned_data[key] != None:
                    if form.cleaned_data[key] != "":
                        valid = True
                else:
                    if form.cleaned_data[key]:
                        valid = True
            if not valid:
                print(form.cleaned_data)
                return render(request, 'index.html', {'form': form})
            print("check: " + str(valid))
            print(form.cleaned_data)
            return HttpResponseRedirect("/search")
        #print('form not valid')
    # if a GET (or any other method) we'll create a blank form
    else:
        print(form.cleaned_data)
        form = PublicationForm()

    return render(request, 'index.html', {'form': form})
    
class HomePageView(TemplateView):
    template_name = 'home.html'
    
    def home(request):
        author_list = Author.objects.all()
        
        return render(request, 'templates/home.html', {'authors': author_list})

class SearchResultsView(ListView):
    model = Publication
    template_name = 'search_results.html'
        
    def get_queryset(self): # new
        title_original = self.request.GET.get('title_original')
        title_subtitle_transcription = self.request.GET.get('title_subtitle_transcription')
        title_subtitle_european = self.request.GET.get('title_subtitle_european')
        title_translation = self.request.GET.get('title_translation')
        authors = self.request.GET.getlist('author')
        translators = self.request.GET.getlist('translator')
        authors = Author.objects.filter(pk__in=authors).all()
        translators = Translator.objects.filter(pk__in=translators).all()
        form_of_publication = self.request.GET.get('form_of_publication')
        printed_by = self.request.GET.get('printed_by')
        published_by = self.request.GET.get('published_by')
        publication_date = self.request.GET.get('publication_date')
        publication_country = self.request.GET.get('publication_country')
        publication_city = self.request.GET.get('publication_city')
        publishing_organisation = self.request.GET.get('publishing_organisation')
        possible_donor = self.request.GET.get('possible_donor')
        affiliated_churches = self.request.GET.getlist('affiliated_church')
        affiliated_churches = Church.objects.filter(pk__in=affiliated_churches).all()
        languages = self.request.GET.getlist('language')
        content_description = self.request.GET.get('content_description')
        content_genres = self.request.GET.getlist('content_genre')
        content_genres = Genre.objects.filter(pk__in=content_genres).all()
        connected_to_special_occasions = self.request.GET.getlist('connected_to_special_occasion')
        connected_to_special_occasions = SpecialOccasion.objects.filter(pk__in=connected_to_special_occasions).all()
        description_of_illustration = self.request.GET.get('description_of_illustration')
        image_details = self.request.GET.get('image_details')
        nr_of_pages = self.request.GET.get('nr_of_pages')
        collection_date = self.request.GET.get('collection_date')
        collection_country = self.request.GET.get('collection_country')
        collection_venue_and_city = self.request.GET.get('collection_venue_and_city')
        copyrights = self.request.GET.get('copyrights')
        currently_owned_by = self.request.GET.getlist('currently_owned_by')
        currently_owned_by = Owner.objects.filter(pk__in=currently_owned_by).all()
        contact_info = self.request.GET.get('contact_info')
        comments = self.request.GET.get('comments')
        
        
        
       
        object_list = Publication.objects.all()
        print(object_list)
        '''
        FIELDS = [('title_original',False, False),('title_subtitle_transcription',False, False),('title_subtitle_european',False, False), ('title_translation', False, False),('authors',True, False) \
                  ('translators', True, False), ('form_of_publication', False, False), ('printed_by', False, False), ('published_by', False, False), ('publication_date', False, True), ('publication_country', False, False \
                  ('publication_city',]
        received_results = {}
        
        for field, islist, isnone in FIELDS:
        
            if islist:
                received_results[field] = self.request.GET.getlist(field)
            else:
                received_results[field] = self.request.GET.get(field)
        '''
        
        if title_original != "":
            object_list = object_list.filter(title_original__icontains=title_original)
        if title_subtitle_transcription != "":
            object_list = object_list.filter(title_subtitle_transcription__icontains=title_subtitle_transcription)
        if title_subtitle_european != "":
            object_list = object_list.filter(title_subtitle_european__icontains=title_subtitle_european)
        if title_translation != "":
            object_list = object_list.filter(title_translation__icontains=title_translation)
        for author in authors:
            object_list = object_list.filter(author__firstname__iexact = author.firstname, \
                               author__lastname__iexact = author.lastname)
        for translator in translators:
            object_list = object_list.filter(translator__firstname__iexact = translator.firstname, \
                               translator__lastname__iexact = translator.lastname)
                       
        if form_of_publication != "":
            object_list = object_list.filter(form_of_publication__icontains=form_of_publication) 
        if printed_by != "":
            object_list = object_list.filter(printed_by__icontains=printed_by)   
        if published_by != "":
            object_list = object_list.filter(published_by__icontains=published_by)
        if publication_date != "":
            object_list = object_list.filter(publication_date__icontains=publication_date) 
        if publication_country != "":
            object_list = object_list.filter(publication_country__icontains=publication_country)
        
        if publication_city != "":
            object_list = object_list.filter(publication_city__name__icontains=publication_city)
        if publishing_organisation != "":
            object_list = object_list.filter(publishing_organisation__icontains=publishing_organisation)
        if possible_donor != "":
            object_list = object_list.filter(possible_donor__icontains=possible_donor)
        for church in affiliated_churches:
            object_list = object_list.filter(affiliated_church__name__iexact = church.name)
        for language in languages:
            object_list = object_list.filter(language__name__iexact = language.name)
        if content_description != "":
            object_list = object_list.filter(content_description__icontaints = content_description)
        for genre in content_genres:
            object_list = object_list.filter(genre__name__iexact = genre.name)
        for occasion in connected_to_special_occasions:
            object_list = object_list.filter(special_occasion__name__iexact = occasion.name)
        if description_of_illustration != "":
            object_list = object_list.filter(description_of_illustration__icontains=description_of_illustration)
        if image_details != "":
            object_list = object_list.filter(image_details__icontains=image_details)
        if nr_of_pages != "":
            object_list = object_list.filter(nr_of_pages__icontains=nr_of_pages)
        if collection_date != "":
            object_list = object_list.filter(collection_date__icontains=collection_date)
        if collection_country != "":
            object_list = object_list.filter(collection_country__icontains=collection_country)
        if collection_venue_and_city != "":
            object_list = object_list.filter(collection_venue_and_city__icontains=collection_venue_and_city)
        if str(copyrights) != "unknown":
            object_list = object_list.filter(copyrights__iexact=copyrights)
        for owner in currently_owned_by:
            object_list = object_list.filter(owner__name__iexact = owner.name)
        if contact_info != "":
            object_list = object_list.filter(contact_info__icontains=contact_info)
        if comments != "":
            object_list = object_list.filter(comments__icontains=comments)
        #print('after: ' + str(object_list))    
        
        return object_list
        
# def index(request):
    #return HttpResponse("Hello, world. You're at the publication index.")
    # latest_publication_list = Publication.objects.all()
    # context = {
        # 'latest_publication_list': latest_publication_list,
    # }
    # return render(request, 'publications/index.html', context)
	
# def detail(request, publication_id):
	# publication = get_object_or_404(Publication, pk=publication_id)
	# return render(request, 'publications/detail.html', {'publication': publication})
    
# def publication_new(request):
    # form = PublicationForm()
    # return render(request, 'publication/publication_edit.html', {'form': form})
