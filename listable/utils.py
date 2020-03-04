import importlib

from django.urls import reverse, resolve, get_script_prefix
import django.db.models.fields

BOOL_TYPE = django.db.models.fields.BooleanField().get_internal_type()


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


def lookup_dunder_prop(obj, props, multi=False):
    """
    Take an obj and lookup the value of a related attribute
    using __ notation.

    For example if Obj.a.b.c == "foo" then lookup_dunder (Obj, "a__b__c") == "foo"
    """
    try:
        if "__" in props:
            head, tail = props.split("__", 1)
            obj = getattr(obj, head)
            return lookup_dunder_prop(obj, tail, multi=multi)
        if multi:
            return [getattr(o, props) for o in obj.all()]
        return getattr(obj, props)
    except AttributeError:
        return None


def class_for_view_name(view_name, args=None, kwargs=None):
    """ return View class for input view_name
    see http://stackoverflow.com/a/21313506/79802
    """

    reverse_ = reverse(view_name, args=args, kwargs=kwargs)
    if reverse_ and reverse_[0] != "/":
        reverse_ = "/%s" % reverse_

    prefix = get_script_prefix()
    view_func = resolve(reverse_.replace(prefix, "/", 1)).func
    module = importlib.import_module(view_func.__module__)
    return getattr(module, view_func.__name__)


def find_field(cls, lookup):
    """Take a root class and a field lookup string
    and return the model field if it exists or raise
    a django.db.models.fields.FieldDoesNotExist if the
    field is not found."""

    lookups = list(reversed(lookup.split("__")))

    field = None

    while lookups:

        f = lookups.pop()

        # will raise FieldDoesNotExist exception if not found
        field = cls._meta.get_field(f)

        try:
            cls = field.rel.to
        except AttributeError:
            if lookups:
                # not all lookup fields were used
                # must be an incorrect lookup
                raise django.db.models.fields.FieldDoesNotExist(lookup)

    return field

