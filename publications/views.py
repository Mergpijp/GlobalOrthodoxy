from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Publication, Author
from .forms import PublicationForm
from django.views.generic import TemplateView, ListView
from django.db.models import Q
import random
import string
from .forms import NameForm, PublicationForm
from django.db.models.query import QuerySet

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
                if not isinstance(form.cleaned_data[key], QuerySet):
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
        any_input = False
        if title_original != "":
            object_list = object_list.filter(title_original__icontains=title_original)
            any_input = True
        if title_subtitle_transcription != "":
            object_list = object_list.filter(title_subtitle_transcription__icontains=title_subtitle_transcription)
            any_input = True
        if title_subtitle_european != "":
            object_list = object_list.filter(title_subtitle_european__icontains=title_subtitle_european)
            any_input = True
        if title_translation != "":
            object_list = object_list.filter(title_translation__icontains=title_translation)
            any_input = True
        if not any_input:
            return object_list
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
