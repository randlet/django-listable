import json

from django import template
from django.core.urlresolvers import reverse
from django.templatetags.static import static

from .. import utils
from .. views import SELECT, TEXT
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
        '<link href="{0}" rel="stylesheet">'.format(static('listable/css/jquery.dataTables.css')),
        '<link href="{0}" rel="stylesheet">'.format(static('listable/css/jquery.dataTables.bootstrap.css'))
    ])


@register.simple_tag
def listable_js():
    return '\n'.join(DATATABLES_SCRIPTS)


def values_to_dt(values):
    return [{"value": str(x[0]), "label": x[1]} for x in utils.unique(values)]


@register.filter(name="header")
def header(value):
    return value.replace("__", " ").replace("_", " ").title()


@register.simple_tag
def listable(view_name, save_state=False, css_table_class="", css_input_class=""):

    cls = utils.class_for_view_name(view_name)
    mdl = cls.model

    column_defs = []
    column_filter_defs = []

    for field in cls.fields:

        # column ordering def for datatablse
        order_allowed = cls.order_fields.get(field, True)
        column_defs.append({"bSortable": False} if not order_allowed else None)

        # column filters
        filter_allowed = cls.search_fields.get(field, True)
        widget_type = cls.widgets.get(field, TEXT)

        if not filter_allowed:
            column_filter_defs.append(None)
        elif widget_type == TEXT:
            column_filter_defs.append({"type": "text"})
        elif widget_type == SELECT:
            is_local = field in [f.name for f in mdl._meta.fields]
            choices = cls.model._meta.get_field(field).choices if is_local else None

            if is_local and choices:
                # local field with choices defined
                values = values_to_dt(choices)
            else:
                values = values_to_dt(cls.model.objects.values_list(field, field).order_by(field))
            column_filter_defs.append({"type": "select", "values": values})
        else:
            raise TypeError("{wt} is not a valid widget type".format(wt=widget_type))

    opts = {
        "tableId": "#listable-table-"+view_name,
        "paginationType": settings.LISTABLE_PAGINATION_TYPE,
        "stateSave": settings.LISTABLE_STATE_SAVE,
        "url": reverse(view_name),
        "bProcessing": True,
        "autoWidth": True,
        "DOM": settings.LISTABLE_DOM,
        "columnDefs": column_defs,
        "columnFilterDefs": column_filter_defs,
        "cssTableClass": css_table_class,
        "cssInputClass": css_input_class,
    }

    scripts = ['<script type="text/javascript">var Listable = {0};</script>'.format(json.dumps(opts))]
    scripts += DATATABLES_SCRIPTS
    scripts += ['<script src="{0}" type="text/javascript"></script>'.format(static('listable/js/listable.js'))]

    return "\n".join(scripts)
