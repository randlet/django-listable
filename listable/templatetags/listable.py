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
def listable_js(): #pragma: nocover
    return '\n'.join(DATATABLES_SCRIPTS)


def values_to_dt(values):
    return [{"value": str(x[0]), "label": x[1]} for x in utils.unique(values)]


@register.filter(name="header")
def header(value):
    return value.replace("__", " ").replace("_", " ").title()

def get_dt_ordering(cls):

    orderings = []

    for idx, field in enumerate(cls.order_by):
        if field[0] == '-':
            direction = "desc"
            field=field[1:]
        else:
            direction = "asc"

        try:
            orderings.append([cls.fields.index(field), direction])
        except (ValueError, IndexError):
            raise ValueError("The field '{field}' is an invalid listable order_by value. It is not present in the listable fields definition.".format(field=field))


    return orderings


def get_options(context, view_name, dom="", save_state=None, pagination_type="", css_table_class="", css_input_class=""):

    view_args = context.get('args', None)
    view_kwargs = context.get('kwargs', None)

    if save_state is None:
        save_state = settings.LISTABLE_STATE_SAVE

    if dom is "":
        dom = settings.LISTABLE_DOM

    if pagination_type is "":
        pagination_type = settings.LISTABLE_PAGINATION_TYPE

    cls = utils.class_for_view_name(view_name, args=view_args, kwargs=view_kwargs)
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

    url = reverse(view_name, args=view_args, kwargs=view_kwargs)

    opts = {
        "tableId": "#listable-table-" + view_name.replace(":","_"),
        "paginationType": pagination_type,
        "stateSave": save_state,
        "url": url,
        "bProcessing": True,
        "autoWidth": True,
        "displayLength": cls.paginate_by,
        "DOM": dom,
        "order": get_dt_ordering(cls),
        "columnDefs": column_defs,
        "columnFilterDefs": column_filter_defs,
        "cssTableClass": css_table_class,
        "cssInputClass": css_input_class,
    }

    return opts


@register.simple_tag(takes_context=True)
def listable(context, view_name, dom="", save_state=None, pagination_type=None, css_table_class="", css_input_class=""):
    """ Generate all script tags and DataTables options for a given table"""


    opts = get_options(context, view_name, dom, save_state, pagination_type, css_table_class, css_input_class)

    scripts = ['<script type="text/javascript">var Listable = {0};</script>'.format(json.dumps(opts))]
    scripts += DATATABLES_SCRIPTS
    scripts += ['<script src="{0}" type="text/javascript"></script>'.format(static('listable/js/listable.js'))]

    return "\n".join(scripts)
