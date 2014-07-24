import nltk   
from urllib import urlopen
import lxml.html


url = "http://www.facebook.com"
html = urlopen(indexedPage).read()    
raw = nltk.clean_html(html)  
#print(nltk.word_tokenize(raw))
print(html)

print "Links", "--"*100
raw_html =  lxml.html.fromstring(html)
for link in raw_html.xpath('//a/@href'): # select the url in href for all a tags(links)
    print link
