import json

from django import template
from django.core.urlresolvers import reverse
from django.templatetags.static import static

from .. import utils
from .. views import SELECT
from .. import settings

register = template.Library()


@register.simple_tag
def listable_css():
    return '\n'.join([
        '<link href="%s" rel="stylesheet">'% (static('listable/css/jquery.dataTables.css')),
        '<link href="%s" rel="stylesheet">'% (static('listable/css/jquery.dataTables.bootstrap.css'))
    ])



def values_to_dt(values):
    return [{"value":str(x[0]), "label":x[1]} for x in utils.unique(values)]


@register.simple_tag
def listable(view_name, save_state=False):

    cls = utils.class_for_view_name(view_name)
    mdl = cls.model

    column_defs = []
    column_filter_defs = []
    for column in cls.columns:

        #colum ordering
        column_defs.append({"bSortable":False} if not column.ordering else None)

        # column filters
        if isinstance(column.filtering, basestring) and column.widget==SELECT:

            if "__" in column.filtering:
                # foreign key select widget (select by pk)
                filtering = "%s__pk" % utils.column_filter_model(column)
            else:
                # local field select widget
                filtering = column.filtering

            values = values_to_dt(cls.model.objects.values_list(filtering, column.filtering).order_by(column.filtering))
            column_filter_defs.append({"type":"select", "values":values})
        elif column.filtering:
            column_filter_defs.append({"type":"text"})
        else:
            column_filter_defs.append(None)

    opts = {
        "tableId":"#listable-table",
        "sPaginationType":settings.LISTABLE_PAGINATION_TYPE,
        "stateSave":settings.LISTABLE_STATE_SAVE,
        "url": reverse(view_name),
        "bProcessing":True,
        "autoWidth":True,
        "DOM": settings.LISTABLE_DOM,
        "columnDefs":column_defs,
        "columnFilterDefs":column_filter_defs,
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


