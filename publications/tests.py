import datetime

from django.test import TestCase, RequestFactory
from django.utils import timezone

from .models import Publication
from .views import PublicationDetailView, SearchResultsView
from django.test import Client
from django.contrib.auth.models import User
import pdb

class PublicationModelTests(TestCase):

    def setUp(self):
        user = User.objects.create_superuser(username='admin', password='12345', email='')
        user.save()
        Publication.objects.create(title='eindhoven')
        Publication.objects.create(title='لحضور المؤتمر الدولي العاشر ليونيكود')
        Publication.objects.create(title='مزامير') #mazamir
        #Publication.objects.create(titlel='صلوات') #salawat
        
    def test_title_publication(self):
        dutch = Publication.objects.get(title='eindhoven')
        arabic = Publication.objects.get(title='لحضور المؤتمر الدولي العاشر ليونيكود')
        
        self.assertEqual(dutch.title, 'eindhoven')
        self.assertEqual(arabic.title, 'لحضور المؤتمر الدولي العاشر ليونيكود')
        
    def test_environment_set_in_context(self):
        request = RequestFactory().get('/publication/1/detail_view/')
        view = PublicationDetailView()
        view.setup(request)

        context = view.get_context_data()
        self.assertIn('now', context)

    def test_search_results(self):
        client = Client('127.0.0.1')
        response = client.login(username='admin', password='12345')
        response = client.get('/publication/show/', {'q': 'eindhoven'})
        #there should be one search result publication with the title 'eindhoven'
        #pdb.set_trace()
        self.assertEqual('eindhoven', response.context['publications'][0].title)
        #google translate will return the arabic word for mazamir.
        #response = client.get('/publication/show/', {'q': 'mazamir'})
        #Google translate is not functioning
        #self.assertEqual('مزامير', response.context['publications'][0].title)
        response = client.get('/publication/overview/')
        #first one is the newest one.
        self.assertEqual('مزامير', response.context['publications'][0].title)
        response = client.get('/publication/overview/', {'order_by': 'title', 'direction': 'asc'})
        self.assertEqual('eindhoven', response.context['publications'][0].title)
        self.assertEqual('لحضور المؤتمر الدولي العاشر ليونيكود', response.context['publications'][1].title)
        self.assertEqual('مزامير', response.context['publications'][2].title)
        response = client.get('/publication/overview/', {'order_by': 'title', 'direction': 'desc'})
        self.assertEqual('مزامير', response.context['publications'][0].title)
        self.assertEqual('لحضور المؤتمر الدولي العاشر ليونيكود', response.context['publications'][1].title)
        self.assertEqual('eindhoven', response.context['publications'][2].title)

        #response = client.get('/publication/show/', {'q': 'salawat'})
        #self.assertEqual('صلوات', response.context[-1]['publications'][0].title)

    def test_publication_create(self):
        client = Client('127.0.0.1')
        response = client.login(username='admin', password='12345')
        response = client.get('/publication/show/')
        self.assertEqual(3, response.context['publications'].count())
    