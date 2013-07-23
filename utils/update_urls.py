import pandas as pd
import requests
from Queue import Queue
from threading import Thread
import logging

log = logging.getLogger(__name__)


def threaded(items, func, num_threads=5, max_queue=200):
    def queue_consumer():
        while True:
            try:
                item = queue.get(True)
                func(item)
            except Exception, e:
                log.exception(e)
            except KeyboardInterrupt:
                raise
            except:
                pass
            finally:
                queue.task_done()

    queue = Queue(maxsize=max_queue)

    for i in range(num_threads):
        t = Thread(target=queue_consumer)
        t.daemon = True
        t.start()

    for item in items:
        queue.put(item, True)

    queue.join()