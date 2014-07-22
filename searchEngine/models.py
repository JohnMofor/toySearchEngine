from django.db import models

WORD_MAX_LENGTH = 70

class WordLocations(models.Model):
    url = models.ForeignKey("IndexedPage", null = False)
    word = models.CharField(max_length = WORD_MAX_LENGTH, null = False)
    _uniqueId = models.IntegerField(primary_key = True)
    locations = models.CharField(max_length = 500,)
    
    def addLocation(self, newLocation):
        '''
        Caller SHOULD CALL self.SAVE() when done
        '''
        if len(self.locations):
            self.locations += ("," + newLocation)
        else:
            self.locations = newLocation
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self._uniqueId = hash(str(self.word) + str(self.url.url))
            print "Newly created wordLocation " + str(self._uniqueId)
        super(WordLocations, self).save(*args, **kwargs)
    
    def getLocations(self):
        return [self.locations.split(",")]
        
    def __unicode__(self):
        return "WordLocations<word:{word},url:{url},locations:[{locations}]>".format(word = str(self.word),
                                                                                        url = str(self.url),
                                                                                        locations = str(self.locations))

class IndexedPage(models.Model):
    url = models.CharField(max_length = 2049, primary_key = True)
    wordLocations = models.ManyToManyField(WordLocations)
    textContent = models.CharField(max_length = 10)
    
    def __unicode__(self):
        return "IndexedPage<{url}>".format(url = str(self.url))
    
class IndexedWord(models.Model):
    word = models.CharField(max_length = WORD_MAX_LENGTH, primary_key = True)
    urls = models.ManyToManyField("IndexedPage")
    indegree = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return "IndexedWord<{word}>".format(word = str(self.word))    

