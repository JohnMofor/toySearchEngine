from searchEngine.models import WordFromIndexedPage, IndexedPage
from django.db.transaction import commit_on_success
from collections import defaultdict
import requests
from utilities import util
import nltk
import re


class CONST(object):

    INDEXER_URL_CONNECTION_TIMEOUT = 5000

    def __setattr__(self, attr, value):
        pass




class Indexer(object):

    def __init__(self, url):
        self.url = url
        self.cache = {}
        self.WordLocationCache = defaultdict(list)

    # same function as in the example file
    @commit_on_success
    def bulk_save(self, queryset):
        for item in queryset:
            print "saving: ", item
            item.save()

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
        self.bulk_save(all_models_to_save)

    def final_url_after_redirects(self):
        formatted_http_url = util.format_http_url(self.url)
        try:
            r = requests.head(formatted_http_url, allow_redirects=True)
            if r.status_code == 200:
                return r.url
        except:
            return None

    def start(self):
        final_url = Indexer.final_url_after_redirects(self)
        if final_url is None:
            print("this page does not exist!")
            return
        self.populate_indexedPage(final_url)
