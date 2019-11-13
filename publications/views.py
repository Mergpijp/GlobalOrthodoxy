from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Publication

def index(request):
    #return HttpResponse("Hello, world. You're at the publication index.")
    latest_publication_list = Publication.objects.all()
    context = {
        'latest_publication_list': latest_publication_list,
    }
    return render(request, 'publications/index.html', context)
	
def detail(request, publication_id):
	publication = get_object_or_404(Publication, pk=publication_id)
	return render(request, 'publications/detail.html', {'publication': publication})
