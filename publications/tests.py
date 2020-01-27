import datetime

from django.test import TestCase, RequestFactory
from django.utils import timezone

from .models import Publication
from .views import PublicationDetailView, SearchResultsView
from django.test import Client
from django.contrib.auth.models import User

class PublicationModelTests(TestCase):

    def setUp(self):
        user = User.objects.create_superuser(username='admin', password='12345', email='')
        user.save()
        Publication.objects.create(title_original='eindhoven')
        Publication.objects.create(title_original='لحضور المؤتمر الدولي العاشر ليونيكود')
        
    def test_title_publication(self):
        dutch = Publication.objects.get(title_original='eindhoven')
        arabic = Publication.objects.get(title_original='لحضور المؤتمر الدولي العاشر ليونيكود')
        
        self.assertEqual(dutch.title_original, 'eindhoven')
        self.assertEqual(arabic.title_original, 'لحضور المؤتمر الدولي العاشر ليونيكود')
        
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
        self.assertEqual(1, response.context[-1]['publications'].count())

    