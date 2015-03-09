import threading

from indexer import Indexer
from utilities.util import TQueue, RunOnMainThread, profile_main
import utilities.tselogging as logging
from searchEngine.models import IndexedPage, WordFromIndexedPage

logger = logging.getLogger("tse.se.crawler")


class Crawler(threading.Thread):

    """Class representing a single instance of a crawler."""

    POP_TIMEOUT_IN_SECONDS = 1000

    def __init__(
            self,
            max_links_to_crawl=100,
            max_active_indexers=5,
            links_queue=TQueue(["google.com"]),  # passed to indexers to populate.
            main_thread_cmd_queue=TQueue()):  # passed to indexers: commands to run on main thread
        threading.Thread.__init__(self)

        self.max_links_to_crawl = max(max_links_to_crawl, 1)
        self.max_active_indexers = max(max_active_indexers, 1)
        self.links_queue = links_queue
        self.main_thread_cmd_queue = main_thread_cmd_queue

        self.finished_indexers_list = []
        self.number_of_non_trivial_indexes = 0
        self.current_count_of_indexers = 0

    def create_new_indexer(self):
        candidate_link = self.links_queue.pop(timeout=Crawler.POP_TIMEOUT_IN_SECONDS)
        candidate_indexedPage, was_create = IndexedPage.objects.get_or_create(pk=candidate_link)
        if was_create:
            Indexer(indexed_page=candidate_indexedPage,
                    on_finished_indexing=self.on_indexer_finished,
                    main_thread_cmd_queue=self.main_thread_cmd_queue,
                    links_queue=self.links_queue).start()
            return True
        else:
            logger.info("Skipping {url}. Index already exists".format(url=candidate_link))
            return False

    def on_indexer_finished(self, *args):
        """Call back called from an indexer when it just finished it's
        execution."""

        # Book-keeping.

        # Let's decrease the counter of current active indexers.
        self.current_count_of_indexers -= 1

        # Log something hopeful.
        indexed_url = args[0]
        self.number_of_non_trivial_indexes += not args[1]
        self.finished_indexers_list.append(indexed_url)
        percentage_complete = \
            self.number_of_non_trivial_indexes / (0.01 * self.max_links_to_crawl)
        logger.info("Logging of {url} finished!".format(url=indexed_url))
        logger.info("CRAWLING NOW {perc}% COMPLETE!!".format(perc=int(percentage_complete)))

        # Now, let's replace the complete indexer(s)
        if self.number_of_non_trivial_indexes <= self.max_links_to_crawl:
            while self.current_count_of_indexers < self.max_active_indexers:
                self.current_count_of_indexers += self.create_new_indexer()

    def run(self):
        """
        Called when Crawler.start() is invoked.

        Starts up at-least 1 indexer, then goes into the listening phase.

        During the listening phase, this crawler will keep waiting for commands from
        indexers and keep applying them, as long as some crawling is still needed.

        """

        # Start atleast 1 non trivial indexing. The hope is, it
        while not self.create_new_indexer():
            pass

        # Start listening for commands.
        while self.number_of_non_trivial_indexes <= self.max_links_to_crawl:
            write_cmd = self.main_thread_cmd_queue.pop(timeout=Crawler.POP_TIMEOUT_IN_SECONDS)
            if isinstance(write_cmd, RunOnMainThread):
                write_cmd.run()
            else:
                logger.warn("Main thread received a command it couldn't parse: ", write_cmd)

        # Crawling complete. Hola the team!
        logger.info(
            "Crawling complete. Logged: {n_urls}".format(
                n_urls=len(
                    self.finished_indexers_list)))


def main():
    #[x.delete() for x in list(IndexedPage.objects.all()) + list(WordFromIndexedPage.objects.all())]
    crawler = Crawler(
        links_queue=TQueue(
            ["https://www.facebook.com"]),
        max_active_indexers=10,
        max_links_to_crawl=50)
    #crawler.start()
    #crawler.join()
    crawler.run()
    logger.info("Crawling complete!")

if __name__ == '__main__':
    profile_main()
