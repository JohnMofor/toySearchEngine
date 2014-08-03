from collections import defaultdict
from urlparse import urljoin
import re
import threading

from django.db import transaction
import lxml.html
import nltk
import requests

from searchEngine.models import WordFromIndexedPage, IndexedPage
from utilities.util import bulk_save, final_url_after_redirects, profile_main, \
    constant, RunOnMainThread
import utilities.tselogging as logging


logger = logging.getLogger("tse.se.indexer")


class _CONST(object):

    @constant
    def INDEXER_URL_CONNECTION_TIMEOUT(self):
        return 5000

CONST = _CONST()


@transaction.atomic
def page_already_indexed(indexed_page, text_content_hash):
    original = IndexedPage.objects.filter(text_content_hash=text_content_hash)
    if original.exists():
        indexed_page.original_page = original[0]
        indexed_page.save()
        indexed_page.original_page.save()
        return True
    else:
        indexed_page.text_content_hash = text_content_hash
        indexed_page.save()
        return False


class Indexer(threading.Thread):

    def __init__(
            self,
            indexed_page=None,
            on_finished_indexing=None,
            main_thread_cmd_queue=None,
            links_queue=None):

        threading.Thread.__init__(self)
        assert isinstance(indexed_page, IndexedPage)

        self.indexed_page = indexed_page
        self.on_finished_indexing = on_finished_indexing
        self.main_thread_cmd_queue = main_thread_cmd_queue
        self.links_queue = links_queue

        self.url = indexed_page.url

        self.cache = {}
        self.word_location_cache = defaultdict(list)

    def index_words(self, all_words):
        # Locations are the indices in all_words at which a particular word is
        for i in xrange(len(all_words)):
            current_word = all_words[i]
            if current_word not in self.cache:
                self.cache[current_word] = WordFromIndexedPage(
                    indexed_page=self.indexed_page,
                    word=current_word)
            self.word_location_cache[current_word].append(i)

        for key in self.cache:
            self.cache[key].set_offsets(self.word_location_cache[key])

    def populate_indexedPage(self, final_url):

        self.raw_html = requests.get(final_url).content
        self.text_content = nltk.clean_html(self.raw_html)
        self.text_content_hash = str(hash(self.text_content))

        command_for_page_already_indexed = RunOnMainThread(
            func_from_other_thread=page_already_indexed,
            args_to_func=((self.indexed_page, self.text_content_hash), {}),
            call_back_on_other_thread=self.on_page_already_indexed_done)

        self.main_thread_cmd_queue.append(command_for_page_already_indexed)

    def on_page_already_indexed_done(self, already_indexed):
        self.already_indexed = already_indexed
        if already_indexed:
            logger.info("IndexedPage {url} is NOT an Original.".format(url=self.url))
            return

        logger.info("IndexedPage {url} is an original".format(url=self.url))
        all_words = [word.lower() for word in re.findall(re.compile('\w+'), self.text_content)]
        self.index_words(all_words)

        self.indexed_page.raw_html = self.raw_html
        self.indexed_page.text_content = self.text_content

        all_models_to_save = self.cache.values()
        all_models_to_save.append(self.indexed_page)

        save_on_main_thread_command = RunOnMainThread(
            func_from_other_thread=bulk_save,
            args_to_func=((), {"queryset": all_models_to_save}),
            call_back_on_other_thread=self.on_all_models_to_save_saved)
        self.main_thread_cmd_queue.append(save_on_main_thread_command)

    def on_all_models_to_save_saved(self, _):
        all_links = [urljoin(self.final_url, link)
                     for link in lxml.html.fromstring(self.raw_html).xpath('//a/@href')]
        if hasattr(self.links_queue, "extend"):
            self.links_queue.extend(all_links)
        if (self.on_finished_indexing is not None):
            self.on_finished_indexing(self.url, self.already_indexed)
        logger.info("finished indexing url={url}".format(url=self.url))

    def run(self):
        logger.info("starting to index page url={url}".format(url=self.url))
        self.final_url = final_url_after_redirects(self.url)
        if self.final_url is not None:
            if self.links_queue is not None:
                self.populate_indexedPage(self.final_url)


def main():
    #t = Indexer(indexed_page="http://example.com", on_finished_indexing=None, links_queue=[])
    # t.start()
    # t.join()
    pass

if __name__ == '__main__':
    profile_main('main()')
