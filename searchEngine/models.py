from django.db import models
import re

class CONST(object):
    WORD_MAX_LENGTH = 70
    URL_MAX_LENGTH = 2 * (1000) + 49
    RAW_HTML_MAX_LENGTH = 100 * (1000)
    HTML_TEXT_CONTENT_MAX_LENGTH = 10 * (1000)
    LOCATIONS_MAX_LENGTH = 0.5 * (1000)

    WORDININDEXEDPAGE_WORD_DB_NAME = "Word"
    WORDININDEXEDPAGE_INDEXEDPAGE_DB_NAME = "IndexedPage"
    WORDININDEXEDPAGE_UNIQUE_ID_DB_NAME = "Unique ID"
    WORDININDEXEDPAGE_OFFSETSININDEXEDPAGE_DB_NAME = "Offsets"

    INDEXEDPAGE_URL_DB_NAME = "URL"
    INDEXEDPAGE_RAW_HTML_DB_NAME = "Raw HTML"
    INDEXEDPAGE_TEXT_CONTENT_DB_NAME = "Parsed Text"
    INDEXEDPAGE_RAW_HTML__HASH_DB_NAME = "HTML Hash"
    INDEXEDPAGE_ORIGINAL_PAGE_DB_NAME = "Original Page"
    INDEXEDPAGE_INDEGREE_DB_NAME = "In-degree"
    
    def __setattr__(self, attr, value):
        pass
    


class WordFromIndexedPage(models.Model):
    word = models.CharField(max_length = CONST.WORD_MAX_LENGTH,
                            null = False,
                            db_column = CONST.WORDININDEXEDPAGE_WORD_DB_NAME)

    indexedPage = models.ForeignKey("IndexedPage",
                            null = False,
                            related_name = "words",
                            db_column = CONST.WORDININDEXEDPAGE_INDEXEDPAGE_DB_NAME)

    _unique_id = models.IntegerField(primary_key = True,
                                     db_column = CONST.WORDININDEXEDPAGE_UNIQUE_ID_DB_NAME)

    offsets_in_indexedPage = models.CharField(max_length = CONST.LOCATIONS_MAX_LENGTH,
                                 db_column = CONST.WORDININDEXEDPAGE_OFFSETSININDEXEDPAGE_DB_NAME)

    def set_offsets(self, locations):
        self.offsets_in_indexedPage = str(locations)


    def save(self, *args, **kwargs):
        if not self.pk:
            self._unique_id = hash(str(self.word) + str(self.indexedPage.url))
        super(WordFromIndexedPage, self).save(*args, **kwargs)

    def get_offsets(self):
        return map(int, re.findall('\d+', self.offsets_in_indexedPage))

    def __unicode__(self):
        return "WordFromIndexedPage<word:{word},indexedPage:{indexedPage},offsets_in_indexedPage:{offsets_in_indexedPage}>".format(
                word = str(self.word), indexedPage = str(self.indexedPage.url), offsets_in_indexedPage = str(self.offsets_in_indexedPage))

class IndexedPage(models.Model):
    url = models.CharField(primary_key = True,
                           max_length = CONST.URL_MAX_LENGTH,
                           db_column = CONST.INDEXEDPAGE_URL_DB_NAME)

    raw_html = models.CharField(null = True,
                                max_length = CONST.RAW_HTML_MAX_LENGTH,
                                db_column = CONST.INDEXEDPAGE_RAW_HTML_DB_NAME)

    text_content = models.CharField(null = True,
                                    max_length = CONST.HTML_TEXT_CONTENT_MAX_LENGTH,
                                    db_column = CONST.INDEXEDPAGE_TEXT_CONTENT_DB_NAME)

    raw_html_hash = models.IntegerField(null = True,
                                        db_column = CONST.INDEXEDPAGE_RAW_HTML__HASH_DB_NAME)

    original_page = models.ForeignKey("self",
                                null = True,
                                related_name = "synonyms",
                                db_column = CONST.INDEXEDPAGE_ORIGINAL_PAGE_DB_NAME)

    indegree = models.IntegerField(null = True,
                                   db_column = CONST.INDEXEDPAGE_INDEGREE_DB_NAME)

    def get_words(self):
        return self.words.all()

    def get_synonyms(self):
        if self.original_page == None:
            return self.synonyms.all()
        else:
            all_synonyms = set(self.original_page.synonyms.all())
            all_synonyms.remove(self)
            all_synonyms.add(self.original_page)
            return list(all_synonyms)

    def __unicode__(self):
        return "IndexedPage<{url}>".format(url = str(self.url))
