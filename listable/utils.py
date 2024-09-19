import importlib
import re
from urllib.parse import unquote

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
    if hasattr(view_func, "view_class"):
        return getattr(module, view_func.view_class.__name__)
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


def unquote_unicode(string, encoding='utf-8'):
    """
    Unquote and decode Unicode characters, handling surrogate pairs and
    standalone Unicode characters.

    (I wish I could claim I wrote this myself but it was primarily written by
    ChatGPT with *a lot* of coaching from me.)
    """
    string = unquote(string, encoding=encoding)

    def decode_surrogate_pair(match):
        """Decodes a surrogate pair into a single Unicode character."""
        high_surrogate = int(match.group(1), 16)
        low_surrogate = int(match.group(2), 16)
        combined_codepoint = ((high_surrogate - 0xD800) * 0x400) + (low_surrogate - 0xDC00) + 0x10000
        return chr(combined_codepoint)

    def decode_single_unicode_escape(match):
        """Decodes a single %uXXXX sequence."""
        codepoint = int(match.group(1), 16)
        return chr(codepoint)

    # First, decode all surrogate pairs into their corresponding Unicode characters
    string = re.sub(r'%u(D[89A-B][0-9A-F]{2})%u(DC[0-9A-F]{2})', decode_surrogate_pair, string)

    # Then, decode all remaining %uXXXX sequences (including standalone characters and variation selectors)
    string = re.sub(r'%u([a-fA-F0-9]{4})', decode_single_unicode_escape, string)

    # Finally, decode any remaining %XX sequences (e.g., regular URL-encoded characters)
    string = re.sub(r'%([a-fA-F0-9]{2})', lambda m: chr(int(m.group(1), 16)), string)

    # Ensure any remaining surrogate pairs in the string are combined into full characters
    def combine_remaining_surrogates(s):
        result = []
        i = 0
        while i < len(s):
            # Check for a high surrogate
            if 0xD800 <= ord(s[i]) <= 0xDBFF and i + 1 < len(s):
                high_surrogate = ord(s[i])
                low_surrogate = ord(s[i + 1])
                if 0xDC00 <= low_surrogate <= 0xDFFF:
                    # Combine into a single character
                    combined_codepoint = ((high_surrogate - 0xD800) * 0x400) + (low_surrogate - 0xDC00) + 0x10000
                    result.append(chr(combined_codepoint))
                    i += 2  # Skip the low surrogate as it's been combined
                    continue
            result.append(s[i])
            i += 1
        return ''.join(result)

    # Apply the final surrogate combination pass
    return combine_remaining_surrogates(string)
