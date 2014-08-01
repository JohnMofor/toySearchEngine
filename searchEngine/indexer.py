from collections import defaultdict
import requests
from utilities.util import bulk_save, format_http_url
import nltk
import re
from utilities.util import constant


class _CONST(object):

    @constant
    def INDEXER_URL_CONNECTION_TIMEOUT(self):
        return 5000

CONST = _CONST()


class Indexer(object):

    def __init__(self, url):
        self.url = url
        self.cache = {}
        self.word_location_cache = defaultdict(list)

    def populate_indexedPage(self, final_url):
        raw_html = requests.get(final_url).content
        raw_html_hash = str(hash(raw_html))
        text_content = nltk.clean_html(raw_html_hash)
        all_words = re.findall(re.compile('\w+'), text_content)

#         tokenizer = RegexpTokenizer(r'\w+')
#         words = tokenizer.tokenize(text_content)

        # todo: logic for locations

        all_models_to_save = self.cache.values()
        all_models_to_save.append(final_url)
        bulk_save(all_models_to_save)

    def final_url_after_redirects(self):
        formatted_http_url = format_http_url(self.url)
        try:
            r = requests.head(formatted_http_url, allow_redirects=True)
            if r.status_code == 200:
                return r.url
        except:
            return None

    def start(self):
        final_url = Indexer.final_url_after_redirects(self)
        if final_url is None:
            print "this page does not exist!"
            return
        self.populate_indexedPage(final_url)
