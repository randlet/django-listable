import json
import importlib

from datetime import datetime
from django import template
from django.core.urlresolvers import reverse, resolve
from django.db.models import FieldDoesNotExist
from django.templatetags.static import static

from .. import utils
from .. views import SELECT, TEXT, SELECT_MULTI, DATE, DATE_RANGE
from .. views import TODAY, THIS_WEEK, THIS_MONTH, THIS_QUARTER, THIS_YEAR
from .. import settings

register = template.Library()

DATATABLES_SCRIPTS = [
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.columnFilter.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.searchPlugins.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.bootstrap.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/jquery.dataTables.sort.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/bootstrap.multiselect.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/bootstrap-datepicker.min.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/moment.min.js'),
    '<script src="%s" type="text/javascript"></script>' % static('listable/js/daterangepicker.js')
]


@register.simple_tag
def listable_css():
    return '\n'.join([
        '<link href="{0}" rel="stylesheet">'.format(static('listable/css/jquery.dataTables.css')),
        '<link href="{0}" rel="stylesheet">'.format(static('listable/css/jquery.dataTables.bootstrap.css')),
        '<link href="{0}" rel="stylesheet">'.format(static('listable/css/bootstrap.multiselect.css')),
        '<link href="{0}" rel="stylesheet">'.format(static('listable/css/bootstrap-datepicker.min.css')),
        '<link href="{0}" rel="stylesheet">'.format(static('listable/css/daterangepicker.css')),
        '<link href="{0}" rel="stylesheet">'.format(static('listable/css/font-awesome.min.css'))
    ])


@register.simple_tag
def listable_js(): #pragma: nocover
    return '\n'.join(DATATABLES_SCRIPTS)


def values_to_dt(values):
    return [{"value": str(x[0]), "label": str(x[1])} for x in utils.unique(values)]


@register.filter(name="header")
def header(value):
    return value.replace("__", " ").replace("_", " ").title()


def get_dt_ordering(cls):

    orderings = []

    for idx, field in enumerate(cls.order_by):
        if field[0] == '-':
            direction = "desc"
            field = field[1:]
        else:
            direction = "asc"

        try:
            orderings.append([cls.fields.index(field), direction])
        except (ValueError, IndexError):
            raise ValueError("The field '{field}' is an invalid listable order_by value. It is not present in the listable fields definition.".format(field=field))

    return orderings


def get_options(context, view_name, dom="", save_state=None, pagination_type="", css_table_class="", css_input_class="", auto_width=True):

    view_args = context.get('args', None)
    view_kwargs = context.get('kwargs', None)
    view_instance = context.get('view', None)

    if save_state is None:
        save_state = settings.LISTABLE_STATE_SAVE

    if not dom:
        dom = settings.LISTABLE_DOM

    if not pagination_type:
        pagination_type = settings.LISTABLE_PAGINATION_TYPE

    cls = utils.class_for_view_name(view_name, args=view_args, kwargs=view_kwargs)
    mdl = cls.model

    column_defs = []
    column_filter_defs = []

    if view_instance:
        qs = view_instance.get_queryset()

        for field in cls.fields:

            # try:
            #     mdl_field = utils.find_field(mdl, field)
            # except django.db.models.fields.FieldDoesNotExist:
            #     mdl_field = None

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

            # elif widget_type == SELECT and mdl_field:
            elif widget_type == SELECT:
                is_local = field in [f.name for f in mdl._meta.fields]
                choices = cls.model._meta.get_field(field).choices if is_local else None

                if is_local and choices:
                    # local field with choices defined
                    values = values_to_dt(choices)
                else:
                    values = values_to_dt(view_instance.get_filters(field, queryset=qs))

                column_filter_defs.append({'type': 'select', 'values': values, 'label': '-----'})

            elif widget_type == SELECT_MULTI:
                is_local = field in [f.name for f in mdl._meta.fields]
                choices = cls.model._meta.get_field(field).choices if is_local else None

                if is_local and choices:
                    # local field with choices defined
                    values = values_to_dt(choices)
                else:
                    values = values_to_dt(view_instance.get_filters(field, queryset=qs))
                column_filter_defs.append({'type': 'select', 'values': values, 'multiple': 'multiple'})

            elif widget_type == DATE_RANGE:

                ranges = cls.date_ranges.get(field, [TODAY, THIS_WEEK, THIS_MONTH, THIS_QUARTER, THIS_YEAR])

                column_filter_defs.append({
                    'type': 'daterange',
                    'ranges': ranges
                })

            elif widget_type == DATE:
                column_filter_defs.append({'type': 'date'})

            else:
                raise TypeError("{wt} is not a valid widget type".format(wt=widget_type))

    url = reverse(view_name, args=view_args, kwargs=view_kwargs)

    opts = {
        "tableId": "#listable-table-" + view_name.replace(":", "_"),
        "paginationType": pagination_type,
        "stateSave": save_state,
        "url": url,
        "bProcessing": True,
        "autoWidth": auto_width,
        "displayLength": cls.paginate_by,
        "DOM": dom,
        "order": get_dt_ordering(cls),
        "columnDefs": column_defs,
        "columnFilterDefs": column_filter_defs,
        "cssTableClass": css_table_class,
        "cssInputClass": css_input_class,
        "cookie": "{0}_listable-table-{1}_".format(settings.DT_COOKIE_NAME, view_name)
    }

    if settings.LISTABLE_LANGUAGE:
        opts.update(language=settings.LISTABLE_LANGUAGE)

    return opts


@register.simple_tag(takes_context=True)
def listable(context, view_name, dom="", save_state=None, pagination_type="", css_table_class="",
             css_input_class="", auto_width=True, requirejs=False):
    """ Generate all script tags and DataTables options for a given table"""

    opts = get_options(context, view_name, dom, save_state, pagination_type, css_table_class, css_input_class, auto_width)

    scripts = ['<script type="text/javascript">var Listable = {0};</script>'.format(json.dumps(opts))]
    if not requirejs:
        scripts += DATATABLES_SCRIPTS
        scripts += ['<script src="{0}" type="text/javascript"></script>'.format(static('listable/js/listable.js'))]

    return "\n".join(scripts)
