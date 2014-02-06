import json

from django import template
from django.core.urlresolvers import reverse
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def listable_css():
    return '\n'.join([
        '<link href="%s" rel="stylesheet">'% (static('listable/css/jquery.dataTables.css')),
        '<link href="%s" rel="stylesheet">'% (static('listable/css/jquery.dataTables.bootstrap.css'))
    ])


@register.simple_tag
def listable(url):
    opts = {
        "tableId":"#listable-table",
        "paginationType":"bootstrap",
        "url":reverse(url),
        "autoWidth":True,
        "DOM": '<"row-fluid"<"span6"ir><"span6"p>>t<"row-fluid"<"span12"lp>>',
        "columnDefs":[],
        "columnFilterDefs":[],
    }
    scripts = [
        '<script type="text/javascript">var Listable = %s;</script>' % (json.dumps(opts), ),
        '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.js'),
        '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.columnFilter.js'),
        '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.searchPlugins.js'),
        '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.bootstrap.js'),
        '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.sort.js'),
        '<script src="%s" type="text/javascript"></script>' % static('listable/js/listable.js'),
    ]
    return "\n".join(scripts)


