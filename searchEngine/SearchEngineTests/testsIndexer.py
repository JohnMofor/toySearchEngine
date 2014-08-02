from django.test import TestCase
from searchEngine.models import WordFromIndexedPage, IndexedPage


class IndexerTest(TestCase):

    def setUp(self):
        models_to_delete = list(IndexedPage.objects.all())
        models_to_delete.extend(list(WordFromIndexedPage.objects.all()))
        for obj in models_to_delete:
            obj.delete()

    def test_google_dot_com(self):
        pass
    
    
