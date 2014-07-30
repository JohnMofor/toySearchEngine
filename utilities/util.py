import utilities.tselogging as logging
import urlparse
from django.db.transaction import commit_on_success

logger = logging.getLogger('tse.u.util')


class UTIL(object):

    def __init__(self):
        pass

    def __setattr__(self, attr, value):
        pass

@commit_on_success
def bulk_save(queryset):
    for item in queryset:
        item.save()


def format_http_url(url):
    logger.debug(
        "About to format url={url}".format(url=url))
    raw_url = url
    parsed_url = urlparse.urlparse(raw_url)
    formatted_url = urlparse.urlparse(
        raw_url, scheme=(parsed_url.scheme or "http"))
    out_url = formatted_url.geturl()
    logger.debug("formatted raw_url={raw_url} to {out_url}".format(
        raw_url=raw_url, out_url=out_url))
    return out_url

