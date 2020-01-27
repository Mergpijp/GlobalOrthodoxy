import datetime

from django.test import TestCase, RequestFactory
from django.utils import timezone

from .models import Publication
from .views import PublicationDetailView


class PublicationModelTests(TestCase):

    def setUp(self):
        
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


    