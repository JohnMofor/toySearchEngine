import urlparse

from django.db.transaction import commit_on_success
import requests

import utilities.tselogging as logging


logger = logging.getLogger('tse.u.util')


def constant(f):
    def fset(self, value):
        raise SyntaxError

    def fget(self):
        return f(self)
    return property(fget, fset)


@commit_on_success
def bulk_save(queryset):
    for item in queryset:
        item.save()


def welform_url(url):
    logger.debug(
        "About to format url={url}".format(url=url))
    raw_url = url
    parsed_url = urlparse.urlparse(raw_url)

    formatted_url = urlparse.urlparse(
        raw_url, scheme=(parsed_url.scheme or "http"))
    out_url = formatted_url.geturl().replace("///", "//", 1)
    logger.debug("formatted raw_url={raw_url} to {out_url}".format(
        raw_url=raw_url, out_url=out_url))
    return out_url


def final_url_after_redirects(raw_url, allow_redirects=True):
    formatted_http_url = welform_url(raw_url)
    try:
        r = requests.head(formatted_http_url, allow_redirects=allow_redirects)
        if r.status_code == 200:
            return r.url
    except:
        logger.error(
            "Page:{pageName} does not exist".format(
                pageName=formatted_http_url))
        return None


def profile_main(cmd):
    import cProfile
    import pstats
    import os

    cProfile.run(cmd, "profileRes.txt")
    p = pstats.Stats("profileRes.txt")
    p.sort_stats('cumulative').print_stats()
    os.remove("profileRes.txt")
