from collections import defaultdict
import re

from django.db import transaction
import lxml.html
import nltk
from urlparse import urljoin
import requests

from searchEngine.models import WordFromIndexedPage, IndexedPage
from utilities.util import bulk_save, welform_url, final_url_after_redirects, profile_main
from utilities.util import constant
import utilities.tselogging as logging


logger = logging.getLogger("tse.se.indexer")


class _CONST(object):

    @constant
    def INDEXER_URL_CONNECTION_TIMEOUT(self):
        return 5000

CONST = _CONST()


@transaction.atomic
def page_already_indexed(indexedPage, text_content_hash):
    original = IndexedPage.objects.filter(text_content_hash=text_content_hash)
    if original.exists():
        indexedPage.original_page = original[0]
        indexedPage.save()
        indexedPage.original_page.save()
        return True
    else:
        indexedPage.text_content_hash = text_content_hash
        indexedPage.save()
        return False


class Indexer(object):

    def __init__(self, url):
        self.url = welform_url(url)
        self.cache = {}
        self.word_location_cache = defaultdict(list)
        self.indexed_page = None

    def index_words(self, all_words):
        # Locations are the indices in all_words at which a particular word is
        for i in xrange(len(all_words)):
            current_word = all_words[i]
            if current_word not in self.cache:
                self.cache[current_word] = WordFromIndexedPage(
                    indexedPage=self.indexed_page,
                    word=current_word)
            self.word_location_cache[current_word].append(i)

        for key in self.cache:
            self.cache[key].set_offsets(self.word_location_cache[key])

    def populate_indexedPage(self, final_url):
        # Acquire lock on self.url IndexedPage
        self.indexed_page, was_created = IndexedPage.objects.get_or_create(url=self.url)

        if not was_created:
            logger.info("The page with url={url} already exists".format(url=self.url))
            return

        raw_html = requests.get(final_url).content
        text_content = nltk.clean_html(raw_html)
        text_content_hash = str(hash(text_content))

        if page_already_indexed(self.indexed_page, text_content_hash):
            logger.info("IndexedPage.original has been set for url={url}".format(url=self.url))
            return

        logger.info("IndexedPage {url} is an original".format(url=self.url))
        all_words = [word.lower() for word in re.findall(re.compile('\w+'), text_content)]
        self.index_words(all_words)

        self.indexed_page.raw_html = raw_html
        self.indexed_page.text_content = text_content

        all_models_to_save = self.cache.values()
        all_models_to_save.append(self.indexed_page)
        bulk_save(all_models_to_save)

        return [urljoin(final_url, link)
                for link in lxml.html.fromstring(raw_html).xpath('//a/@href')]

    def start(self):
        logger.info("starting to index page url={url}".format(url=self.url))
        final_url = final_url_after_redirects(self.url)
        if final_url is not None:
            return self.populate_indexedPage(final_url)
        logger.info("finished indexing url={url}".format(url=self.url))

def main():
    print Indexer(url="http://norvig.com/big.txt").start()
    
if __name__ == '__main__':
    profile_main('main()')
