from django.test import TestCase
from searchEngine.models import WordFromIndexedPage, IndexedPage


class IndexedPageModelTest(TestCase):

    def setUp(self):
        models_to_delete = list(IndexedPage.objects.all())
        models_to_delete.extend(list(WordFromIndexedPage.objects.all()))
        for obj in models_to_delete:
            obj.delete()

    def test_get_words_no_words(self):
        url = "http://www.google.com"
        google_page = IndexedPage(url=url)
        google_page.save()
        word_list = []
        for word in word_list:
            WordFromIndexedPage(
                word=word,
                indexed_page=google_page,
                offsets_in_indexedPage=str(
                    [1])).save()
        self.assertEqual(len(google_page.words.all()), len(word_list))
        all_words = map(lambda element: element.word, google_page.get_words())
        for word in word_list:
            self.assertIn(word, all_words)

    def test_get_words_no_repetition(self):
        url = "http://www.google.com"
        google_page = IndexedPage(url=url)
        google_page.save()
        word_list = ["google", "feeling", "lucky", "search"]
        for word in word_list:
            WordFromIndexedPage(
                word=word,
                indexed_page=google_page,
                offsets_in_indexedPage=str(
                    [1])).save()
        self.assertEqual(len(google_page.words.all()), len(word_list))
        all_words = map(lambda element: element.word, google_page.get_words())
        for word in word_list:
            self.assertIn(word, all_words)

    def test_get_words_with_repetition(self):
        url = "http://www.google.com"
        google_page = IndexedPage(url=url)
        google_page.save()
        word_list = ["google", "feeling", "lucky", "search"] * 3
        for word in word_list:
            WordFromIndexedPage(
                word=word,
                indexed_page=google_page,
                offsets_in_indexedPage=str(
                    [1])).save()
        self.assertEqual(len(google_page.words.all()), len(set(word_list)))
        all_words = map(lambda element: element.word, google_page.get_words())
        for word in word_list:
            self.assertIn(word, all_words)

    def test_synonyms_logic_invariant(self):
        original_google_url = "http://www.google.com"
        original_google_page = IndexedPage(url=original_google_url)
        original_google_page.save()

        other_google_urls = [
            "www.google.com",
            "https://www.google.com",
            "google.com",
            "http://google.com"]
        for url in other_google_urls:
            IndexedPage(url=url, original_page=original_google_page).save()

        # Make sure they all know their original
        for page in IndexedPage.objects.all():
            if not page == original_google_page:
                self.assertEqual(original_google_page, page.original_page, "original not set!")
            else:
                self.assertIsNone(page.original_page, "original_page's orginal_page should be none")

    def test_get_synonyms(self):
        original_google_url = "http://www.google.com"
        original_google_page = IndexedPage(url=original_google_url)
        original_google_page.save()

        other_google_urls = [
            "www.google.com",
            "https://www.google.com",
            "google.com",
            "http://google.com"]
        noice_urls = ["facebook.com", "math.org"]
        for url in other_google_urls:
            IndexedPage(url=url, original_page=original_google_page).save()
        for url in noice_urls:
            IndexedPage(url=url).save()

        # test function from original
        expected = set(other_google_urls)
        actual = set([e.url for e in original_google_page.get_synonyms()])
        self.assertSetEqual(expected, actual)

        # test function from all secondary pages.
        for url in other_google_urls:
            secondary_page = IndexedPage.objects.get(pk=url)
            expected = set(other_google_urls) ^ set([url]) | set([original_google_url])
            actual = set([e.url for e in secondary_page.get_synonyms()])
            self.assertSetEqual(expected, actual)
