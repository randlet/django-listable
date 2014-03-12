import json

from django import template
from django.core.urlresolvers import reverse
from django.templatetags.static import static

from .. import utils
from .. views import SELECT
from .. import settings

register = template.Library()

DATATABLES_SCRIPTS = [
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.columnFilter.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.searchPlugins.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.bootstrap.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.sort.js'),
]

@register.simple_tag
def listable_css():
    return '\n'.join([
        '<link href="%s" rel="stylesheet">'% (static('listable/css/jquery.dataTables.css')),
        '<link href="%s" rel="stylesheet">'% (static('listable/css/jquery.dataTables.bootstrap.css'))
    ])

@register.simple_tag
def listable_js():
    return '\n'.join(DATATABLES_SCRIPTS)


def values_to_dt(values):
    return [{"value":str(x[0]), "label":x[1]} for x in utils.unique(values)]


@register.filter(name="header")
def header(value):
    return value.title().replace("__"," ").replace("_", " ")

@register.simple_tag
def listable(view_name, save_state=False, css_table_class="", css_input_class=""):

    cls = utils.class_for_view_name(view_name)
    mdl = cls.model

    column_defs = []
    column_filter_defs = []
    for column in cls.columns:

        #colum ordering
        column_defs.append({"bSortable":False} if not column.ordering else None)

        # column filters
        if column.widget==SELECT:

            if isinstance(column.filtering, basestring) and "__" in column.filtering:
                # foreign key select widget (select by pk)
                filtering_k = "%s__pk" % utils.column_filter_model(column)
                filtering_v = column.filtering
            elif column.field in [field.name for field in mdl._meta.fields]:
                # local field select widget
                filtering_k = column.field
                filtering_v = column.field
            else:
                filtering_k = column.filtering
                filtering_v = column.filtering

            values = values_to_dt(cls.model.objects.values_list(filtering_k, filtering_v).order_by(filtering_v))
            column_filter_defs.append({"type":"select", "values":values})
        elif column.filtering:
            column_filter_defs.append({"type":"text"})
        else:
            column_filter_defs.append(None)

    opts = {
        "tableId":"#listable-table",
        "paginationType":settings.LISTABLE_PAGINATION_TYPE,
        "stateSave":settings.LISTABLE_STATE_SAVE,
        "url": reverse(view_name),
        "bProcessing":True,
        "autoWidth":True,
        "DOM": settings.LISTABLE_DOM,
        "columnDefs":column_defs,
        "columnFilterDefs":column_filter_defs,
        "cssTableClass":css_table_class,
        "cssInputClass":css_input_class,
    }
    scripts = [ '<script type="text/javascript">var Listable = %s;</script>' % (json.dumps(opts), ), ]
    scripts += DATATABLES_SCRIPTS
    scripts += ['<script src="%s" type="text/javascript"></script>' % static('listable/js/listable.js')]

    return "\n".join(scripts)


