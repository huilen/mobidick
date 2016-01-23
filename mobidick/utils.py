import sys
import json
import logging
import getopt
import pickle
import importlib


logger = logging.getLogger(__name__)


def memoized(path):
    def memoize(fn):
        def memoize_wrapper(*args, **kwargs):
            try:
                with open(path, 'rb') as file:
                    logger.info("Loading pickle %s", path)
                    data = pickle.load(file)
            except (FileNotFoundError, EOFError):
                data = fn(*args, **kwargs)
                with open(path, 'wb') as file:
                    pickle.dump(data, file)
            return data
        return memoize_wrapper
    return memoize


def configuration(argv):
    opts, args = getopt.getopt(
        argv, 's:', ['settings='])
    for opt, arg in opts:
        if opt in ('-s', '--settings'):
            with open(arg) as config:
                return json.load(config)
    raise ValueError("Must specify --settings")


def print_progress(completed, total, message=None):
    if completed != total and completed != 1:
        if completed % 1000 != 0:
            return
    percentage = completed / total * 100
    sys.stdout.write("\r{completed}/{total} ({percentage}%)".format(
        completed=completed, total=total, percentage=int(percentage)))
    if message:
        sys.stdout.write(" " + message)
    if completed == total:
        sys.stdout.write("\r")
    sys.stdout.flush()


def load_class(path):
    module, class_name = path.rsplit('.', 1)
    module = importlib.import_module(module)
    return getattr(module, class_name)
