from __future__ import absolute_import
from threading import Thread

from fig.packages.six.moves import queue


# Yield STOP from an input generator to stop the
# top-level loop without processing any more input.
STOP = object()


class Multiplexer(object):

    def __init__(self, generators):
        self.generators = generators
        self.queue = queue.Queue()

    def loop(self):
        self._init_readers()
        finished = 0

        while finished < len(self.generators):
            try:
                item = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if item is STOP:
                finished += 1
            else:
                yield item

    def _init_readers(self):
        for generator in self.generators:
            t = Thread(target=_enqueue_output, args=(generator, self.queue))
            t.daemon = True
            t.start()


def _enqueue_output(generator, queue):
    for item in generator:
        queue.put(item)
