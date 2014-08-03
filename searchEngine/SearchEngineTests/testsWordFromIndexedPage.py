from django.test import TestCase
from searchEngine.models import WordFromIndexedPage, IndexedPage

#Started it, work in progress -saadiyah :)

class WordFromIndexedPageModelTest(TestCase):
    
    def setUp(self):
        models_to_delete = list(IndexedPage.objects.all())
        models_to_delete.extend(list(WordFromIndexedPage.objects.all()))
        for obj in models_to_delete:
            obj.delete()
    
    def test_set_and_check_attributes_empty_locations(self):
        url = "http://www.google.com"
        google_page = IndexedPage(url = url)
        google_page.save()
        our_word = WordFromIndexedPage(word = "google", indexed_page = google_page)
        locations_list = []
        our_word.set_offsets(locations_list)
        our_word.save()

        #checking if the locations are retrievable        
        retrieved_offsets = our_word.get_offsets()
        for location in locations_list:
            self.assertIn(location, retrieved_offsets)
        self.assertEqual(len(locations_list), len(retrieved_offsets))
    
    def test_set_and_check_attributes_non_duplicated_locations(self):
        url = "http://www.google.com"
        google_page = IndexedPage(url = url)
        google_page.save()
        our_word = WordFromIndexedPage(word = "google", indexed_page = google_page)    
        locations_list = [2, 5, 7, 11]
        our_word.set_offsets(locations_list)
        our_word.save()
        
        #checking if the locations are retrievable
        retrieved_offsets = our_word.get_offsets()
        for location in locations_list:
            self.assertIn(location, retrieved_offsets)
        self.assertEqual(len(locations_list), len(retrieved_offsets))
        
    def test_set_and_check_attributes_duplicated_locations(self):
        url = "http://www.google.com"
        google_page = IndexedPage(url = url)
        google_page.save()
        our_word = WordFromIndexedPage(word = "google", indexed_page = google_page)
        locations_list = [2, 5, 7, 7, 2, 2, 11]
        our_word.set_offsets(locations_list)
        our_word.save()
        
        #checking if the locations are retrievable
        retrieved_offsets = our_word.get_offsets()
        for location in locations_list:
            self.assertIn(location, retrieved_offsets)
        self.assertEqual(len(locations_list), len(retrieved_offsets))