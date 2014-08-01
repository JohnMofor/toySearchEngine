"""
Class defining TSE data structures and Django Models.

"""

from django.db import models
import re
from astropy.constants.constant import Constant
from utilities.util import constant

class _CONST(object):
    @constant
    def WORD_MAX_LENGTH(self):
        return 70
    
    @constant
    def URL_MAX_LENGTH(self):
        return (2 * 1000 + 49)
    
    @constant
    def RAW_HTML_MAX_LENGTH(self):
        return (100 * 1000)

    @constant
    def HTML_TEXT_CONTENT_MAX_LENGTH(self):
        return (10 * 1000)
    @constant
    def LOCATIONS_MAX_LENGTH(self):
        return (0.5 * 1000)

    @constant
    def WFIP_WORD_DB_NAME(self):
        return 'Word'
    
    @constant
    def WFIP_IP_DB_NAME(self):
        return 'IndexedPage'
    
    @constant 
    def WFIP_UNIQUE_ID_DB_NAME(self):
        return 'Unique ID'
    
    @constant
    def WFIP_OFFSETSINIP_DB_NAME(self):
        return 'Offsets'

    @constant
    def IP_URL_DB_NAME(self):
        return 'URL'
    
    @constant
    def IP_RAW_HTML_DB_NAME(self):
        return 'Raw HTML'
    
    @constant
    def IP_TEXT_CONTENT_DB_NAME(self):
        return 'Parsed Text'
    
    @Constant
    def IP_RAW_HTML__HASH_DB_NAME(self):
        return 'HTML Hash'
    
    @Constant
    def IP_ORIGINAL_PAGE_DB_NAME(self):
        return 'Original Page'
    
    @constant
    def IP_INDEGREE_DB_NAME(self):
        return 'In-degree'

    def __setattr__(self, attr, value):
        pass

CONST = _CONST()

class WordFromIndexedPage(models.Model):

    word = models.CharField(
        max_length=CONST.WORD_MAX_LENGTH,
        null=False,
        db_column=CONST.WFIP_WORD_DB_NAME)

    indexedPage = models.ForeignKey(
        'IndexedPage',
        null=False,
        related_name='words',
        db_column=CONST.WFIP_IP_DB_NAME)

    _unique_id = models.IntegerField(
        primary_key=True, db_column=CONST.WFIP_UNIQUE_ID_DB_NAME)

    offsets_in_indexedPage = models.CharField(
        max_length=CONST.LOCATIONS_MAX_LENGTH,
        db_column=CONST.WFIP_OFFSETSINIP_DB_NAME)

    def set_offsets(self, locations):
        self.offsets_in_indexedPage = str(locations)

    def save(self, *args, **kwargs):
        if not self.pk:
            self._unique_id = hash(str(self.word) + str(self.indexedPage.url))
        super(WordFromIndexedPage, self).save(*args, **kwargs)

    def get_offsets(self):
        return map(int, re.findall('\d+', self.offsets_in_indexedPage))

    def __unicode__(self):
        components = [
            'WordFromIndexedPage<word:', str(
                self.word), 'indexedPage:', str(
                self.indexedPage.url), 'offsets_in_indexedPage:', str(
                self.offsets_in_indexedPage)]
        return ('').join(components)


class IndexedPage(models.Model):

    url = models.CharField(primary_key=True, max_length=CONST.URL_MAX_LENGTH,
                           db_column=CONST.IP_URL_DB_NAME)

    raw_html = models.CharField(
        null=True,
        max_length=CONST.RAW_HTML_MAX_LENGTH,
        db_column=CONST.IP_RAW_HTML_DB_NAME)

    text_content = models.CharField(
        null=True,
        max_length=CONST.HTML_TEXT_CONTENT_MAX_LENGTH,
        db_column=CONST.IP_TEXT_CONTENT_DB_NAME)

    raw_html_hash = models.IntegerField(
        null=True, db_column=CONST.IP_RAW_HTML__HASH_DB_NAME)

    original_page = models.ForeignKey(
        'self',
        null=True,
        related_name='synonyms',
        db_column=CONST.IP_ORIGINAL_PAGE_DB_NAME)

    indegree = models.IntegerField(
        null=True, db_column=CONST.IP_INDEGREE_DB_NAME)

    def get_words(self):
        return self.words.all()

    def get_synonyms(self):
        if self.original_page is None:
            return self.synonyms.all()
        else:
            all_synonyms = set(self.original_page.synonyms.all())
            all_synonyms.remove(self)
            all_synonyms.add(self.original_page)
            return list(all_synonyms)

    def __unicode__(self):
        return ('IndexedPage<{url}>').format(url=str(self.url))
