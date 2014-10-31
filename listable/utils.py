import importlib

from django.core.urlresolvers import reverse, resolve


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


def lookup_dunder_prop(obj, props):
    """
    Take an obj and lookup the value of a related attribute
    using __ notation.

    For example if Obj.a.b.c == "foo" then lookup_dunder (Obj, "a__b__c") == "foo"
    """

    if "__" in props:
        head, tail = props.split("__", 1)
        obj = getattr(obj, head)
        return lookup_dunder_prop(obj, tail)

    return getattr(obj, props)


def class_for_view_name(view_name, args=None, kwargs=None):
    """ return View class for input view_name
    see http://stackoverflow.com/a/21313506/79802
    """

    reverse_ = reverse(view_name, args=args, kwargs=kwargs, prefix="")
    if reverse_ and reverse_[0] != "/":
        reverse_ = "/%s" % reverse_

    view_func = resolve(reverse_).func
    module = importlib.import_module(view_func.__module__)
    return getattr(module, view_func.__name__)
