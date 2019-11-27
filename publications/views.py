from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Publication, Author, Translator
from .forms import PublicationForm
from django.views.generic import TemplateView, ListView
from django.db.models import Q
import random
import string
from .forms import NameForm, PublicationForm
from django.db.models.query import QuerySet
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

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
                return render(request, 'index.html', {'form': form})
            print("check: " + str(valid))
            return HttpResponseRedirect("/search")
        #print('form not valid')
    # if a GET (or any other method) we'll create a blank form
    else:
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
        '''
        N = 20
        if title_original == "":
            title_original = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        if title_subtitle_transcription == "":
            title_subtitle_transcription = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        if title_subtitle_european == "":
            title_subtitle_european = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        if title_translation == "":
            title_translation = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
            
        object_list = Publication.objects.filter(
            Q(title_original__icontains=title_original) | Q(title_subtitle_transcription__icontains=title_subtitle_transcription) |
            Q(title_subtitle_european__icontains=title_subtitle_european) | Q(title_translation__icontains=title_translation)     
        )
        '''
        object_list = Publication.objects.all()
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
