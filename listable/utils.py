import importlib

from django.core.urlresolvers import reverse, resolve

def unique(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]


def class_for_view_name(view_name):
    """ return View class for input view_name
    see http://stackoverflow.com/a/21313506/79802
    """
    view_func = resolve(reverse(view_name)).func
    module = importlib.import_module(view_func.__module__)
    return getattr(module, view_func.__name__)


def column_filter_model(column):
    return column.filtering[:column.filtering.rindex("__")]
