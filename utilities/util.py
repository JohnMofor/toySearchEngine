import Queue
import urlparse

from django.db.transaction import commit_on_success
import requests

import utilities.tselogging as logging


logger = logging.getLogger('tse.u.util')


def constant(f):
    '''Simple read-only decorator'''

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
    logger.debug("About to format url={url}".format(url=url))
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


class TQueue(Queue.Queue):

    """Simple wrapper about Queue.Queue (FIFO) to add more conventional
    methods."""

    def __init__(self, initial_list=[], maxsize=0):
        Queue.Queue.__init__(self, maxsize=maxsize)
        self.extend(initial_list)

    def extend(self, items, block=True, timeout=None):
        for item in items:
            Queue.Queue.put(self, item, block=block, timeout=timeout)

    def append(self, item, block=True, timeout=None):
        Queue.Queue.put(self, item, block=block, timeout=timeout)

    def __len__(self):
        return Queue.Queue.qsize(self)

    def pop(self, block=True, timeout=None):
        return Queue.Queue.get(self, block=block, timeout=timeout)


class RunOnMainThread(object):

    """Type representing an instance of a command."""

    def __init__(
            self,
            func_from_other_thread=None,
            args_to_func=((), {}),
            call_back_on_other_thread=None):
        self.func_from_other_thread = func_from_other_thread
        self.args_to_func = args_to_func
        self.call_back_on_other_thread = call_back_on_other_thread

    def run(self):
        '''
        will execute:

        ret_value = func_from_other_thread(*args_to_func[0], **args_to_func[1])
        call_back_on_other_thread(ret_value)

        on the callee's thread.
        '''
        ret_value = None
        if self.func_from_other_thread is not None:
            ret_value = self.func_from_other_thread(*self.args_to_func[0], **self.args_to_func[1])
        if self.call_back_on_other_thread is not None:
            self.call_back_on_other_thread(ret_value)


def profile_main(cmd):
    import cProfile
    import pstats
    import os

    cProfile.run(cmd, "profileRes.txt")
    p = pstats.Stats("profileRes.txt")
    p.sort_stats('cumulative').print_stats()
    os.remove("profileRes.txt")
