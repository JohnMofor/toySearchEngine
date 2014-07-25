from searchEngine.models import WordFromIndexedPage,IndexedPage

googlePage = IndexedPage(url="http://www.google.com")
googlePage.save()
print googlePage

googleWord = "google"
googleWord2 = "google2"


googleWordLocation = WordFromIndexedPage(indexedPage=googlePage,word=googleWord)
googleWordLocation.set_offsets([1])
googleWordLocation.save()

googleWord2Location = WordFromIndexedPage(indexedPage=googlePage,word=googleWord2)
googleWord2Location.set_offsets([1])
googleWord2Location.save()

print "--"*100

print "googlePage.words:",googlePage.get_words()
print len(googlePage.words.all())