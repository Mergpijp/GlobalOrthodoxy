from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Publication, Author, Translator, FormOfPublication, Genre, Church, SpecialOccasion, Owner, City, Language, \
    IllustrationLayoutType, UploadedFile, Keyword, FileCategory
from django.views.generic import TemplateView, ListView
from django.db.models import Q
import random
import string
from django.db.models.functions import Coalesce
from .forms import PublicationForm, NewCrispyForm, KeywordForm,\
    AuthorForm, TranslatorForm, FormOfPublicationForm, GenreForm, ChurchForm, LanguageForm, CityForm, SpecialOccasionForm, \
    OwnerForm, IllustrationLayoutTypeForm, UploadedFileForm, CityForm, FileCategoryForm
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
import traceback
from itertools import chain
import itertools
from collections import Counter
from django.core.exceptions import ImproperlyConfigured
import json
from django.urls import reverse
from django.core import serializers
from countries_plus.models import Country
from django.core.paginator import Paginator
from googletrans import Translator as GTranslator
from django.contrib.auth.models import User
from django.conf import settings

from googletrans import LANGUAGES
from django.template.loader import render_to_string
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
from bootstrap_modal_forms.generic import BSModalCreateView
from django.urls import reverse_lazy
from .forms import UploadedFileModelForm
from bootstrap_modal_forms.generic import (
  BSModalCreateView,
  BSModalUpdateView,
  BSModalReadView,
  BSModalDeleteView
)
import csv

from excel_response import ExcelResponse
from os.path import isfile


utc=pytz.UTC


register = template.Library()

countries_dict = dict([(y.lower(), x) for (x,y) in countries])
#languages_dict = dict([(x.lower(), y) for (x,y) in countries])
countries_list = [y for (x,y) in countries]
translator = GTranslator(service_urls=['translate.googleapis.com'])


@login_required(login_url='/accounts/login/')
def nothing(request):
    return HttpResponse(status=200)

@login_required(login_url='/accounts/login/')
def get_countries(request):
    query = request.GET.get('term', None)
    if query:
        result_countries = [(x,y) for (x,y) in countries if query in y]
    else:
        result_countries = countries
    list_of_countries_dict = []
    for idx, (x,y) in enumerate(result_countries):
        list_of_countries_dict.append({'id': idx, 'text': y, 'code': x})
    #pdb.set_trace()
    return JsonResponse({'results': list_of_countries_dict}, safe=False)

@login_required(login_url='/accounts/login/')
def city_proces(request):
    post_mutable = {'name': request.POST['name'], 'country': request.POST['country']}
    form = CityForm(post_mutable or None, instance=None)
    #pdb.set_trace()
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            return HttpResponse()
    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def filecategory_ajax(request):
    query = request.GET.get('term', None)
    if query:
        filecategories = FileCategory.objects.filter(name__icontains=query).values("pk", "name")
    else:
        filecategories = FileCategory.objects.values("pk", "name")
    filecategories = list(filecategories)
    for d in filecategories:
        d['id'] = d.pop('pk')
        d['text'] = d.pop('name')
    return JsonResponse({'results':filecategories}, safe=False)

