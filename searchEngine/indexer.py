from searchEngine.models import WordFromIndexedPage,IndexedPage
from django.db.transaction import commit_on_success
from collections import defaultdict
import urllib2

class CONST(object):
        
    INDEXER_URL_CONNECTION_TIMEOUT = 5000

class Indexer(object):
    
    def __init__(self, url):
        self.url = url
        self.cache = {}
        self.WordLocationCache = defaultdict(list)
    
    #same function as in the example file
    @commit_on_success
    def bulk_save(self, queryset):
        for item in queryset:
            print "saving: ", item
            item.save()

    
    def set_up_info_about_current_page(self):
       
        pass
    
    
        
    def url_connection(self):
        try:
            return urllib2.urlopen(self.url, timeout=CONST.INDEXER_URL_CONNECTION_TIMEOUT)
        except:
            return None
        
    def start(self):
        page = Indexer.url_connection(self)
        if page == None: 
            print("this page does not exist!")
            return
        return page
        

            
    
 