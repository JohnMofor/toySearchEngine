from searchEngine.models import WordLocations,IndexedPage,IndexedWord

googlePage = IndexedPage(url="http://www.google.com")
googlePage.save()
print googlePage

googleWord = IndexedWord(word="google")
googleWord2 = IndexedWord(word="google2")
print googleWord
googleWord.save()

googleWord.urls.add(googlePage)
googleWord.save()

print googleWord.urls.all()

googleWordLocation = WordLocations(url=googlePage,word=googleWord.word)
googleWordLocation.addLocation("1")
googleWordLocation.save()

googleWord2Location = WordLocations(url=googlePage,word=googleWord2.word)
googleWord2Location.addLocation("1")
googleWord2Location.save()
#print googleWordLocation

print "--"*100

print "googlePage.wordlocation_set:",googlePage.wordlocations_set.all()
print len(googlePage.wordlocations_set.all())
