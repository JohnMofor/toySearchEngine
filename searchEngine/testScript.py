from searchEngine.models import WordLocations,IndexedPage

googlePage = IndexedPage(url="http://www.google.com")
googlePage.save()
print googlePage

googleWord = "google"
googleWord2 = "google2"


googleWordLocation = WordLocations(url=googlePage,word=googleWord)
googleWordLocation.set_locations([1])
googleWordLocation.save()

googleWord2Location = WordLocations(url=googlePage,word=googleWord2)
googleWord2Location.set_locations([1])
googleWord2Location.save()

print "--"*100

print "googlePage.words:",googlePage.get_words()
print len(googlePage.words.all())