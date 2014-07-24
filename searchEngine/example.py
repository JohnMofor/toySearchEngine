from searchEngine.models import WordLocations, IndexedPage
from django.db.transaction import commit_on_success
from collections import defaultdict

# Example executions.
# Say "google" is an already saved WordLocations Instance, and we get these words from nltk clean html
list_of_words = ["new", "google", "googl3", "google4"]

# Database queries (eg, save(), get, filter) etc do disk-IO op,
# hence are slower than mem access,
# we could cache stuffs, and batch save all objects at the end :)
# with a function like:

@commit_on_success
def bulk_save(queryset):
    """
    source:#http://stackoverflow.com/questions/3395236/aggregating-saves-in-django

    """
    for item in queryset:
        print "saving: ", item
        item.save()

cache = {}  # word<String> : wordL<WordLocations>
cacheWordLocation = defaultdict(list)

# it's ok, we do this just ones...-ish
url = IndexedPage.objects.get(pk = "http://www.google.com")
for word in list_of_words:
    wordL = None
    if not word in cache:
        cache[word] = WordLocations(url=url, word=word)  
    
    
#     if word in cache:
#         wordL = cache[word]
#         
#     else:
#          unfortunately wordL wasn't in memory, let's go get it from disk,
#          Notice, the get_or_create... better than obj.get (1 disk access) then check
#          if the obj was non null and may create it (another disk access).
#         wordL, was_created = WordLocations.objects.get_or_create(url = url, word = word)
#          and cache it!
#         cache[word] = wordL
    cacheWordLocation[word].append(32)

for key in cache.keys():
    cache[key].set_locations(cacheWordLocation[key])
    

    # DO NOT SAVE() each time ;)
all_models_to_save = cache.values()
# you might not wanna forget this dude. question: why mush URL be the *last model*?
all_models_to_save.append(url)  

bulk_save(all_models_to_save)

raw_input("Inspect database (F5=refresh),\
 then press enter to undo this example's effects are removed")

for update in cache.values(): update.delete()
WordLocations(url = url, word = "google", locations = str([1])).save()



