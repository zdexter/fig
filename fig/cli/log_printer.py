from __future__ import unicode_literals
from __future__ import absolute_import
import sys

from fig.packages.six.moves import zip
from itertools import cycle, repeat

from .multiplexer import Multiplexer, STOP
from . import colors
from .utils import split_buffer


def calculate_prefix_width(containers):
    """
    Calculate the maximum width of container names so we can make the log
    prefixes line up like so:

    db_1  | Listening
    web_1 | Listening
    """
    return max(len(container.name_without_project) for container in containers)


def get_color_generator(monochrome):
    return repeat(lambda s: s) if monochrome else cycle(colors.rainbow())


def format_prefix(container, width):
    """Format the container name as a prefix for a log line.
    """
    return "%s | " % container.name_without_project.ljust(width)


def run_printer(generators, output=sys.stdout):
    mux = Multiplexer(generators)
    for line in mux.loop():
        output.write(line)


def build_log_generators(containers, monochrome=False):
    if not containers:
        return []

    prefix_width = calculate_prefix_width(containers)
    color_funcs = get_color_generator(monochrome)

    def make_log_generator(container, color_fn):
        prefix = color_fn(
            format_prefix(container, prefix_width)).encode('utf-8')

        # Attach to container before log printer starts running
        # TODO: is split_buffer still necessary
        for line in split_buffer(container.attach(stream=True, logs=True)):
            yield prefix + line

        exit_code = container.wait()
        yield color_fn("%s exited with code %s\n" % (container.name, exit_code))
        yield STOP

    return [make_log_generator(*item) for item in zip(containers, color_funcs)]