@login_required(login_url='/accounts/login/')
def process_file(request, pk=None, pkb=None):
    obj, created = UploadedFile.objects.get_or_create(pk=pk)
    data = dict()

    #try:
    #pdb.set_trace()
    post_mutable = {'image_title': request.POST['image_title'], 'filecategory': request.POST['filecategory'], \
                    'image_contents': request.POST['image_contents']}
    #except:
    #    return HttpResponse(status=200)

    # '''
    # my_filter_qs = Q()
    # for id in request.POST['publication'] :
    #     my_filter_qs = my_filter_qs | Q(id=id)
    # if not my_filter_qs:
    #     post_mutable['publication'] = None
    # else:
    #     post_mutable['publication'] = Publication.objects.filter(my_filter_qs)
    # '''

    form = UploadedFileForm(post_mutable or None, request.FILES or None, instance=obj)
    #pdb.set_trace()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            pub = Publication.objects.get(pk=pkb)
            #return HttpResponse(status=200)
            data['table'] = render_to_string(
                '_uploadedfiles_table.html',
                {'publication': pub},
                request=request
            )
            return JsonResponse(data)

    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def process_file2(request, pkb=None):
    data = dict()
    obj, created = UploadedFile.objects.get_or_create(pk=None)

    post_mutable = {'image_title': request.POST['image_title'], 'filecategory': request.POST['filecategory'], \
                    'image_contents': request.POST['image_contents']}

    form = UploadedFileForm(post_mutable or None, request.FILES or None, instance=obj)

    if request.method == 'POST':
        #pdb.set_trace()
        if form.is_valid():
            instance = form.save()

            IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG']

            #In an image, create a small version
            if instance.file.path.split('.')[-1] in IMAGE_EXTENSIONS:

                from PIL import Image

                SMALL_FILE_SIZE = 400
                image = Image.open(instance.file.path)
                image.thumbnail((SMALL_FILE_SIZE, SMALL_FILE_SIZE), Image.ANTIALIAS)

                small_file_path = instance.file.path
                for extension in ['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG']:
                    small_file_path = small_file_path.replace('.'+extension, '_small.'+extension)

                if '.png' in small_file_path.lower():
                    file_type = 'PNG'
                else:
                    file_type = 'JPEG'

                image.save(small_file_path,file_type)

            #Link to publication
            if pkb:
                pub = Publication.objects.get(pk=pkb)
                pub.uploadedfiles.add(instance)
                pub.save()

                data['table'] = render_to_string(
                    '_uploadedfiles_table.html',
                    {'publication': pub},
                    request=request
                )
                return JsonResponse(data)

    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def process_author(request, pkb=None, pk=None):
    #pdb.set_trace()
    data = dict()
    obj, created = Author.objects.get_or_create(pk=pk)

    post_mutable = {'name': request.POST['name'], 'name_original_language': request.POST['name_original_language'], \
                    'extra_info': request.POST['extra_info']}

    form = AuthorForm(post_mutable or None, instance=obj)

    if request.method == 'POST':
        if form.is_valid():
            #pdb.set_trace()
            instance = form.save()
            pub = Publication.objects.get(pk=pkb)
            pub.authors.add(instance)
            pub.save()
            if pkb:
                data['table'] = render_to_string(
                    '_authors_table.html',
                    {'publication': pub},
                    request=request
                )
                return JsonResponse(data)

    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def process_translator(request, pkb=None, pk=None):
    data = dict()
    obj, created = Translator.objects.get_or_create(pk=pk)

    post_mutable = {'name': request.POST['name'], 'name_original_language': request.POST['name_original_language'], \
                    'extra_info': request.POST['extra_info']}

    form = TranslatorForm(post_mutable or None, instance=obj)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            pub = Publication.objects.get(pk=pkb)
            pub.translators.add(instance)
            pub.save()
            if pkb:
                data['table'] = render_to_string(
                    '_translators_table.html',
                    {'publication': pub},
                    request=request
                )
                return JsonResponse(data)

    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def proces_language(request):
    post_mutable = {'name': request.POST['name'], 'direction': request.POST['direction']}
    form = LanguageForm(post_mutable or None, instance=None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            return HttpResponse()
    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def proces_form_of_publication(request):
    post_mutable = {'name': request.POST['name']}
    form = FormOfPublicationForm(post_mutable or None, instance=None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            return HttpResponse()
    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def church_proces(request):
    post_mutable = {'name': request.POST['name']}
    form = ChurchForm(post_mutable or None, instance=None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            return HttpResponse()
    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def genre_proces(request):
    post_mutable = {'name': request.POST['name']}
    form = GenreForm(post_mutable or None, instance=None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            return HttpResponse()
    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def occasion_proces(request):
    post_mutable = {'name': request.POST['name']}
    form = SpecialOccasionForm(post_mutable or None, instance=None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            return HttpResponse()
    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def ownedby_proces(request):
    post_mutable = {'name': request.POST['name']}
    form = OwnerForm(post_mutable or None, instance=None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            return HttpResponse()
    return render(request, 'error_template.html', {'form': form}, status=500)

@login_required(login_url='/accounts/login/')
def filecategory_proces(request):
    post_mutable = {'name': request.POST['name'], 'list_view_priority': request.POST['list_view_priority'],
                    'order_index': request.POST['order_index']}
    form = FileCategoryForm(post_mutable or None, instance=None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save()
            return HttpResponse()
    return render(request, 'error_template.html', {'form': form}, status=500)


@login_required(login_url='/accounts/login/')
def link_file(request, pkb=None, pk=None):
    data = dict()
    if pkb and pk:
        pub = Publication.objects.get(pk=pkb)
        file = UploadedFile.objects.get(pk=pk)
        if not file in pub.uploadedfiles.all():
            pub.uploadedfiles.add(file)
            pub.save()
            data['table'] = render_to_string(
                '_uploadedfiles_table.html',
                {'publication': pub},
                request=request
            )
            return JsonResponse(data)
        else:
            return HttpResponse(409)

@login_required(login_url='/accounts/login/')
def link_author(request, pkb=None, pk=None):
    data = dict()
    #pdb.set_trace()
    if pkb and pk:
        pub = Publication.objects.get(pk=pkb)
        author = Author.objects.get(pk=pk)
        if not author in pub.authors.all():
            pub.authors.add(author)
            pub.save()
            author.save()
            data['table'] = render_to_string(
                '_authors_table.html',
                {'publication': pub},
                request=request
            )
            return JsonResponse(data)
        else:
            data['table'] = render_to_string(
                '_authors_table.html',
                {'publication': pub},
                request=request
            )
            return JsonResponse(data)
        return HttpResponse(409)

@login_required(login_url='/accounts/login/')
def link_translator(request, pkb=None, pk=None):
    data = dict()
    if pkb and pk:
        pub = Publication.objects.get(pk=pkb)
        translator = Translator.objects.get(pk=pk)
        if not translator in pub.translators.all():
            pub.translators.add(translator)
            pub.save()
            data['table'] = render_to_string(
                '_translators_table.html',
                {'publication': pub},
                request=request
            )
            return JsonResponse(data)
        else:
            data['table'] = render_to_string(
                '_translators_table.html',
                {'publication': pub},
                request=request
            )
            return JsonResponse(data)
    return HttpResponse(409)

@login_required(login_url='/accounts/login/')
def unlink_file(request, pkb=None, pk=None):
    data = dict()
    if pkb and pk:
        pub = Publication.objects.get(pk=pkb)
        file = UploadedFile.objects.get(pk=pk)
        if file in pub.uploadedfiles.all():
            pub.uploadedfiles.remove(file)
            pub.save()
            data['table'] = render_to_string(
                '_uploadedfiles_table.html',
                {'publication': pub},
                request=request
            )
            return JsonResponse(data)
        else:
            return HttpResponse(409)

@login_required(login_url='/accounts/login/')
def unlink_author(request, pkb=None, pk=None):
    data = dict()
    if pkb and pk:
        pub = Publication.objects.get(pk=pkb)
        author = Author.objects.get(pk=pk)
        if author in pub.authors.all():
            pub.authors.remove(author)
            pub.save()
            data['table'] = render_to_string(
                '_authors_table.html',
                {'publication': pub},
                request=request
            )
            return JsonResponse(data)
        else:
            return HttpResponse(409)

@login_required(login_url='/accounts/login/')
def unlink_translator(request, pkb=None, pk=None):
    data = dict()
    if pkb and pk:
        pub = Publication.objects.get(pk=pkb)
        translator = Translator.objects.get(pk=pk)
        if translator in pub.translators.all():
            pub.translators.remove(translator)
            pub.save()
            data['table'] = render_to_string(
                '_translators_table.html',
                {'publication': pub},
                request=request
            )
            return JsonResponse(data)
        else:
            return HttpResponse(409)



@login_required(login_url='/accounts/login/')
def view_input_update(request):
    return HttpResponse(200)
    if request.method == 'GET':
        if 'input' in request.GET:
            input = request.GET['input']
            language = translator.detect(input).lang
            return HttpResponse(LANGUAGES[language])
    return HttpResponse('ERROR')

'''
@login_required(login_url='/accounts/login/')
def search_uploaded_files(request):
    if request.method == 'GET':
        if 'input' in request.GET:
            input = request.GET['input']
            uploadedfiles = UploadedFile.objects.filter(image_title=input).order_by('image_title')[:10]
            return render(request, 'search_files_dropdown_list.html', {'uploadedfiles': uploadedfiles})
    return HttpResponse('ERROR')
'''
@login_required(login_url='/accounts/login/')
def search_uploaded_files(request, pkb=None):
    data = dict()
    if request.method == 'POST':
        if pkb:
            if 'input' in request.POST:
                input = request.POST['input']
                uploadedfiles = UploadedFile.objects.filter(image_title__icontains=input).order_by('image_title')[:10]
            else:
                uploadedfiles = UploadedFile.objects.none()
            publication = Publication.objects.get(pk=pkb)
            data['table'] = render_to_string(
                '_uploadedfiles_candidates_table.html',
                {'uploadedfiles': uploadedfiles, 'publication': publication},
                request=request
            )
            return JsonResponse(data)

@login_required(login_url='/accounts/login/')
def search_authors(request, pkb=None):
    data = dict()
    if request.method == 'POST':
        if pkb:
            if 'input' in request.POST:
                input = request.POST['input']
                authors = Author.objects.filter(Q(name__icontains=input) | Q(name_original_language__icontains=input)| Q(extra_info__icontains=input)).order_by('name')[:10]
            else:
                authors = Author.objects.none()
            #pdb.set_trace()
            publication = Publication.objects.get(pk=pkb)
            data['table'] = render_to_string(
                '_authors_candidates_table.html',
                {'authors': authors, 'publication': publication},
                request=request
            )
            return JsonResponse(data)

@login_required(login_url='/accounts/login/')
def search_translators(request, pkb=None):
    data = dict()
    if request.method == 'POST':
        if pkb:
            if 'input' in request.POST:
                input = request.POST['input']
                translators = Translator.objects.filter(Q(name__icontains=input) | Q(name_original_language__icontains=input)| Q(extra_info__icontains=input)).order_by('name')[:10]
            else:
                translators = Translator.objects.none()
            publication = Publication.objects.get(pk=pkb)
            data['table'] = render_to_string(
                '_translators_candidates_table.html',
                {'translators': translators, 'publication': publication},
                request=request
            )
            return JsonResponse(data)

@login_required(login_url='/accounts/login/')
def search_files(request):
    if request.method == 'GET':
        if 'file' in request.GET:
            file = request.GET['file']
            files = UploadedFile.objects.filter(image_title__icontains=file)
            return HttpResponse(files)
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
@login_required(login_url='/accounts/login/')
def uploadedfiles(request, pkb=None):
    data = dict()
    if (request.method == 'GET' or request.method == 'POST') and pkb:
        publication = Publication.objects.get(pk=pkb)
        data['table'] = render_to_string(
            '_uploadedfiles_table.html',
            {'publication': publication},
            request=request
        )
        return JsonResponse(data)

@login_required(login_url='/accounts/login/')
def authors(request, pkb=None):
    data = dict()
    #pdb.set_trace()
    if (request.method == 'GET' or request.method == 'POST') and pkb:
        publication = Publication.objects.get(pk=pkb)
        data['table'] = render_to_string(
            '_authors_table.html',
            {'publication': publication},
            request=request
        )
        return JsonResponse(data)

@login_required(login_url='/accounts/login/')
def translators(request, pkb=None):
    data = dict()
    if (request.method == 'GET' or request.method == 'POST') and pkb:
        publication = Publication.objects.get(pk=pkb)
        data['table'] = render_to_string(
            '_translators_table.html',
            {'publication': publication},
            request=request
        )
        return JsonResponse(data)

class UploadedFileCreateView(BSModalCreateView):
    template_name = 'uploadedfiles/uploadedfile_new.html'
    form_class = UploadedFileModelForm
    success_message = 'Success: uploadedfile was created.'
    #context_object_name = 'publication'
    #model = Publication
    success_url = reverse_lazy('publication-new')

    def get_context_data(self, **kwargs):
        context = super(UploadedFileCreateView, self).get_context_data(**kwargs)
        context['pkb'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        return HttpResponse(status=200)
    '''
    def get_success_url(self):
        return reverse_lazy('publication-new', kwargs={'active_tab': 'tab_files', 'object_id': self.object.id}, )
        #return render(self.request, 'publications/form_create.html', {'form': self.form_valid(None) ,'active_tab': 'tab_files', 'object_id': str(self.object.id)})
    '''
    '''
    def get_success_url(self):
        """Detect the submit button used and act accordingly"""
        if 'next' in self.request.POST:
            return '/publication/show/'
        elif 'save' in self.request.POST:
            return '/publication/' + str(self.object.id) + '/edit/'
        else: #self.request.path == 'uploadedfile_new/' or self.request.path == 'uploadedfile_unlink/<int:pk>':
            #pdb.set_trace()
            return reverse_lazy('/publication/' + str(self.object.id) + '/edit/')
    '''

        #return super().form_valid(form)

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
    context_object_name = 'publication'
    #success_url = '/publication/show/'

    def get_success_url(self):
        if self.request.POST.get("save_add_another"):
            return '/publication/new/'
        elif self.request.POST.get("save_and_continue_editing") :
            return '/publication/' + str(self.object.id) + '/edit/'
        elif self.request.POST.get("save"):
        #else:
            url = self.request.GET.get('next')
            if url == None:
                return '/publication/' + str(self.object.id) + '/edit/'
            if self.request.GET.get('q'):
                url += '?q=' + self.request.GET.get('q')
            if self.request.GET.get('page'):
                url += '&page=' + self.request.GET.get('page')
            if self.request.GET.get('order_by'):
                url += '&order_by=' + self.request.GET.get('order_by')
            if self.request.GET.get('direction'):
                url += '&direction=' + self.request.GET.get('direction')
            return url
        '''
        """Detect the submit button used and act accordingly"""
        if 'next' in self.request.POST:
            return '/publication/show/'
        elif 'save' in self.request.POST:
            return '/publication/' + str(self.object.id) + '/edit/'
        '''

    def form_valid(self, form):
        if form.is_valid():
            #self.object = form.save()
            self.object = form.save()
            self.object.save()
            #self.object = form.save(commit=False)
            #self.object.save()

        return redirect(self.get_success_url())
        #pdb.set_trace()
        '''
        red = self.get_success_url()
        if red:
         return redirect(red)
        else:
            return HttpResponse('')
        #pdb.set_trace()
        '''
@login_required(login_url='/accounts/login/')
def PublicationDelete(request, pk):
    '''
    Deletes a publication 
    argument pk int value of the id of the to be deleted publication
    redirect to main publication page (Show)
    '''
    publication = Publication.objects.get(id=pk)
    publication.is_deleted = True
    publication.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class PublicationCreate(UpdateView):
    '''
    inherits CreateView
    Uses template for creating/updating.
    Uses standard edit/new form (NewCrispyForm)
    redirect to publication main page (publication show)
    '''
    template_name = 'publications/form_create.html'
    form_class = NewCrispyForm
    context_object_name = 'publication'
    model = Publication
    #fields = ['UploadedFiles']
    # success_url = '/publication/show/'
    '''
    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )

            return model_forms.modelform_factory(model, fields=self.fields)
    '''
    '''
    def get_context_data(self, **kwargs):
        context = super(PublicationCreate, self).get_context_data(**kwargs)
        try:
            if context['files'] and context['files'].count() < 1:
                context['files'] = UploadedFile.objects.filter(pk=self.kwargs['object_id'])
            else:
                context['files'] |= UploadedFile.objects.filter(pk=self.kwargs['object_id'])
        except:
            traceback.print_exc()
            #context['files_list'] = chain(context['files_list'],context['files'].append(UploadedFile.objects.filter(pk=self.kwargs['pk'])))
        return context
    '''
    '''
    def get_context_data(self, **kwargs):
        context = super(PublicationCreate, self).get_context_data(**kwargs)
        context['publication'] = Publication(is_stub=True)
        return context
    '''
    #def get_success_url(self):
    #    return

    def get_object(self):
        '''
        pubs = Publication.objects.filter(Q(created_by = self.request.user) and Q(is_stub=True) and Q(is_deleted=False))
        pk = 0
        if pubs:
            for pub in pubs:
                if pub.pk > pk:
                    pk = pub.pk
                    publication = pub
            return publication
        else:
        '''
        pub = Publication.objects.create(is_stub=True, created_by=self.request.user)
        pub.save()
        return pub

    def form_valid(self, form):
        # todo: temporal solution for double publication.
        pk = 0
        for pub in Publication.objects.all():
            if pub.is_stub is True and pub.is_deleted is False and pub.created_by == self.request.user and pub.pk > pk\
                    and pub.pk != form.instance.pk:
                pk = pub.pk
        form.instance.created_by = self.request.user
        form.instance.is_stub = False
        pub = Publication.objects.get(pk=pk)
        form.instance.authors.add(*pub.authors.all())
        form.instance.uploadedfiles.add(*pub.uploadedfiles.all())
        form.instance.translators.add(*pub.translators.all())
        if form.is_valid():
            self.object = form.save()
            self.object.save()

        pub.is_deleted = True
        #pdb.set_trace()
        return redirect(self.get_success_url())

    def get_success_url(self):
        """Detect the submit button used and act accordingly"""
        '''
        if 'next' in self.request.POST:
            return '/publication/show/'
        elif 'save' in self.request.POST:
            return '/publication/' + str(self.object.id) + '/edit/'
        elif self.request.path == 'uploadedfile_new/' or self.request.path == 'uploadedfile_unlink/<int:pk>':
            return '/publication/' + str(self.object.id) + '/edit/'
        '''
        if self.request.POST.get("save_add_another"):
            return '/publication/new/'
        elif self.request.POST.get("save_and_continue_editing") :
            return '/publication/' + str(self.object.id) + '/edit/'
        elif self.request.POST.get("save"):
            url = self.request.GET.get('next')
            if url == None:
                return '/publication/' + str(self.object.id) + '/edit/'
            if self.request.GET.get('q'):
                url += '?q=' + self.request.GET.get('q')
            if self.request.GET.get('page'):
                url += '&page=' + self.request.GET.get('page')
            if self.request.GET.get('order_by'):
                url += '&order_by=' + self.request.GET.get('order_by')
            if self.request.GET.get('direction'):
                url += '&direction=' + self.request.GET.get('direction')
            return url

class PublicationDetailView(DetailView):
    '''
    Inherits DetailView
    Detailview for publication
    Usess now in template thus the function get_context_data
    '''
    model = Publication

    def get_queryset(self):
        publications = Publication.objects.filter(is_deleted=False, is_stub=False)
        return publications

    def get_context_data(self, **kwargs):
        self.object = []
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class PublicationDetailViewNew(DetailView):
    '''
    Inherits DetailView
    Detailview for publication
    Usess now in template thus the function get_context_data
    '''
    model = Publication
    template_name = 'publications/new_detail.html'

    def get_queryset(self):
        publications = Publication.objects.filter(is_deleted=False, is_stub=False)
        return publications

    def get_context_data(self, **kwargs):
        self.object = []
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        cover_image = ''
        context['publication'] = Publication.objects.filter(pk=self.kwargs['pk'])[0]
        min = 9
        for uploadedfile in context['publication'].uploadedfiles.all():
            if uploadedfile.filecategory and uploadedfile.filecategory.list_view_priority:
                compare = int(uploadedfile.filecategory.list_view_priority)
                if compare < min:
                    min = compare
                    cover_image = uploadedfile.file

        date = datetime.datetime.now()
        date = date.replace(tzinfo=utc)

        for uploadedfile in context['publication'].uploadedfiles.all():

            list_view_priority = 9

            try:
                list_view_priority = uploadedfile.filecategory.list_view_priority
            except AttributeError:
                pass

            if uploadedfile.uploaded_at and uploadedfile.uploaded_at < date and uploadedfile.file and \
                    list_view_priority == min:
                try:
                    im = Image.open(uploadedfile.file)
                    date = uploadedfile.uploaded_at
                    cover_image = uploadedfile.file
                except IOError:
                    continue

        context['cover_image'] = cover_image
        context['cover_image_small'] = cover_image # set the backup, then try to find a smaller one

        if cover_image is not None:

            for extension in ['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG']:

                if not cover_image.path.endswith(extension):
                    continue

                small_image_path = cover_image.path.replace('.'+extension, '_small.'+extension)

                if isfile(small_image_path):
                    context['cover_image_small'] = cover_image.name.replace('.'+extension, '_small.'+extension)
                    break

        context['request'] = self.request

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

def export_xlsx_file(request, queryset):
    '''
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=export.csv'

    opts = queryset.model._meta
    field_names = [field.name for field in opts.fields]

    writer = csv.writer(response, delimiter='\t')
    # write a first row with header information
    writer.writerow(field_names)

    # write data rows
    # I suggest you to check what output of `queryset`
    # because your `queryset` using `cursor.fetchall()`
    # print(queryset)
    for pub in queryset:
        fields = []
        for field_name in field_names:
            fields.append(getattr(pub, field_name))
        writer.writerow(fields)
    return response
    '''
    '''
    workbook = Workbook()
    worksheet = workbook.active

    response = HttpResponse(content=save_virtual_workbook(workbook),
                            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=myexport.xlsx'
    return response
    '''
    return ExcelResponse(queryset)

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
    publications = Publication.objects.filter(is_deleted=False, is_stub=False)
    paginate_by = 10
    #ordering = 'title'

    '''
    def get_success_url(self):
        url = self.request.GET.get('')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        if self.request.GET.get('q'):
            url += '&q' + self.request.GET.get('q')
        return url
    '''

    def get_template_names(self):
        if self.request.path == 'uploadedfile_new/' or self.request.path == 'uploadedfile_unlink/<int:pk>':
            return ['publications/form_create.html']
        return ['publications/show.html']

    def post(self, request, *args, **kwargs):
        return export_xlsx_file(request, self.get_queryset())
        #q = request.POST.get('q')
        #pubs= self.get_queryset()
        #return render(request, self.template_name, {'publications': pubs, 'q': q})

    def get_ordering(self):
        #pdb.set_trace()
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_queryset(self):

            #pub.save()
        #form = PublicationForm(self.request.GET)
        authors = self.request.GET.getlist('authors')
        translators = self.request.GET.getlist('translators')
       #pdb.set_trace()
        if not authors == ['']:
            authors = Author.objects.filter(pk__in=authors).all()
        if not translators == ['']:
            translators = Translator.objects.filter(pk__in=translators).all()
        form_of_publications = self.request.GET.getlist('form_of_publication')
        if not form_of_publications == ['']:
            form_of_publications = FormOfPublication.objects.filter(pk__in=form_of_publications).all()
        languages = self.request.GET.getlist('language')
        if not languages == ['']:
            languages = Language.objects.filter(pk__in=languages).all()
        affiliated_churches = self.request.GET.getlist('affiliated_church')
        if not affiliated_churches == ['']:
            affiliated_churches = Church.objects.filter(pk__in=affiliated_churches).all()
        content_genres = self.request.GET.getlist('content_genre')
        if not content_genres == ['']:
            content_genres = Genre.objects.filter(pk__in=content_genres).all()
        connected_to_special_occasions = self.request.GET.getlist('connected_to_special_occasion')
        if not connected_to_special_occasions == ['']:
            connected_to_special_occasions = SpecialOccasion.objects.filter(pk__in=connected_to_special_occasions).all()
        currently_owned_by = self.request.GET.getlist('currently_owned_by')
        if not currently_owned_by == ['']:
            currently_owned_by = Owner.objects.filter(pk__in=currently_owned_by).all()
        copyrights = self.request.GET.get('copyrights')
        is_a_translation = self.request.GET.get('is_a_translation')

        publications = Publication.objects.filter(is_deleted=False, is_stub=False)

        #publications = Publication.objects.filter(is_deleted=False).values('id').distinct()
        #publications = publications.filter(is_deleted=False)
        uploadedfiles = self.request.GET.getlist('uploadedfiles')
        #files = UploadedFile.objects.filter(is_deleted=False)
        #uploadedfiles = files.filter(pk__in=uploadedfiles).all()
        if not uploadedfiles == ['']:
            uploadedfiles = UploadedFile.objects.filter(pk__in=uploadedfiles).all()
        keywords = self.request.GET.getlist('keywords')
        if not keywords == ['']:
            keywords = Keyword.objects.filter(pk__in=keywords).all()
        translated_from = self.request.GET.getlist('translated_From')
        if not translated_from == ['']:
            translated_from = Language.objects.filter(pk__in=translated_from).all()
        city = self.request.GET.getlist('publication_city')
        country = self.request.GET.getlist('publication_country')
        collection_country = self.request.GET.getlist('collection_country')
        filecategory = self.request.GET.getlist('filecategory')
        if not filecategory == ['']:
            filecategory = FileCategory.objects.filter(pk__in=filecategory).all()

        if list(collection_country) != ['']:
            collection_country = Country.objects.filter(pk__in=city).all()

        if list(country) != ['']:
            country = Country.objects.filter(pk__in=country).all()

        print('....', city)
        if list(city) != ['']:
            city = City.objects.filter(pk__in=city).all()

        print(publications)

        search_title = self.request.GET.get('search_title')
        search_title_translation = self.request.GET.get('search_title_translation')
        search_author = self.request.GET.get('search_author')
        search_keywords = self.request.GET.get('search_keywords')
        search_image_content = self.request.GET.get('search_image_content')
        search_description = self.request.GET.get('search_description')


        exclude = ['csrfmiddlewaretoken','search', 'order_by', 'direction']
        in_variables = [('authors', authors), ('translators', translators), ('form_of_publication', form_of_publications), ('language',languages), ('affiliated_church', affiliated_churches) \
        , ('content_genre', content_genres), ('connected_to_special_occasion', connected_to_special_occasions), ('currently_owned_by', currently_owned_by),\
        ('uploadedfiles', uploadedfiles), ('publication_country', country), ('publication_city', city), ('collection_country', collection_country), \
        ('keywords', keywords), ('translated_from',translated_from), ('uploadedfiles__filecategory', filecategory),
                    ]
        special_case = ['copyrights', 'page', 'is_a_translation', 'filecategory']

        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            if query_string.lower() in countries_dict.keys():
                query_string = countries_dict[query_string.lower()]

            search_fields = []

            if((search_title == 'true' and search_title_translation == 'true' and search_author == 'true' and search_keywords == 'true' and \
                    search_image_content == 'true' and search_description == 'true') or (search_title == 'false' and search_title_translation == 'false' and \
                    search_author == 'false' and search_keywords == 'false' and search_image_content == 'false' and \
                    search_description == 'false') or (not search_title and not search_title_translation and not search_author and not search_keywords and \
                    not search_image_content and not search_description)):
                search_fields = ['title', 'title_subtitle_transcription', 'title_translation', 'authors__name', 'authors__name_original_language', 'authors__extra_info', \
                      'form_of_publication__name', 'editor', 'printed_by', 'published_by', 'publication_year', 'publication_country__name', 'publication_city__name', 'publishing_organisation', 'translators__name', 'translators__name_original_language', 'translators__extra_info', \
                      'language__name', 'language__direction', 'affiliated_church__name', 'extra_info', 'content_genre__name', 'connected_to_special_occasion__name', 'donor', 'content_description', 'description_of_illustration', \
                      'nr_of_pages', 'uploadedfiles__filecategory__name', 'uploadedfiles__uploaded_at', 'uploadedfiles__image_contents', \
                      'uploadedfiles__image_title', 'general_comments', 'team_comments', 'keywords__name', 'is_a_translation', 'ISBN_number', 'translated_from__name', 'translated_from__direction', \
                      'title2', 'title_subtitle_transcription2', 'title_translation2', 'title3', 'title_subtitle_transcription3', 'title_translation3', \
                      'title4', 'title_subtitle_transcription4', 'title_translation4', 'title5', 'title_subtitle_transcription5', 'title_translation5', \
                      'currency', 'price', 'collection_context']

            else:
                if search_title == 'true':
                    search_fields.extend(['title'])
                if search_title_translation == 'true':
                    search_fields.extend(['title_translation'])
                if search_author == 'true':
                    search_fields.extend(['authors__name', 'authors__name_original_language', 'authors__extra_info'])
                if search_keywords == 'true':
                    search_fields.extend(['keywords__name'])
                if search_image_content == 'true':
                    search_fields.extend(['uploadedfiles__image_contents'])
                if search_description == 'true':
                    search_fields.extend(['content_description'])

            if self.request.user.is_authenticated:
                search_fields.extend(['collection_date', 'collection_country__name', 'collection_venue_and_city', 'contact_telephone_number', 'contact_email', 'contact_website', 'currently_owned_by__name'])

            print(query_string)
            #arabic_query = translator.translate(query_string, dest='ar').text
            query_string = to_searchable(query_string)

            #arabic_query = to_searchable(arabic_query)
            entry_query = get_query(query_string, search_fields)
            #publications

            #arabic_query = get_query(arabic_query, search_fields)
            print('&&&&&&', query_string)
            #publications = publications.filter(entry_query)
            #pdb.set_trace()
            #publications = publications.filter(Q(entry_query) | Q(arabic_query))
            publications = publications.filter(Q(entry_query))

            #for (idx, apin) in enumerate(appears_in):
            '''
            print(publications)
            ordering = self.get_ordering()
            if ordering is not None and ordering != "":
                publications = publications.order_by(ordering)
            publications = publications.distinct()

            #pdb.set_trace()

            #context['publications'] = publications
            return publications
            '''
        for field_name in self.request.GET:
            if field_name == 'q' or field_name.startswith('search_') or field_name == 'page_name':
                continue
            get_value = self.request.GET.get(field_name)
            if get_value != "" and not field_name in exclude and not field_name in [i[0] for i in in_variables] and\
               not field_name in special_case:
                print('******', field_name)
                #arabic_query = translator.translate(get_value, dest='ar').text
                get_value = to_searchable(get_value)
                get_value = get_query(get_value, [field_name])
                #arabic_query = get_query(arabic_query, [field_name])
                print('444444444', get_value)
                publications.filter(Q(get_value))
                #publications = publications.filter(Q(get_value) | Q(arabic_query))
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
        elif self.request.path == '/publication/show/' or self.request.path == '/':
            publications = publications.order_by('-date_created')

        publications = publications.distinct()
        return publications

    def make_human_friendly(self, field):
        return field.replace("_", " ")

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        #pdb.set_trace()
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
        affiliated_church = self.request.GET.get('affiliated_church')
        if affiliated_church is not None and affiliated_church != "":
            context['affiliated_church'] = affiliated_church
        else:
            context['affiliated_church'] = ''
        authors = self.request.GET.get('authors')
        if authors is not None and authors != "":
            context['authors'] = authors
        else:
            context['authors'] = ''
        translators = self.request.GET.get('translators')
        if translators is not None and translators != "":
            context['translators'] = translators
        else:
            context['translators'] = ''
        form_of_publication = self.request.GET.get('form_of_publication')
        if form_of_publication is not None and form_of_publication != "":
            context['form_of_publication'] = form_of_publication
        else:
            context['form_of_publication'] = ''
        publication_city = self.request.GET.get('publication_city')
        if publication_city is not None and publication_city != "":
            context['publication_city'] = publication_city
        else:
            context['publication_city'] = ''
        language = self.request.GET.get('language')
        if language is not None and language != "":
            context['language'] = language
        else:
            context['language'] = ''
        content_genre = self.request.GET.get('content_genre')
        if content_genre is not None and content_genre != "":
            context['content_genre'] = content_genre
        else:
            context['content_genre'] = ''
        connected_to_special_occasion = self.request.GET.get('connected_to_special_occasion')
        if connected_to_special_occasion is not None and connected_to_special_occasion != "":
            context['connected_to_special_occasion'] = connected_to_special_occasion
        else:
            context['connected_to_special_occasion'] = ''
        currently_owned_by = self.request.GET.get('currently_owned_by')
        if currently_owned_by is not None and currently_owned_by != "":
            context['currently_owned_by'] = currently_owned_by
        else:
            context['currently_owned_by'] = ''
        keywords = self.request.GET.get('keywords')
        if keywords is not None and keywords != "":
            context['keywords'] = keywords
        else:
            context['keywords'] = ''
        uploadedfiles = self.request.GET.get('uploadedfiles')
        if uploadedfiles is not None and uploadedfiles != "":
            context['uploadedfiles'] = uploadedfiles
        else:
            context['uploadedfiles'] = ''
        filecategory = self.request.GET.get('filecategory')
        if filecategory is not None and filecategory != "":
            context['filecategory'] = filecategory
        else:
            context['filecategory'] = ''
        search_title = self.request.GET.get('search_title')
        if search_title is not None and search_title != "":
            context['search_title'] = search_title
        else:
            context['search_title'] = ''
        search_title_translation = self.request.GET.get('search_title_translation')
        if search_title_translation is not None and search_title_translation != "":
            context['search_title_translation'] = search_title_translation
        else:
            context['search_title_translation'] = ''
        search_author = self.request.GET.get('search_author')
        if search_author is not None and search_author != "":
            context['search_author'] = search_author
        else:
            context['search_author'] = ''
        search_keywords = self.request.GET.get('search_keywords')
        if search_keywords is not None and search_keywords != "":
            context['search_keywords'] = search_keywords
        else:
            context['search_keywords'] = ''
        search_image_content = self.request.GET.get('search_image_content')
        if search_image_content is not None and search_image_content != "":
            context['search_image_content'] = search_image_content
        else:
            context['search_image_content'] = ''
        search_description = self.request.GET.get('search_description')
        if search_description is not None and search_description != "":
            context['search_description'] = search_description
        else:
            context['search_description'] = ''

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
        context['cover_images'] = cover_images
        context['request'] = self.request
        regexp = re.compile(context['q'], re.IGNORECASE)
        search_term_appear_in = []
        index = 0
        for pub in context['publications']:
            search_term_appear_in.append('')
            if q == None or q == '':
                continue
            for field in Publication._meta.get_fields():
                if Publication._meta.get_field(field.name).get_internal_type() == 'ManyToManyField' or \
                        Publication._meta.get_field(field.name).get_internal_type() == 'ForeignKey':
                    if field.name == 'authors':
                        for author in pub.authors.all():
                            for author_field in Author._meta.get_fields():
                                if author_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(author, author_field.name), str) \
                                        and not isinstance(getattr(author, author_field.name), int):
                                    continue
                                if regexp.search(str(getattr(author, author_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'author ' + self.make_human_friendly(author_field.name)
                                    elif not ('author ' + self.make_human_friendly(author_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', author ' + self.make_human_friendly(author_field.name)
                    elif field.name == 'translators':
                        for translator in pub.translators.all():
                            for translator_field in Translator._meta.get_fields():
                                if translator_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(translator, translator_field.name), str) \
                                        and not isinstance(getattr(translator, translator_field.name), int):
                                    continue
                                if regexp.search(str(getattr(translator, translator_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'translator '+ self.make_human_friendly(translator_field.name)
                                    elif not ('translator ' + self.make_human_friendly(translator_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', translator ' + self.make_human_friendly(translator_field.name)
                    elif field.name == 'publication_city' and pub.publication_city:
                        if not isinstance(pub.publication_city.name, str) \
                                and not isinstance(pub.publication_city.name, int):
                            continue
                        if regexp.search(str(pub.publication_city.name)):
                            if search_term_appear_in[index] == '':
                                search_term_appear_in[index] = 'publication city name'
                            elif not ('publication city name' in search_term_appear_in[index]):
                                search_term_appear_in[index] = search_term_appear_in[index] + ', ' + 'publication city name'
                    elif field.name == 'publication_country' and pub.publication_country:
                        if not isinstance(pub.publication_country.name, str) \
                                and not isinstance(pub.publication_country.name, int):
                            continue
                        if regexp.search(str(pub.publication_country.name)):
                            if search_term_appear_in[index] == '':
                                search_term_appear_in[index] = 'publication country name'
                            elif not ('publication country name' in search_term_appear_in[index]):
                                search_term_appear_in[index] = search_term_appear_in[index] + ', ' + 'publication country name'
                    elif field.name == 'form_of_publication':
                        for form_of_publication in pub.form_of_publication.all():
                            for form_of_publication_field in FormOfPublication._meta.get_fields():
                                if form_of_publication_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(form_of_publication, form_of_publication_field.name), str) \
                                        and not isinstance(getattr(form_of_publication, form_of_publication_field.name),
                                                           int):
                                    continue
                                if regexp.search(str(getattr(form_of_publication, form_of_publication_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'form of publication ' + self.make_human_friendly(form_of_publication_field.name)
                                    elif not ('form of publication' + self.make_human_friendly(form_of_publication_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', form of publication ' + self.make_human_friendly(form_of_publication_field.name)
                    elif field.name == 'affiliated_church':
                        for affiliated_church in pub.affiliated_church.all():
                            for affiliated_church_field in Church._meta.get_fields():
                                if affiliated_church_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(affiliated_church, affiliated_church_field.name), str) \
                                        and not isinstance(getattr(affiliated_church, affiliated_church_field.name),
                                                           int):
                                    continue
                                if regexp.search(str(getattr(affiliated_church, affiliated_church_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'affiliated church ' + self.make_human_friendly(affiliated_church_field.name)
                                    elif not ('affiliated church ' + self.make_human_friendly(affiliated_church_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', affiliated church ' + self.make_human_friendly(affiliated_church_field.name)
                    elif field.name == 'language':
                        for language in pub.language.all():
                            for language_field in Language._meta.get_fields():
                                if language_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(language, language_field.name), str) \
                                        and not isinstance(getattr(language, language_field.name), int):
                                    continue
                                if regexp.search(str(getattr(language, language_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'language '+ self.make_human_friendly(language_field.name)
                                    elif not ('language ' + self.make_human_friendly(language_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', language ' + self.make_human_friendly(language_field.name)
                    elif field.name == 'translated_from' and pub.translated_from:
                        for translated_from_field in Language._meta.get_fields():
                            if translated_from_field.name == 'publication':
                                continue
                            if not isinstance(getattr(pub.translated_from, translated_from_field.name), str) \
                                    and not isinstance(getattr(pub.translated_from, translated_from_field.name), int):
                                continue
                            if regexp.search(str(getattr(pub.translated_from, translated_from_field.name))):
                                if search_term_appear_in[index] == '':
                                    search_term_appear_in[index] = 'translated from '+ self.make_human_friendly(translated_from_field.name)
                                elif not ('translated from ' + self.make_human_friendly(translated_from_field.name) in search_term_appear_in[index]):
                                    search_term_appear_in[index] = search_term_appear_in[
                                                                       index] + ', translated from ' + self.make_human_friendly(translated_from_field.name)
                    elif field.name == 'content_genre':
                        for genre in pub.content_genre.all():
                            for content_genre_field in Genre._meta.get_fields():
                                if content_genre_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(genre, content_genre_field.name), str) \
                                        and not isinstance(getattr(genre, content_genre_field.name), int):
                                    continue
                                if regexp.search(str(getattr(genre, content_genre_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'content genre '+ self.make_human_friendly(content_genre_field.name)
                                    elif not ('content genre '+ self.make_human_friendly(content_genre_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', content genre ' + self.make_human_friendly(content_genre_field.name)
                    elif field.name == 'connected_to_special_occasion':
                        for special_occasion in pub.connected_to_special_occasion.all():
                            for special_occasion_field in SpecialOccasion._meta.get_fields():
                                if special_occasion_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(special_occasion, special_occasion_field.name), str) \
                                        and not isinstance(getattr(special_occasion, special_occasion_field.name), int):
                                    continue
                                if regexp.search(str(getattr(special_occasion, special_occasion_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'special_occasion '+ self.make_human_friendly(special_occasion_field.name)
                                    elif not ('special_occasion '+ self.make_human_friendly(special_occasion_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', special_occasion ' + self.make_human_friendly(special_occasion_field.name)
                    elif field.name == 'collection_country' and pub.collection_country:
                        if not isinstance(pub.collection_country.name, str) \
                                and not isinstance(pub.collection_country.name, int):
                            continue
                        if regexp.search(str(pub.collection_country.name)):
                            if search_term_appear_in[index] == '':
                                search_term_appear_in[index] = 'collection country name'
                            elif not ('collection country name' in search_term_appear_in[index]):
                                search_term_appear_in[index] = search_term_appear_in[
                                                                   index] + ', ' + 'collection country name'
                    elif field.name == 'currently_owned_by':
                        for currently_owned_by in pub.currently_owned_by.all():
                            for currently_owned_by_field in Owner._meta.get_fields():
                                if currently_owned_by_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(currently_owned_by, currently_owned_by_field.name), str) \
                                        and not isinstance(getattr(currently_owned_by, currently_owned_by_field.name),
                                                           int):
                                    continue
                                if regexp.search(str(getattr(currently_owned_by, currently_owned_by_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'currently_owned_by_field '+ self.make_human_friendly(currently_owned_by_field.name)
                                    elif not ('currently_owned_by_field '+ self.make_human_friendly(currently_owned_by_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', currently_owned_by_field ' + self.make_human_friendly(currently_owned_by_field.name)
                    elif field.name == 'keywords':
                        for keyword in pub.keywords.all():
                            for keyword_field in Keyword._meta.get_fields():
                                if keyword_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(keyword, keyword_field.name), str) \
                                        and not isinstance(getattr(keyword, keyword_field.name), int):
                                    continue
                                if regexp.search(str(getattr(keyword, keyword_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'keyword '+ self.make_human_friendly(keyword_field.name)
                                    elif not ('keyword '+ self.make_human_friendly(keyword_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', keyword ' + self.make_human_friendly(keyword_field.name)
                    elif field.name == 'uploadedfiles':
                        for uploadedfile in pub.uploadedfiles.all():
                            for uploadedfile_field in UploadedFile._meta.get_fields():
                                if uploadedfile_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(uploadedfile, uploadedfile_field.name), str) \
                                        and not isinstance(getattr(uploadedfile, uploadedfile_field.name), int):
                                    continue
                                if regexp.search(str(getattr(uploadedfile, uploadedfile_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'uploadedfile '+ self.make_human_friendly(uploadedfile_field.name)
                                    elif not ('uploadedfile '+ self.make_human_friendly(uploadedfile_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', uploadedfile ' + self.make_human_friendly(uploadedfile_field.name)
                    elif field.name == 'created_by':
                        user_fields = ['username', 'first_name', 'last_name']
                        for created_by_field in user_fields:
                            if not pub.created_by or not isinstance(getattr(pub.created_by, created_by_field), str) \
                                    and not isinstance(getattr(pub.created_by, created_by_field), int):
                                continue
                            if regexp.search(str(getattr(pub.created_by, created_by_field))):
                                if search_term_appear_in[index] == '':
                                    search_term_appear_in[index] = 'created_by '+ created_by_field
                                elif not ('created_by '+created_by_field in search_term_appear_in[index]):
                                    search_term_appear_in[index] = search_term_appear_in[
                                                                       index] + ', created_by ' + created_by_field
                if not isinstance(getattr(pub, field.name), str) and not isinstance(getattr(pub, field.name), int):
                    continue
                elif regexp.search(str(getattr(pub, field.name))):
                    if search_term_appear_in[index] == '':
                        search_term_appear_in[index] = self.make_human_friendly(field.name)
                    elif not (field.name in search_term_appear_in[index]):
                        search_term_appear_in[index] = search_term_appear_in[index] + ', ' + self.make_human_friendly(field.name)
            index += 1
        context['search_term_appear_in'] = search_term_appear_in
        #pdb.set_trace()
        context['zipped_data'] = zip(context['publications'], context['cover_images'], context['search_term_appear_in'])
        context['count'] = self.get_queryset().count()

        return context

class SearchResultsViewImages(ListView):
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
    publications = Publication.objects.filter(is_deleted=False, is_stub=False)
    #ordering = 'title'

    '''
    def get_success_url(self):
        url = self.request.GET.get('')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        if self.request.GET.get('q'):
            url += '&q' + self.request.GET.get('q')
        return url
    '''

    def get_template_names(self):
        if self.request.path == 'uploadedfile_new/' or self.request.path == 'uploadedfile_unlink/<int:pk>':
            return ['publications/form_create.html']
        return ['publications/images.html']

    def post(self, request, *args, **kwargs):
        return export_xlsx_file(request, self.get_queryset())
        #q = request.POST.get('q')
        #pubs= self.get_queryset()
        #return render(request, self.template_name, {'publications': pubs, 'q': q})

    def get_ordering(self):
        #pdb.set_trace()
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_queryset(self):

            #pub.save()
        #form = PublicationForm(self.request.GET)
        authors = self.request.GET.getlist('authors')
        translators = self.request.GET.getlist('translators')
       #pdb.set_trace()
        if not authors == ['']:
            authors = Author.objects.filter(pk__in=authors).all()
        if not translators == ['']:
            translators = Translator.objects.filter(pk__in=translators).all()
        form_of_publications = self.request.GET.getlist('form_of_publication')
        if not form_of_publications == ['']:
            form_of_publications = FormOfPublication.objects.filter(pk__in=form_of_publications).all()
        languages = self.request.GET.getlist('language')
        if not languages == ['']:
            languages = Language.objects.filter(pk__in=languages).all()
        affiliated_churches = self.request.GET.getlist('affiliated_church')
        if not affiliated_churches == ['']:
            affiliated_churches = Church.objects.filter(pk__in=affiliated_churches).all()
        content_genres = self.request.GET.getlist('content_genre')
        if not content_genres == ['']:
            content_genres = Genre.objects.filter(pk__in=content_genres).all()
        connected_to_special_occasions = self.request.GET.getlist('connected_to_special_occasion')
        if not connected_to_special_occasions == ['']:
            connected_to_special_occasions = SpecialOccasion.objects.filter(pk__in=connected_to_special_occasions).all()
        currently_owned_by = self.request.GET.getlist('currently_owned_by')
        if not currently_owned_by == ['']:
            currently_owned_by = Owner.objects.filter(pk__in=currently_owned_by).all()
        copyrights = self.request.GET.get('copyrights')
        is_a_translation = self.request.GET.get('is_a_translation')

        publications = Publication.objects.filter(is_deleted=False, is_stub=False)

        #publications = Publication.objects.filter(is_deleted=False).values('id').distinct()
        #publications = publications.filter(is_deleted=False)
        uploadedfiles = self.request.GET.getlist('uploadedfiles')
        #files = UploadedFile.objects.filter(is_deleted=False)
        #uploadedfiles = files.filter(pk__in=uploadedfiles).all()
        if not uploadedfiles == ['']:
            uploadedfiles = UploadedFile.objects.filter(pk__in=uploadedfiles).all()
        keywords = self.request.GET.getlist('keywords')
        if not keywords == ['']:
            keywords = Keyword.objects.filter(pk__in=keywords).all()
        translated_from = self.request.GET.getlist('translated_From')
        if not translated_from == ['']:
            translated_from = Language.objects.filter(pk__in=translated_from).all()
        city = self.request.GET.getlist('publication_city')
        country = self.request.GET.getlist('publication_country')
        collection_country = self.request.GET.getlist('collection_country')
        filecategory = self.request.GET.getlist('filecategory')
        if not filecategory == ['']:
            filecategory = FileCategory.objects.filter(pk__in=filecategory).all()

        if list(collection_country) != ['']:
            collection_country = Country.objects.filter(pk__in=city).all()

        if list(country) != ['']:
            country = Country.objects.filter(pk__in=country).all()

        print('....', city)
        if list(city) != ['']:
            city = City.objects.filter(pk__in=city).all()

        print(publications)

        search_title = self.request.GET.get('search_title')
        search_title_translation = self.request.GET.get('search_title_translation')
        search_author = self.request.GET.get('search_author')
        search_keywords = self.request.GET.get('search_keywords')
        search_image_content = self.request.GET.get('search_image_content')
        search_description = self.request.GET.get('search_description')


        exclude = ['csrfmiddlewaretoken','search', 'order_by', 'direction']
        in_variables = [('authors', authors), ('translators', translators), ('form_of_publication', form_of_publications), ('language',languages), ('affiliated_church', affiliated_churches) \
        , ('content_genre', content_genres), ('connected_to_special_occasion', connected_to_special_occasions), ('currently_owned_by', currently_owned_by),\
        ('uploadedfiles', uploadedfiles), ('publication_country', country), ('publication_city', city), ('collection_country', collection_country), \
        ('keywords', keywords), ('translated_from',translated_from), ('uploadedfiles__filecategory', filecategory),
                    ]
        special_case = ['copyrights', 'page', 'is_a_translation', 'filecategory']

        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            if query_string.lower() in countries_dict.keys():
                query_string = countries_dict[query_string.lower()]

            search_fields = []

            if((search_title == 'true' and search_title_translation == 'true' and search_author == 'true' and search_keywords == 'true' and \
                    search_image_content == 'true' and search_description == 'true') or (search_title == 'false' and search_title_translation == 'false' and \
                    search_author == 'false' and search_keywords == 'false' and search_image_content == 'false' and \
                    search_description == 'false') or (not search_title and not search_title_translation and not search_author and not search_keywords and \
                    not search_image_content and not search_description)):
                search_fields = ['title', 'title_subtitle_transcription', 'title_translation', 'authors__name', 'authors__name_original_language', 'authors__extra_info', \
                      'form_of_publication__name', 'editor', 'printed_by', 'published_by', 'publication_year', 'publication_country__name', 'publication_city__name', 'publishing_organisation', 'translators__name', 'translators__name_original_language', 'translators__extra_info', \
                      'language__name', 'language__direction', 'affiliated_church__name', 'extra_info', 'content_genre__name', 'connected_to_special_occasion__name', 'donor', 'content_description', 'description_of_illustration', \
                      'nr_of_pages', 'uploadedfiles__filecategory__name', 'uploadedfiles__uploaded_at', 'uploadedfiles__image_contents', \
                      'uploadedfiles__image_title', 'general_comments', 'team_comments', 'keywords__name', 'is_a_translation', 'ISBN_number', 'translated_from__name', 'translated_from__direction', \
                      'title2', 'title_subtitle_transcription2', 'title_translation2', 'title3', 'title_subtitle_transcription3', 'title_translation3', \
                      'title4', 'title_subtitle_transcription4', 'title_translation4', 'title5', 'title_subtitle_transcription5', 'title_translation5', \
                      'currency', 'price', 'collection_context']

            else:
                if search_title == 'true':
                    search_fields.extend(['title'])
                if search_title_translation == 'true':
                    search_fields.extend(['title_translation'])
                if search_author == 'true':
                    search_fields.extend(['authors__name', 'authors__name_original_language', 'authors__extra_info'])
                if search_keywords == 'true':
                    search_fields.extend(['keywords__name'])
                if search_image_content == 'true':
                    search_fields.extend(['uploadedfiles__image_contents'])
                if search_description == 'true':
                    search_fields.extend(['content_description'])

            if self.request.user.is_authenticated:
                search_fields.extend(['collection_date', 'collection_country__name', 'collection_venue_and_city', 'contact_telephone_number', 'contact_email', 'contact_website', 'currently_owned_by__name'])

            print(query_string)
            #arabic_query = translator.translate(query_string, dest='ar').text
            query_string = to_searchable(query_string)

            #arabic_query = to_searchable(arabic_query)
            entry_query = get_query(query_string, search_fields)
            #publications

            #arabic_query = get_query(arabic_query, search_fields)
            print('&&&&&&', query_string)
            #publications = publications.filter(entry_query)
            #pdb.set_trace()
            #publications = publications.filter(Q(entry_query) | Q(arabic_query))
            publications = publications.filter(Q(entry_query))
            #for (idx, apin) in enumerate(appears_in):

            '''
            print(publications)
            ordering = self.get_ordering()
            if ordering is not None and ordering != "":
                publications = publications.order_by(ordering)
            publications = publications.distinct()

            #pdb.set_trace()

            #context['publications'] = publications
            return publications
            '''
        for field_name in self.request.GET:
            if field_name == 'q' or field_name.startswith('search_') or field_name == 'page_name':
                continue
            get_value = self.request.GET.get(field_name)
            if get_value != "" and not field_name in exclude and not field_name in [i[0] for i in in_variables] and\
               not field_name in special_case:
                print('******', field_name)
                #arabic_query = translator.translate(get_value, dest='ar').text
                get_value = to_searchable(get_value)
                get_value = get_query(get_value, [field_name])
                #arabic_query = get_query(arabic_query, [field_name])
                print('444444444', get_value)
                publications.filter(Q(get_value))
                #publications = publications.filter(Q(get_value) | Q(arabic_query))
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
            publications = publications.filter(copyrights=val)

        if str(is_a_translation) != "unknown" and str(is_a_translation) != "None":
            val = False
            if str(is_a_translation) == "yes":
                val = True
            publications = publications.filter(is_a_translation=val)

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
        elif self.request.path == '/publication/show/' or self.request.path == '/':
            publications = publications.order_by('-date_created')

        publications = publications.distinct()
        return publications

    def make_human_friendly(self, field):
        return field.replace("_", " ")

    def get_context_data(self, **kwargs):
        context = super(SearchResultsViewImages, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        #pdb.set_trace()
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
        affiliated_church = self.request.GET.get('affiliated_church')
        if affiliated_church is not None and affiliated_church != "":
            context['affiliated_church'] = affiliated_church
        else:
            context['affiliated_church'] = ''
        authors = self.request.GET.get('authors')
        if authors is not None and authors != "":
            context['authors'] = authors
        else:
            context['authors'] = ''
        translators = self.request.GET.get('translators')
        if translators is not None and translators != "":
            context['translators'] = translators
        else:
            context['translators'] = ''
        form_of_publication = self.request.GET.get('form_of_publication')
        if form_of_publication is not None and form_of_publication != "":
            context['form_of_publication'] = form_of_publication
        else:
            context['form_of_publication'] = ''
        publication_city = self.request.GET.get('publication_city')
        if publication_city is not None and publication_city != "":
            context['publication_city'] = publication_city
        else:
            context['publication_city'] = ''
        language = self.request.GET.get('language')
        if language is not None and language != "":
            context['language'] = language
        else:
            context['language'] = ''
        content_genre = self.request.GET.get('content_genre')
        if content_genre is not None and content_genre != "":
            context['content_genre'] = content_genre
        else:
            context['content_genre'] = ''
        connected_to_special_occasion = self.request.GET.get('connected_to_special_occasion')
        if connected_to_special_occasion is not None and connected_to_special_occasion != "":
            context['connected_to_special_occasion'] = connected_to_special_occasion
        else:
            context['connected_to_special_occasion'] = ''
        currently_owned_by = self.request.GET.get('currently_owned_by')
        if currently_owned_by is not None and currently_owned_by != "":
            context['currently_owned_by'] = currently_owned_by
        else:
            context['currently_owned_by'] = ''
        keywords = self.request.GET.get('keywords')
        if keywords is not None and keywords != "":
            context['keywords'] = keywords
        else:
            context['keywords'] = ''
        uploadedfiles = self.request.GET.get('uploadedfiles')
        if uploadedfiles is not None and uploadedfiles != "":
            context['uploadedfiles'] = uploadedfiles
        else:
            context['uploadedfiles'] = ''
        filecategory = self.request.GET.get('filecategory')
        if filecategory is not None and filecategory != "":
            context['filecategory'] = filecategory
        else:
            context['filecategory'] = ''
        search_title = self.request.GET.get('search_title')
        if search_title is not None and search_title != "":
            context['search_title'] = search_title
        else:
            context['search_title'] = ''
        search_title_translation = self.request.GET.get('search_title_translation')
        if search_title_translation is not None and search_title_translation != "":
            context['search_title_translation'] = search_title_translation
        else:
            context['search_title_translation'] = ''
        search_author = self.request.GET.get('search_author')
        if search_author is not None and search_author != "":
            context['search_author'] = search_author
        else:
            context['search_author'] = ''
        search_keywords = self.request.GET.get('search_keywords')
        if search_keywords is not None and search_keywords != "":
            context['search_keywords'] = search_keywords
        else:
            context['search_keywords'] = ''
        search_image_content = self.request.GET.get('search_image_content')
        if search_image_content is not None and search_image_content != "":
            context['search_image_content'] = search_image_content
        else:
            context['search_image_content'] = ''
        search_description = self.request.GET.get('search_description')
        if search_description is not None and search_description != "":
            context['search_description'] = search_description
        else:
            context['search_description'] = ''

        cover_images = []
        context['publications'] = context['publications'].order_by('-date_created')
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

        #Check if a small version exists for a cover image
        for cover_image_index, cover_image in enumerate(cover_images):

            if cover_image is None:
                continue

            for extension in ['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG']:

                if not cover_image.path.endswith(extension):
                    continue

                small_image_path = cover_image.path.replace('.'+extension, '_small.'+extension)

                if isfile(small_image_path):
                    cover_images[cover_image_index] = cover_image.name.replace('.'+extension, '_small.'+extension)
                    break

        context['cover_images'] = cover_images
        context['request'] = self.request
        regexp = re.compile(context['q'], re.IGNORECASE)
        search_term_appear_in = []
        index = 0
        ids = []
        context['publications'] = list(context['publications'])
        for idx, im in enumerate(cover_images):
            if not im:
                ids.append(idx)
                #context['cover_images'].pop(idx)
                #context['publications'].pop(idx)
                #pdb.set_trace()

        context['publications'] = [pub for idx, pub in enumerate(context['publications']) if not idx in ids]
        context['cover_images'] = [img for idx, img in enumerate(context['cover_images']) if not idx in ids]
        for pub in context['publications']:
            search_term_appear_in.append('')
            if q == None or q == '':
                continue
            for field in Publication._meta.get_fields():
                if Publication._meta.get_field(field.name).get_internal_type() == 'ManyToManyField' or \
                        Publication._meta.get_field(field.name).get_internal_type() == 'ForeignKey':
                    if field.name == 'authors':
                        for author in pub.authors.all():
                            for author_field in Author._meta.get_fields():
                                if author_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(author, author_field.name), str) \
                                        and not isinstance(getattr(author, author_field.name), int):
                                    continue
                                if regexp.search(str(getattr(author, author_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'author ' + self.make_human_friendly(author_field.name)
                                    elif not ('author ' + self.make_human_friendly(author_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', author ' + self.make_human_friendly(author_field.name)
                    elif field.name == 'translators':
                        for translator in pub.translators.all():
                            for translator_field in Translator._meta.get_fields():
                                if translator_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(translator, translator_field.name), str) \
                                        and not isinstance(getattr(translator, translator_field.name), int):
                                    continue
                                if regexp.search(str(getattr(translator, translator_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'translator '+ self.make_human_friendly(translator_field.name)
                                    elif not ('translator ' + self.make_human_friendly(translator_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', translator ' + self.make_human_friendly(translator_field.name)
                    elif field.name == 'publication_city' and pub.publication_city:
                        if not isinstance(pub.publication_city.name, str) \
                                and not isinstance(pub.publication_city.name, int):
                            continue
                        if regexp.search(str(pub.publication_city.name)):
                            if search_term_appear_in[index] == '':
                                search_term_appear_in[index] = 'publication city name'
                            elif not ('publication city name' in search_term_appear_in[index]):
                                search_term_appear_in[index] = search_term_appear_in[index] + ', ' + 'publication city name'
                    elif field.name == 'publication_country' and pub.publication_country:
                        if not isinstance(pub.publication_country.name, str) \
                                and not isinstance(pub.publication_country.name, int):
                            continue
                        if regexp.search(str(pub.publication_country.name)):
                            if search_term_appear_in[index] == '':
                                search_term_appear_in[index] = 'publication country name'
                            elif not ('publication country name' in search_term_appear_in[index]):
                                search_term_appear_in[index] = search_term_appear_in[index] + ', ' + 'publication country name'
                    elif field.name == 'form_of_publication':
                        for form_of_publication in pub.form_of_publication.all():
                            for form_of_publication_field in FormOfPublication._meta.get_fields():
                                if form_of_publication_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(form_of_publication, form_of_publication_field.name), str) \
                                        and not isinstance(getattr(form_of_publication, form_of_publication_field.name),
                                                           int):
                                    continue
                                if regexp.search(str(getattr(form_of_publication, form_of_publication_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'form of publication ' + self.make_human_friendly(form_of_publication_field.name)
                                    elif not ('form of publication' + self.make_human_friendly(form_of_publication_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', form of publication ' + self.make_human_friendly(form_of_publication_field.name)
                    elif field.name == 'affiliated_church':
                        for affiliated_church in pub.affiliated_church.all():
                            for affiliated_church_field in Church._meta.get_fields():
                                if affiliated_church_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(affiliated_church, affiliated_church_field.name), str) \
                                        and not isinstance(getattr(affiliated_church, affiliated_church_field.name),
                                                           int):
                                    continue
                                if regexp.search(str(getattr(affiliated_church, affiliated_church_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'affiliated church ' + self.make_human_friendly(affiliated_church_field.name)
                                    elif not ('affiliated church ' + self.make_human_friendly(affiliated_church_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', affiliated church ' + self.make_human_friendly(affiliated_church_field.name)
                    elif field.name == 'language':
                        for language in pub.language.all():
                            for language_field in Language._meta.get_fields():
                                if language_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(language, language_field.name), str) \
                                        and not isinstance(getattr(language, language_field.name), int):
                                    continue
                                if regexp.search(str(getattr(language, language_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'language '+ self.make_human_friendly(language_field.name)
                                    elif not ('language ' + self.make_human_friendly(language_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', language ' + self.make_human_friendly(language_field.name)
                    elif field.name == 'translated_from' and pub.translated_from:
                        for translated_from_field in Language._meta.get_fields():
                            if translated_from_field.name == 'publication':
                                continue
                            if not isinstance(getattr(pub.translated_from, translated_from_field.name), str) \
                                    and not isinstance(getattr(pub.translated_from, translated_from_field.name), int):
                                continue
                            if regexp.search(str(getattr(pub.translated_from, translated_from_field.name))):
                                if search_term_appear_in[index] == '':
                                    search_term_appear_in[index] = 'translated from '+ self.make_human_friendly(translated_from_field.name)
                                elif not ('translated from ' + self.make_human_friendly(translated_from_field.name) in search_term_appear_in[index]):
                                    search_term_appear_in[index] = search_term_appear_in[
                                                                       index] + ', translated from ' + self.make_human_friendly(translated_from_field.name)
                    elif field.name == 'content_genre':
                        for genre in pub.content_genre.all():
                            for content_genre_field in Genre._meta.get_fields():
                                if content_genre_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(genre, content_genre_field.name), str) \
                                        and not isinstance(getattr(genre, content_genre_field.name), int):
                                    continue
                                if regexp.search(str(getattr(genre, content_genre_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'content genre '+ self.make_human_friendly(content_genre_field.name)
                                    elif not ('content genre '+ self.make_human_friendly(content_genre_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', content genre ' + self.make_human_friendly(content_genre_field.name)
                    elif field.name == 'connected_to_special_occasion':
                        for special_occasion in pub.connected_to_special_occasion.all():
                            for special_occasion_field in SpecialOccasion._meta.get_fields():
                                if special_occasion_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(special_occasion, special_occasion_field.name), str) \
                                        and not isinstance(getattr(special_occasion, special_occasion_field.name), int):
                                    continue
                                if regexp.search(str(getattr(special_occasion, special_occasion_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'special_occasion '+ self.make_human_friendly(special_occasion_field.name)
                                    elif not ('special_occasion '+ self.make_human_friendly(special_occasion_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', special_occasion ' + self.make_human_friendly(special_occasion_field.name)
                    elif field.name == 'collection_country' and pub.collection_country:
                        if not isinstance(pub.collection_country.name, str) \
                                and not isinstance(pub.collection_country.name, int):
                            continue
                        if regexp.search(str(pub.collection_country.name)):
                            if search_term_appear_in[index] == '':
                                search_term_appear_in[index] = 'collection country name'
                            elif not ('collection country name' in search_term_appear_in[index]):
                                search_term_appear_in[index] = search_term_appear_in[
                                                                   index] + ', ' + 'collection country name'
                    elif field.name == 'currently_owned_by':
                        for currently_owned_by in pub.currently_owned_by.all():
                            for currently_owned_by_field in Owner._meta.get_fields():
                                if currently_owned_by_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(currently_owned_by, currently_owned_by_field.name), str) \
                                        and not isinstance(getattr(currently_owned_by, currently_owned_by_field.name),
                                                           int):
                                    continue
                                if regexp.search(str(getattr(currently_owned_by, currently_owned_by_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'currently_owned_by_field '+ self.make_human_friendly(currently_owned_by_field.name)
                                    elif not ('currently_owned_by_field '+ self.make_human_friendly(currently_owned_by_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', currently_owned_by_field ' + self.make_human_friendly(currently_owned_by_field.name)
                    elif field.name == 'keywords':
                        for keyword in pub.keywords.all():
                            for keyword_field in Keyword._meta.get_fields():
                                if keyword_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(keyword, keyword_field.name), str) \
                                        and not isinstance(getattr(keyword, keyword_field.name), int):
                                    continue
                                if regexp.search(str(getattr(keyword, keyword_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'keyword '+ self.make_human_friendly(keyword_field.name)
                                    elif not ('keyword '+ self.make_human_friendly(keyword_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', keyword ' + self.make_human_friendly(keyword_field.name)
                    elif field.name == 'uploadedfiles':
                        for uploadedfile in pub.uploadedfiles.all():
                            for uploadedfile_field in UploadedFile._meta.get_fields():
                                if uploadedfile_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(uploadedfile, uploadedfile_field.name), str) \
                                        and not isinstance(getattr(uploadedfile, uploadedfile_field.name), int):
                                    continue
                                if regexp.search(str(getattr(uploadedfile, uploadedfile_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'uploadedfile '+ self.make_human_friendly(uploadedfile_field.name)
                                    elif not ('uploadedfile '+ self.make_human_friendly(uploadedfile_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', uploadedfile ' + self.make_human_friendly(uploadedfile_field.name)
                    elif field.name == 'created_by':
                        user_fields = ['username', 'first_name', 'last_name']
                        for created_by_field in user_fields:
                            if not pub.created_by or not isinstance(getattr(pub.created_by, created_by_field), str) \
                                    and not isinstance(getattr(pub.created_by, created_by_field), int):
                                continue
                            if regexp.search(str(getattr(pub.created_by, created_by_field))):
                                if search_term_appear_in[index] == '':
                                    search_term_appear_in[index] = 'created_by '+ created_by_field
                                elif not ('created_by '+created_by_field in search_term_appear_in[index]):
                                    search_term_appear_in[index] = search_term_appear_in[
                                                                       index] + ', created_by ' + created_by_field
                if not isinstance(getattr(pub, field.name), str) and not isinstance(getattr(pub, field.name), int):
                    continue
                elif regexp.search(str(getattr(pub, field.name))):
                    if search_term_appear_in[index] == '':
                        search_term_appear_in[index] = self.make_human_friendly(field.name)
                    elif not (field.name in search_term_appear_in[index]):
                        search_term_appear_in[index] = search_term_appear_in[index] + ', ' + self.make_human_friendly(field.name)
            index += 1
        context['search_term_appear_in'] = search_term_appear_in
        #pdb.set_trace()
        #for pub in context['publications']:

        context['zipped_data'] = zip(context['publications'], context['cover_images'], context['search_term_appear_in'])
        return context


class SearchResultsViewNew(ListView):
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
    publications = Publication.objects.filter(is_deleted=False, is_stub=False)
    paginate_by = 500
    #ordering = 'title'

    '''
    def get_success_url(self):
        url = self.request.GET.get('')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        if self.request.GET.get('q'):
            url += '&q' + self.request.GET.get('q')
        return url
    '''

    def get_template_names(self):
        if self.request.path == 'uploadedfile_new/' or self.request.path == 'uploadedfile_unlink/<int:pk>':
            return ['publications/form_create.html']
        return ['publications/show_new.html']

    def post(self, request, *args, **kwargs):
        return export_xlsx_file(request, self.get_queryset())
        #q = request.POST.get('q')
        #pubs= self.get_queryset()
        #return render(request, self.template_name, {'publications': pubs, 'q': q})

    def get_ordering(self):
        #pdb.set_trace()
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_queryset(self):

            #pub.save()
        #form = PublicationForm(self.request.GET)
        authors = self.request.GET.getlist('authors')
        translators = self.request.GET.getlist('translators')
       #pdb.set_trace()
        if not authors == ['']:
            authors = Author.objects.filter(pk__in=authors).all()
        if not translators == ['']:
            translators = Translator.objects.filter(pk__in=translators).all()
        form_of_publications = self.request.GET.getlist('form_of_publication')
        if not form_of_publications == ['']:
            form_of_publications = FormOfPublication.objects.filter(pk__in=form_of_publications).all()
        languages = self.request.GET.getlist('language')
        if not languages == ['']:
            languages = Language.objects.filter(pk__in=languages).all()
        affiliated_churches = self.request.GET.getlist('affiliated_church')
        if not affiliated_churches == ['']:
            affiliated_churches = Church.objects.filter(pk__in=affiliated_churches).all()
        content_genres = self.request.GET.getlist('content_genre')
        if not content_genres == ['']:
            content_genres = Genre.objects.filter(pk__in=content_genres).all()
        connected_to_special_occasions = self.request.GET.getlist('connected_to_special_occasion')
        if not connected_to_special_occasions == ['']:
            connected_to_special_occasions = SpecialOccasion.objects.filter(pk__in=connected_to_special_occasions).all()
        currently_owned_by = self.request.GET.getlist('currently_owned_by')
        if not currently_owned_by == ['']:
            currently_owned_by = Owner.objects.filter(pk__in=currently_owned_by).all()
        copyrights = self.request.GET.get('copyrights')
        is_a_translation = self.request.GET.get('is_a_translation')

        publications = Publication.objects.filter(is_deleted=False, is_stub=False)

        #publications = Publication.objects.filter(is_deleted=False).values('id').distinct()
        #publications = publications.filter(is_deleted=False)
        uploadedfiles = self.request.GET.getlist('uploadedfiles')
        #files = UploadedFile.objects.filter(is_deleted=False)
        #uploadedfiles = files.filter(pk__in=uploadedfiles).all()
        if not uploadedfiles == ['']:
            uploadedfiles = UploadedFile.objects.filter(pk__in=uploadedfiles).all()
        keywords = self.request.GET.getlist('keywords')
        if not keywords == ['']:
            keywords = Keyword.objects.filter(pk__in=keywords).all()
        translated_from = self.request.GET.getlist('translated_From')
        if not translated_from == ['']:
            translated_from = Language.objects.filter(pk__in=translated_from).all()
        city = self.request.GET.getlist('publication_city')
        country = self.request.GET.getlist('publication_country')
        collection_country = self.request.GET.getlist('collection_country')
        filecategory = self.request.GET.getlist('filecategory')
        if not filecategory == ['']:
            filecategory = FileCategory.objects.filter(pk__in=filecategory).all()

        if list(collection_country) != ['']:
            collection_country = Country.objects.filter(pk__in=city).all()

        if list(country) != ['']:
            country = Country.objects.filter(pk__in=country).all()

        print('....', city)
        if list(city) != ['']:
            city = City.objects.filter(pk__in=city).all()

        print(publications)

        search_title = self.request.GET.get('search title')
        search_title_translation = self.request.GET.get('search title translation')
        search_author = self.request.GET.get('search author')
        search_keywords = self.request.GET.get('search keywords')
        search_image_content = self.request.GET.get('search image content')
        search_description = self.request.GET.get('search description')


        exclude = ['csrfmiddlewaretoken','search', 'order_by', 'direction']
        in_variables = [('authors', authors), ('translators', translators), ('form_of_publication', form_of_publications), ('language',languages), ('affiliated_church', affiliated_churches) \
        , ('content_genre', content_genres), ('connected_to_special_occasion', connected_to_special_occasions), ('currently_owned_by', currently_owned_by),\
        ('uploadedfiles', uploadedfiles), ('publication_country', country), ('publication_city', city), ('collection_country', collection_country), \
        ('keywords', keywords), ('translated_from',translated_from), ('uploadedfiles__filecategory', filecategory),
                    ]
        special_case = ['copyrights', 'page', 'is_a_translation', 'filecategory']

        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            if query_string.lower() in countries_dict.keys():
                query_string = countries_dict[query_string.lower()]

            search_fields = []

            if((search_title == 'true' and search_title_translation == 'true' and search_author == 'true' and search_keywords == 'true' and \
                    search_image_content == 'true' and search_description == 'true') or (search_title == 'false' and search_title_translation == 'false' and \
                    search_author == 'false' and search_keywords == 'false' and search_image_content == 'false' and \
                    search_description == 'false') or (not search_title and not search_title_translation and not search_author and not search_keywords and \
                    not search_image_content and not search_description)):
                search_fields = ['title', 'title_subtitle_transcription', 'title_translation', 'authors__name', 'authors__name_original_language', 'authors__extra_info', \
                      'form_of_publication__name', 'editor', 'printed_by', 'published_by', 'publication_year', 'publication_country__name', 'publication_city__name', 'publishing_organisation', 'translators__name', 'translators__name_original_language', 'translators__extra_info', \
                      'language__name', 'language__direction', 'affiliated_church__name', 'extra_info', 'content_genre__name', 'connected_to_special_occasion__name', 'donor', 'content_description', 'description_of_illustration', \
                      'nr_of_pages', 'uploadedfiles__filecategory__name', 'uploadedfiles__uploaded_at', 'uploadedfiles__image_contents', \
                      'uploadedfiles__image_title', 'general_comments', 'team_comments', 'keywords__name', 'is_a_translation', 'ISBN_number', 'translated_from__name', 'translated_from__direction', \
                      'title2', 'title_subtitle_transcription2', 'title_translation2', 'title3', 'title_subtitle_transcription3', 'title_translation3', \
                      'title4', 'title_subtitle_transcription4', 'title_translation4', 'title5', 'title_subtitle_transcription5', 'title_translation5', \
                      'currency', 'price', 'collection_context']

            else:
                if search_title == 'true':
                    search_fields.extend(['title'])
                if search_title_translation == 'true':
                    search_fields.extend(['title_translation'])
                if search_author == 'true':
                    search_fields.extend(['authors__name', 'authors__name_original_language', 'authors__extra_info'])
                if search_keywords == 'true':
                    search_fields.extend(['keywords__name'])
                if search_image_content == 'true':
                    search_fields.extend(['uploadedfiles__image_contents'])
                if search_description == 'true':
                    search_fields.extend(['content_description'])

            if self.request.user.is_authenticated:
                search_fields.extend(['collection_date', 'collection_country__name', 'collection_venue_and_city', 'contact_telephone_number', 'contact_email', 'contact_website', 'currently_owned_by__name'])

            print(query_string)
            #arabic_query = translator.translate(query_string, dest='ar').text
            query_string = to_searchable(query_string)

            #arabic_query = to_searchable(arabic_query)
            entry_query = get_query(query_string, search_fields)
            #publications

            #arabic_query = get_query(arabic_query, search_fields)
            print('&&&&&&', query_string)
            #publications = publications.filter(entry_query)
            #pdb.set_trace()
            #publications = publications.filter(Q(entry_query) | Q(arabic_query))
            publications = publications.filter(Q(entry_query))
            #for (idx, apin) in enumerate(appears_in):

            ordering = self.get_ordering()
            if ordering is not None and ordering != "":

                if 'publication_year' in ordering:
                    if ordering == "publication_year":
                        ordering = 'y'
                    else:
                        ordering = '-y'

                    publications = publications.annotate(y=Coalesce('publication_year', 'start_year')).order_by(ordering)
                else:
                    publications = publications.order_by(ordering)

            publications = publications.distinct()

            #pdb.set_trace()

            #context['publications'] = publications
            return publications

        for field_name in self.request.GET:
            get_value = self.request.GET.get(field_name)
            if get_value != "" and not field_name in exclude and not field_name in [i[0] for i in in_variables] and\
               not field_name in special_case:
                print('******', field_name)
                #arabic_query = translator.translate(get_value, dest='ar').text
                get_value = to_searchable(get_value)
                get_value = get_query(get_value, [field_name])
                #arabic_query = get_query(arabic_query, [field_name])
                print('444444444', get_value)
                publications.filter(Q(get_value))
                #publications = publications.filter(Q(get_value) | Q(arabic_query))
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

                if 'publication_year' in ordering:
                    if ordering == "publication_year":
                        ordering = 'y'
                    else:
                        ordering = '-y'

                    publications = publications.annotate(y=Coalesce('publication_year', 'start_year')).order_by(
                        ordering)
                else:
                    publications = publications.order_by(ordering)

        elif self.request.path == '/publication/show/' or self.request.path == '/':
            publications = publications.order_by('-date_created')

        return publications

    def make_human_friendly(self, field):
        return field.replace("_", " ")

    def get_context_data(self, **kwargs):
        context = super(SearchResultsViewNew, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        #pdb.set_trace()
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
        affiliated_church = self.request.GET.get('affiliated_church')
        if affiliated_church is not None and affiliated_church != "":
            context['affiliated_church'] = affiliated_church
        else:
            context['affiliated_church'] = ''
        authors = self.request.GET.get('authors')
        if authors is not None and authors != "":
            context['authors'] = authors
        else:
            context['authors'] = ''
        translators = self.request.GET.get('translators')
        if translators is not None and translators != "":
            context['translators'] = translators
        else:
            context['translators'] = ''
        form_of_publication = self.request.GET.get('form_of_publication')
        if form_of_publication is not None and form_of_publication != "":
            context['form_of_publication'] = form_of_publication
        else:
            context['form_of_publication'] = ''
        publication_city = self.request.GET.get('publication_city')
        if publication_city is not None and publication_city != "":
            context['publication_city'] = publication_city
        else:
            context['publication_city'] = ''
        language = self.request.GET.get('language')
        if language is not None and language != "":
            context['language'] = language
        else:
            context['language'] = ''
        content_genre = self.request.GET.get('content_genre')
        if content_genre is not None and content_genre != "":
            context['content_genre'] = content_genre
        else:
            context['content_genre'] = ''
        connected_to_special_occasion = self.request.GET.get('connected_to_special_occasion')
        if connected_to_special_occasion is not None and connected_to_special_occasion != "":
            context['connected_to_special_occasion'] = connected_to_special_occasion
        else:
            context['connected_to_special_occasion'] = ''
        currently_owned_by = self.request.GET.get('currently_owned_by')
        if currently_owned_by is not None and currently_owned_by != "":
            context['currently_owned_by'] = currently_owned_by
        else:
            context['currently_owned_by'] = ''
        keywords = self.request.GET.get('keywords')
        if keywords is not None and keywords != "":
            context['keywords'] = keywords
        else:
            context['keywords'] = ''
        uploadedfiles = self.request.GET.get('uploadedfiles')
        if uploadedfiles is not None and uploadedfiles != "":
            context['uploadedfiles'] = uploadedfiles
        else:
            context['uploadedfiles'] = ''
        filecategory = self.request.GET.get('filecategory')
        if filecategory is not None and filecategory != "":
            context['filecategory'] = filecategory
        else:
            context['filecategory'] = ''

        cover_images = []

        used_uploaded_file_pks = set()

        for pub in context['publications']:
            min = 999
            length = len(cover_images)
            inside = False

            for uploadedfile in pub.uploadedfiles.all():
                if uploadedfile.filecategory and uploadedfile.filecategory.list_view_priority:

                    #If filtering on a file category, only use files of that category
                    if filecategory != None and uploadedfile.filecategory.pk != int(filecategory):
                        continue

                    #Dont show the same uploaded file twice (for example when a periodical has >1 front covers)
                    if uploadedfile.pk in used_uploaded_file_pks:
                        continue

                    compare = int(uploadedfile.filecategory.list_view_priority)
                    if compare < min:
                        min = compare
                        if inside:
                            cover_images = cover_images[:-1]
                        inside = True
                        cover_images.append(uploadedfile.file)
                        used_uploaded_file_pks.add(uploadedfile.pk)

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

        #Now we have all cover images, try to find smaller versions
        small_cover_images = []
        small_cover_image = None

        for cover_image in cover_images:

            small_cover_image = None

            if cover_image is None:
                small_cover_images.append(None)
                continue

            for extension in ['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG']:

                if not cover_image.path.endswith(extension):
                    continue

                small_image_path = cover_image.path.replace('.' + extension, '_small.' + extension)

                if isfile(small_image_path):
                    small_cover_image = cover_image.name.replace('.' + extension, '_small.' + extension)
                    break

            if small_cover_image is None:
                small_cover_images.append(cover_image)
            else:
                small_cover_images.append(small_cover_image)

        context['cover_images'] = small_cover_images

        context['request'] = self.request

        regexp = re.compile(context['q'], re.IGNORECASE)
        search_term_appear_in = []
        index = 0
        for pub in context['publications']:
            search_term_appear_in.append('')
            if q == None or q == '':
                continue
            for field in Publication._meta.get_fields():
                if Publication._meta.get_field(field.name).get_internal_type() == 'ManyToManyField' or \
                        Publication._meta.get_field(field.name).get_internal_type() == 'ForeignKey':
                    if field.name == 'authors':
                        for author in pub.authors.all():
                            for author_field in Author._meta.get_fields():
                                if author_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(author, author_field.name), str) \
                                        and not isinstance(getattr(author, author_field.name), int):
                                    continue
                                if regexp.search(str(getattr(author, author_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'author ' + self.make_human_friendly(author_field.name)
                                    elif not ('author ' + self.make_human_friendly(author_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', author ' + self.make_human_friendly(author_field.name)
                    elif field.name == 'translators':
                        for translator in pub.translators.all():
                            for translator_field in Translator._meta.get_fields():
                                if translator_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(translator, translator_field.name), str) \
                                        and not isinstance(getattr(translator, translator_field.name), int):
                                    continue
                                if regexp.search(str(getattr(translator, translator_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'translator '+ self.make_human_friendly(translator_field.name)
                                    elif not ('translator ' + self.make_human_friendly(translator_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', translator ' + self.make_human_friendly(translator_field.name)
                    elif field.name == 'publication_city' and pub.publication_city:
                        if not isinstance(pub.publication_city.name, str) \
                                and not isinstance(pub.publication_city.name, int):
                            continue
                        if regexp.search(str(pub.publication_city.name)):
                            if search_term_appear_in[index] == '':
                                search_term_appear_in[index] = 'publication city name'
                            elif not ('publication city name' in search_term_appear_in[index]):
                                search_term_appear_in[index] = search_term_appear_in[index] + ', ' + 'publication city name'
                    elif field.name == 'publication_country' and pub.publication_country:
                        if not isinstance(pub.publication_country.name, str) \
                                and not isinstance(pub.publication_country.name, int):
                            continue
                        if regexp.search(str(pub.publication_country.name)):
                            if search_term_appear_in[index] == '':
                                search_term_appear_in[index] = 'publication country name'
                            elif not ('publication country name' in search_term_appear_in[index]):
                                search_term_appear_in[index] = search_term_appear_in[index] + ', ' + 'publication country name'
                    elif field.name == 'form_of_publication':
                        for form_of_publication in pub.form_of_publication.all():
                            for form_of_publication_field in FormOfPublication._meta.get_fields():
                                if form_of_publication_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(form_of_publication, form_of_publication_field.name), str) \
                                        and not isinstance(getattr(form_of_publication, form_of_publication_field.name),
                                                           int):
                                    continue
                                if regexp.search(str(getattr(form_of_publication, form_of_publication_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'form of publication ' + self.make_human_friendly(form_of_publication_field.name)
                                    elif not ('form of publication' + self.make_human_friendly(form_of_publication_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', form of publication ' + self.make_human_friendly(form_of_publication_field.name)
                    elif field.name == 'affiliated_church':
                        for affiliated_church in pub.affiliated_church.all():
                            for affiliated_church_field in Church._meta.get_fields():
                                if affiliated_church_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(affiliated_church, affiliated_church_field.name), str) \
                                        and not isinstance(getattr(affiliated_church, affiliated_church_field.name),
                                                           int):
                                    continue
                                if regexp.search(str(getattr(affiliated_church, affiliated_church_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'affiliated church ' + self.make_human_friendly(affiliated_church_field.name)
                                    elif not ('affiliated church ' + self.make_human_friendly(affiliated_church_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', affiliated church ' + self.make_human_friendly(affiliated_church_field.name)
                    elif field.name == 'language':
                        for language in pub.language.all():
                            for language_field in Language._meta.get_fields():
                                if language_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(language, language_field.name), str) \
                                        and not isinstance(getattr(language, language_field.name), int):
                                    continue
                                if regexp.search(str(getattr(language, language_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'language '+ self.make_human_friendly(language_field.name)
                                    elif not ('language ' + self.make_human_friendly(language_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', language ' + self.make_human_friendly(language_field.name)
                    elif field.name == 'translated_from' and pub.translated_from:
                        for translated_from_field in Language._meta.get_fields():
                            if translated_from_field.name == 'publication':
                                continue
                            if not isinstance(getattr(pub.translated_from, translated_from_field.name), str) \
                                    and not isinstance(getattr(pub.translated_from, translated_from_field.name), int):
                                continue
                            if regexp.search(str(getattr(pub.translated_from, translated_from_field.name))):
                                if search_term_appear_in[index] == '':
                                    search_term_appear_in[index] = 'translated from '+ self.make_human_friendly(translated_from_field.name)
                                elif not ('translated from ' + self.make_human_friendly(translated_from_field.name) in search_term_appear_in[index]):
                                    search_term_appear_in[index] = search_term_appear_in[
                                                                       index] + ', translated from ' + self.make_human_friendly(translated_from_field.name)
                    elif field.name == 'content_genre':
                        for genre in pub.content_genre.all():
                            for content_genre_field in Genre._meta.get_fields():
                                if content_genre_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(genre, content_genre_field.name), str) \
                                        and not isinstance(getattr(genre, content_genre_field.name), int):
                                    continue
                                if regexp.search(str(getattr(genre, content_genre_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'content genre '+ self.make_human_friendly(content_genre_field.name)
                                    elif not ('content genre '+ self.make_human_friendly(content_genre_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', content genre ' + self.make_human_friendly(content_genre_field.name)
                    elif field.name == 'connected_to_special_occasion':
                        for special_occasion in pub.connected_to_special_occasion.all():
                            for special_occasion_field in SpecialOccasion._meta.get_fields():
                                if special_occasion_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(special_occasion, special_occasion_field.name), str) \
                                        and not isinstance(getattr(special_occasion, special_occasion_field.name), int):
                                    continue
                                if regexp.search(str(getattr(special_occasion, special_occasion_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'special_occasion '+ self.make_human_friendly(special_occasion_field.name)
                                    elif not ('special_occasion '+ self.make_human_friendly(special_occasion_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', special_occasion ' + self.make_human_friendly(special_occasion_field.name)
                    elif field.name == 'collection_country' and pub.collection_country:
                        if not isinstance(pub.collection_country.name, str) \
                                and not isinstance(pub.collection_country.name, int):
                            continue
                        if regexp.search(str(pub.collection_country.name)):
                            if search_term_appear_in[index] == '':
                                search_term_appear_in[index] = 'collection country name'
                            elif not ('collection country name' in search_term_appear_in[index]):
                                search_term_appear_in[index] = search_term_appear_in[
                                                                   index] + ', ' + 'collection country name'
                    elif field.name == 'currently_owned_by':
                        for currently_owned_by in pub.currently_owned_by.all():
                            for currently_owned_by_field in Owner._meta.get_fields():
                                if currently_owned_by_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(currently_owned_by, currently_owned_by_field.name), str) \
                                        and not isinstance(getattr(currently_owned_by, currently_owned_by_field.name),
                                                           int):
                                    continue
                                if regexp.search(str(getattr(currently_owned_by, currently_owned_by_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'currently_owned_by_field '+ self.make_human_friendly(currently_owned_by_field.name)
                                    elif not ('currently_owned_by_field '+ self.make_human_friendly(currently_owned_by_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', currently_owned_by_field ' + self.make_human_friendly(currently_owned_by_field.name)
                    elif field.name == 'keywords':
                        for keyword in pub.keywords.all():
                            for keyword_field in Keyword._meta.get_fields():
                                if keyword_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(keyword, keyword_field.name), str) \
                                        and not isinstance(getattr(keyword, keyword_field.name), int):
                                    continue
                                if regexp.search(str(getattr(keyword, keyword_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'keyword '+ self.make_human_friendly(keyword_field.name)
                                    elif not ('keyword '+ self.make_human_friendly(keyword_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', keyword ' + self.make_human_friendly(keyword_field.name)
                    elif field.name == 'uploadedfiles':
                        for uploadedfile in pub.uploadedfiles.all():
                            for uploadedfile_field in UploadedFile._meta.get_fields():
                                if uploadedfile_field.name == 'publication':
                                    continue
                                if not isinstance(getattr(uploadedfile, uploadedfile_field.name), str) \
                                        and not isinstance(getattr(uploadedfile, uploadedfile_field.name), int):
                                    continue
                                if regexp.search(str(getattr(uploadedfile, uploadedfile_field.name))):
                                    if search_term_appear_in[index] == '':
                                        search_term_appear_in[index] = 'uploadedfile '+ self.make_human_friendly(uploadedfile_field.name)
                                    elif not ('uploadedfile '+ self.make_human_friendly(uploadedfile_field.name) in search_term_appear_in[index]):
                                        search_term_appear_in[index] = search_term_appear_in[index] + ', uploadedfile ' + self.make_human_friendly(uploadedfile_field.name)
                    elif field.name == 'created_by':
                        user_fields = ['username', 'first_name', 'last_name']
                        for created_by_field in user_fields:
                            if not pub.created_by or not isinstance(getattr(pub.created_by, created_by_field), str) \
                                    and not isinstance(getattr(pub.created_by, created_by_field), int):
                                continue
                            if regexp.search(str(getattr(pub.created_by, created_by_field))):
                                if search_term_appear_in[index] == '':
                                    search_term_appear_in[index] = 'created_by '+ created_by_field
                                elif not ('created_by '+created_by_field in search_term_appear_in[index]):
                                    search_term_appear_in[index] = search_term_appear_in[
                                                                       index] + ', created_by ' + created_by_field
                if not isinstance(getattr(pub, field.name), str) and not isinstance(getattr(pub, field.name), int):
                    continue
                elif regexp.search(str(getattr(pub, field.name))):
                    if search_term_appear_in[index] == '':
                        search_term_appear_in[index] = self.make_human_friendly(field.name)
                    elif not (field.name in search_term_appear_in[index]):
                        search_term_appear_in[index] = search_term_appear_in[index] + ', ' + self.make_human_friendly(field.name)
            index += 1
        context['search_term_appear_in'] = search_term_appear_in
        #pdb.set_trace()
        context['zipped_data'] = zip(context['publications'], context['cover_images'], context['search_term_appear_in'])

        full_query_set = self.get_queryset()

        languages = Counter()
        genres = Counter()

        for pub in full_query_set:
            for language in pub.language.all():
                languages[language] += 1

            for genre in pub.content_genre.all():
                genres[genre] += 1

        context['languages'] = languages.items()
        context['genres'] = genres.items()
        context['count'] = full_query_set.count()
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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class ThrashbinUploadedFileShow(ListView):
    '''
    Inherits ListView shows author mainpage (ThrashbinShow)
    Uses context_object_name authors for all keywords.
    '''
    model = UploadedFile
    template_name = 'publications/thrashbin_uploadedfile_show.html'
    context_object_name = 'files'
    paginate_by = 10

    def get_queryset(self):
        files = UploadedFile.objects.filter(is_deleted=True)
        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            files = files.order_by(ordering)
        return files

    def get_ordering(self):
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = '-{}'.format(ordering)
        return ordering

    def get_context_data(self, **kwargs):
        context = super(ThrashbinUploadedFileShow, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

@login_required(login_url='/accounts/login/')
def ThrashbinUploadedFileRestore(request, pk):
    file = UploadedFile.objects.get(id=pk)
    file.is_deleted = False
    file.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class KeywordCreate(CreateView):
    '''
    Inherits CreateView uses a standard form for keywords.
    redirects to the keyword main page (show).
    '''
    template_name = 'publications/form.html'
    form_class = KeywordForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/keyword/show/' + '?page=' + url

class KeywordShow(ListView):
    '''
    Inherits ListView shows author mainpage (keyword_show)
    Uses context_object_name keywords for all keywords.
    '''
    model = Keyword
    #template_name = 'publications/keyword_show.html'
    context_object_name = 'keywords'
    paginate_by = 10

    def get_template_names(self):
        if self.request.path == '/keywords/':
            return ['publications/keyword_show_new.html']
        return ['publications/keyword_show.html']


    def get_queryset(self):
        keywords = Keyword.objects.all()

        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')

        if ordering is not None and ordering != "":

            if direction is None or direction in ['','asc']:
                keywords = keywords.order_by(Lower(ordering))
            elif direction == 'desc':
                keywords = keywords.order_by(Lower(ordering).desc())

        return keywords

    def get_ordering(self): #I think unused
        ordering = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction')
        if ordering is not None and ordering != "" and direction is not None and direction != "":
            if direction == 'desc':
                ordering = ordering
        return ordering, direction

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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class KeywordUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses KeywordForm as layout. And model Keyword.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = KeywordForm
    model = Keyword
    #success_url = '/keyword/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url

class AuthorCreate(CreateView):
    '''
    Inherits CreateView uses a standard form for Authors.
    redirects to the author main page (show).
    '''
    template_name = 'publications/form.html'
    form_class = AuthorForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/uploadedfile/show/' + '?page=' + url

class AuthorShow(ListView):
    '''
    Inherits ListView shows author mainpage (author_show)
    Uses context_object_name authors for all authors.
    '''
    model = Author
    #template_name = 'publications/author_show.html'
    context_object_name = 'authors'
    paginate_by = 500

    def get_template_names(self):
        if self.request.path == '/authors/':
            return ['publications/author_show_new.html']
        return ['publications/author_show.html']

    def get_queryset(self):
        authors = Author.objects.all()
        ordering = self.get_ordering()
        for author in authors:
            author.author_churches_list.set(Church.objects.none())
            for pub in author.publication_set.all():
                for church in pub.affiliated_church.all():
                    if church not in author.author_churches_list.all():
                        author.author_churches_list.add(church)
                        author.save()
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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class AuthorUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses AuthorForm as layout. And model Author.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = AuthorForm
    model = Author
    #success_url = '/author/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url
        
class TranslatorCreate(CreateView):
    '''
    Inherits CreateView. Uses TranslatorForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = TranslatorForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/translator/show/' + '?page=' + url

class TranslatorShow(ListView):
    '''
    Inherits ListView.
    Uses Translator as model.
    Uses translator_show.html as template_name.
    Set context_object_name to translators.
    '''
    model = Translator
    #template_name = 'publications/translator_show.html'
    context_object_name = 'translators'
    paginate_by = 500

    def get_template_names(self):
        if self.request.path == '/translators/':
            return ['publications/translator_show_new.html']
        return ['publications/translator_show.html']


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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class TranslatorUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses TranslatorForm as layout. And model Translator.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = TranslatorForm
    model = Translator
    #success_url = '/translator/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url
    
class FormOfPublicationCreate(CreateView):
    '''
    Inherits CreateView. Uses FormOfPublicationForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = FormOfPublicationForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/form_of_publication/show/' + '?page=' + url

class FormOfPublicationShow(ListView):
    '''
    Inherits ListView.
    Uses FormOfPublication as model.
    Uses form_of_publication_show.html as template_name.
    Set context_object_name to form_of_publications.
    '''
    model = FormOfPublication
    #template_name = 'publications/form_of_publication_show.html'
    context_object_name = 'form_of_publications'
    paginate_by = 10

    def get_template_names(self):
        if self.request.path == '/form_of_publications/':
            return ['publications/form_of_publication_show_new.html']
        return ['publications/form_of_publication_show.html']

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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class FormOfPublicationUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses FormOfPublicationForm as layout. And model FormOfPublication.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = FormOfPublicationForm
    model = FormOfPublication
    #success_url = '/form_of_publication/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('q'):
            url += '?q=' + self.request.GET.get('q')
        if self.request.GET.get('page'):
            url += '&page=' + self.request.GET.get('page')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url

class CityCreate(CreateView):
    '''
    Inherits CreateView. Uses CityForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = CityForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/city/show/' + '?page=' + url

class CityShow(ListView):
    '''
    Inherits ListView.
    Uses City as model.
    Uses city_show.html as template_name.
    Set context_object_name to cities.
    '''
    model = City
    #template_name = 'publications/city_show.html'
    context_object_name = 'cities'
    paginate_by = 10


    def get_template_names(self):
        if self.request.path == '/cities/':
            return ['publications/city_show_new.html']
        return ['publications/city_show.html']

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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class CityUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses CityForm as layout. And model City.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = CityForm
    model = City
    #success_url = '/city/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url
    
        
class GenreCreate(CreateView):
    '''
    Inherits CreateView. Uses GenreForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = GenreForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/genre/show/' + '?page=' + url

class GenreShow(ListView):
    '''
    Inherits ListView.
    Uses Genre as model.
    Uses genre_show.html as template_name.
    Set context_object_name to genres.
    '''
    model = Genre
    #template_name = 'publications/genre_show.html'
    context_object_name = 'genres'
    paginate_by = 10

    def get_template_names(self):
        if self.request.path == '/genres/':
            return ['publications/genre_show_new.html']
        return ['publications/genre_show.html']

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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class GenreUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses GenreForm as layout. And model Genre.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = GenreForm
    model = Genre
    #success_url = '/genre/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url
        
class ChurchShowNew(ListView):
    '''
    Inherits ListView.
    Uses Church as model.
    Uses church_show.html as template_name.
    Set context_object_name to churches.
    '''
    model = Church
    template_name = 'publications/church_show_new.html'
    context_object_name = 'churches'
    paginate_by = 6

    def get_queryset(self):
        churches = Church.objects.all()
        ordering = self.get_ordering()
        #pdb.set_trace()
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
        context = super(ChurchShowNew, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

class ChurchCreate(CreateView):
    '''
    Inherits CreateView. Uses ChurchForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = ChurchForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/church/show/' + '?page=' + url

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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class ChurchUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses ChurchForm as layout. And model Church.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = ChurchForm
    model = Church
    #success_url = '/church/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url

class LanguageShowNew(ListView):
    '''
    Inherits ListView.
    Uses Language as model.
    Uses language_show.html as template_name.
    Set context_object_name to languages.
    '''
    model = Language
    template_name = 'publications/language_show_new.html'
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
        context = super(LanguageShowNew, self).get_context_data(**kwargs)
        order_by = self.request.GET.get('order_by')
        if order_by is not None and order_by != "":
            context['order_by'] = order_by
            context['direction'] = self.request.GET.get('direction')
        else:
            context['order_by'] = ''
            context['direction'] = ''
        return context

class LanguageCreate(CreateView):
    '''
    Inherits CreateView. Uses LanguageForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = LanguageForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/language/show/' + '?page=' + url
    
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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

 
class LanguageUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses LanguageForm as layout. And model Language.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = LanguageForm
    model = Language
    #success_url = '/language/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url

    
class SpecialOccasionCreate(CreateView):
    '''
    Inherits CreateView. Uses SpecialOccasionForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = SpecialOccasionForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/special_occasion/show/' + '?page=' + url
    
class SpecialOccasionShow(ListView):
    '''
    Inherits ListView.
    Uses SpecialOccasion as model.
    Uses specialoccasion_show.html as template_name.
    Set context_object_name to specialoccasions.
    '''
    model = SpecialOccasion
    #template_name = 'publications/specialoccasion_show.html'
    context_object_name = 'specialoccasions'
    paginate_by = 10

    def get_template_names(self):
        if self.request.path == '/specialoccasions/':
            return ['publications/specialoccasion_show_new.html']
        return ['publications/specialoccasion_show.html']


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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class SpecialOccasionUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses SpecialOccasionForm as layout. And model SpecialOccasion.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = SpecialOccasionForm
    model = SpecialOccasion
    #success_url = '/special_occasion/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url

class OwnerCreate(CreateView):
    '''
    Inherits CreateView. Uses OwnerForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = OwnerForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/owner/show/' + '?page=' + url
    
class OwnerShow(ListView):
    '''
    Inherits ListView.
    Uses Owner as model.
    Uses owner_show.html as template_name.
    Set context_object_name to owners.
    '''
    model = Owner
    #template_name = 'publications/owner_show.html'
    context_object_name = 'owners'
    paginate_by = 10

    def get_template_names(self):
        return ['publications/owner_show.html']


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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class OwnerUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses OwnerForm as layout. And model Owner.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = OwnerForm
    model = Owner
    #success_url = '/owner/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url

class UploadedFileCreate(CreateView):
    '''
    Inherits CreateView. Uses UploadedFileForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = UploadedFileForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/uploadedfile/show/' + '?page=' + url

    
class UploadedFileShow(ListView):
    '''
    Inherits ListView.
    Uses UploadedFile as model.
    Uses uploadedfile_show.html as template_name.
    Set context_object_name to uploadedfiles.
    '''
    model = UploadedFile
    #template_name = 'publications/uploadedfile_show.html'
    context_object_name = 'uploadedfiles'
    paginate_by = 10

    def get_template_names(self):
        if self.request.path == '/uploadedfiles/':
            return ['publications/uploadedfile_show_new.html']
        return ['publications/uploadedfile_show.html']


    def get_queryset(self):
        uploadedfiles = UploadedFile.objects.filter(is_deleted=False)
        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            search_fields = ['image_title', 'filecategory__name', 'image_contents', 'file', 'uploaded_at']
            query_string = to_searchable(query_string)
            entry_query = get_query(query_string, search_fields)
            uploadedfiles = uploadedfiles.filter(Q(entry_query))

        ordering = self.get_ordering()
        if ordering is not None and ordering != "":
            uploadedfiles = uploadedfiles.order_by(ordering)
        return uploadedfiles

    def post(self, request, *args, **kwargs):
        return export_xlsx_file(request, self.get_queryset())

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

class SpaceTimeSearch(ListView):

    model = Publication
    context_object_name = 'publications'
    template_name = 'publications/spacetime_search.html'    

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.exclude(Q(publication_year__isnull=True) & Q(start_year__isnull=True))

        queryset = queryset.annotate(y=Coalesce('publication_year', 'start_year')).order_by('y')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Count all cities in the query set
        cities = {}

        for publication in context['publications']:

            if publication.publication_city is None:
                continue

            if not publication.publication_city.coordinates_known:
                continue

            if publication.publication_city.name not in cities:
                cities[publication.publication_city.name] = {'x_coord':publication.publication_city.x, 'y_coord':publication.publication_city.y, 'publications': []}

            year = str(publication.publication_year) if publication.publication_year is not None else '0'

            cities[publication.publication_city.name]['publications'].append({'year': year, 'title': publication.title})

        context['cities'] = cities
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
    uploadedfile.is_deleted = True
    uploadedfile.save()
    # redirect('/uploadedfile/show')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class UploadedFileUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses UploadedFileForm as layout. And model UploadedFileForm.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = UploadedFileForm
    model = UploadedFile
    #success_url = '/uploadedfile/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url

class FileCategoryCreate(CreateView):
    '''
    Inherits CreateView. Uses FileCategoryForm as layout.
    redirects to main page (show)
    '''
    template_name = 'publications/form.html'
    form_class = FileCategoryForm

    def get_success_url(self):
        url = self.request.GET.get('page')
        return '/filecategory/show/' + '?page=' + url


class FileCategoryShow(ListView):
    '''
    Inherits ListView.
    Uses Filecategory as model.
    Uses filecategory_show.html as template_name.
    Set context_object_name to filecategories.
    '''
    model = FileCategory
    #template_name = 'publications/filecategory_show.html'
    context_object_name = 'filecategories'
    paginate_by = 10

    def get_template_names(self):
        if self.request.path == '/filecategories/':
            return ['publications/filecategory_show_new.html']
        return ['publications/filecategory_show.html']


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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class FileCategoryUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses FilecategoryForm as layout. And model FileCategory.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = FileCategoryForm
    model = FileCategory
    #success_url = '/filecategory/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url

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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class IllustrationLayoutTypeUpdate(UpdateView):
    '''
    Inherits UpdateView uses a standard form (crispy form)
    Uses IllustrationLayoutTypeForm as layout. And model IllustrationLayoutType.
    redirects to local main page. (show)
    '''
    template_name = 'publications/form.html'
    form_class = IllustrationLayoutTypeForm
    model = IllustrationLayoutType
    #success_url = '/illustration_layout_type/show/'

    def get_success_url(self):
        url = self.request.GET.get('next')
        if self.request.GET.get('order_by'):
            url += '&order_by=' + self.request.GET.get('order_by')
        if self.request.GET.get('direction'):
            url += '&direction=' + self.request.GET.get('direction')
        return url

def about(request):
    return render(request, 'about.html')

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
    appears_in = []
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
         