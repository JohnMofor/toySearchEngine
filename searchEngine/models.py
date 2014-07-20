from django.db import models

class indexedWord(models.Model):
    word = models.CharField(max_length=70)
    
    
class indexedPages(models.Model):
    url = models.CharField(max_length=500)
