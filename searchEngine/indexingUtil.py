import nltk
from urllib import urlopen
import lxml.html


url = "http://www.facebook.com"
html = urlopen(url).read()
raw = nltk.clean_html(html)
# print(nltk.word_tokenize(raw))
print(html)

print "Links", "--" * 100
raw_html = lxml.html.fromstring(html)
# select the url in href for all a tags(links)
for link in raw_html.xpath('//a/@href'):
    print link
