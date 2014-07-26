import urlparse

class UTIL(object):
    
    def __init__(self):
        pass
    
    def __setattr__(self, attr, value):
        pass

def format_http_url(url):
    raw_url = url
    parsed_url = urlparse.urlparse(raw_url)
    formatted_url = urlparse.urlparse(raw_url, scheme=(parsed_url.scheme or "http"))
    return  formatted_url.geturl()
        