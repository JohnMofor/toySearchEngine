import nltk   
from urllib import urlopen
import lxml.html


url = "http://www.example.com"
html = urlopen(url).read()    
raw = nltk.clean_html(html)  
print(nltk.word_tokenize(raw))

print "Links", "--"*100
dom =  lxml.html.fromstring(html)
for link in dom.xpath('//a/@href'): # select the url in href for all a tags(links)
    print link
