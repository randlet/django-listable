import datetime
import json
import urllib

from collections import namedtuple

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils import formats
from django.views.generic import ListView

Column = namedtuple('Column', ['field', 'filtering', 'ordering'])

class BaseListableView(ListView):
    columns = ()
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        if not self.request.is_ajax():
            return super(BaseListableView, self).get(request, *args, **kwargs)

        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                        % {'class_name': self.__class__.__name__})

        context = self.get_table_context_data()
        return HttpResponse(json.dumps(context), content_type='application/json')


    def get_table_context_data(self):

        self.set_page()

        context = super(BaseListableView, self).get_context_data()

        object_list = context["object_list"]

        context = {
            "aaData": self.get_rows(object_list),
            "iTotalRecords": super(BaseListableView, self).get_queryset().count(),
            "iTotalDisplayRecords": self.object_list.count(),
            "sEcho": int(self.search_filters.get("sEcho")),
        }
        return context

    def get_context_data(self, *args, **kwargs):

        context = super(BaseListableView, self).get_context_data(*args, **kwargs)
        template = get_template("listable/_table.html")

        tmpl_context = Context({ 'headers':self.headers(), })
        context['listable_table'] = template.render(tmpl_context)
        return context

    def headers(self):
        if not self.columns:
            raise ValueError("Columns not set on Listable view")

        headers = []
        for col in self.columns:
            attr_name = "%s_column_name" % col.field
            if hasattr(self, attr_name):
                header = getattr(self, attr_name)()
            else:
                header = col.field.title()
            headers.append(header)

        return headers

    def set_page(self):
        offset = int(self.search_filters.get("iDisplayStart", 0))
        page_size = self.get_paginate_by(self.object_list)
        self.kwargs[self.page_kwarg] = offset/page_size + 1

    def get_paginate_by(self, queryset):
        return int(self.search_filters.get("iDisplayLength", self.paginate_by))

    def get_queryset(self):
        qs = super(BaseListableView, self).get_queryset()
        self.set_query_params()
        qs = self.filter_queryset(qs)
        qs = self.order_queryset(qs)
        return qs

    def filter_queryset(self, qs):
        return qs

    def order_queryset(self, qs):
        return qs

    def get_rows(self, objects):
        rows = []
        for obj in objects:
            rows.append([self.format_col(col.field, obj) for col in self.columns])
        return rows

    def format_col(self, field, obj):

        # first see if subclass has a formatter defined
        formatter = getattr(self,field, None)
        if formatter:
            return formatter(obj) if callable(formatter) else formatter


        # then look on object itself
        attr = getattr(obj, field, None)

        if attr is None:
            raise ValueError("'%s' is not a valid format specifier" % (attr))

        if callable(attr):
            return attr()
        elif isinstance(attr, datetime.datetime):
            return formats.date_format(val, "SHORT_DATETIME_FORMAT")
        elif isinstance(attr, datetime.date):
            return formats.date_format(val, "SHORT_DATE_FORMAT")

        return str(attr)

    def set_query_params(self):
        """
        Create a search and filter context, overridng any cookie values
        with request values.  This is required when "Sticky" DataTables filters
        are used.
        """

        self.search_filters = self.get_cookie_filters()

        self.search_filters.update(self.request.GET.dict())

    def get_cookie_filters(self):

        filters = {}
        dt_cookie = None

        for k, v in self.request.COOKIES.items():
            if k.startswith("SpryMedia_DataTables"):
                dt_cookie = v
                break

        if dt_cookie is None:
            return filters

        cookie_filters = json.loads(urllib.unquote(v))

        for idx, search in enumerate(cookie_filters["aoSearchCols"]):
            for k, v in search.items():
                filters["%s_%d" % (k, idx)] = v

        filters["iSortingCols"] = 0
        for idx, (col, dir_, _) in enumerate(cookie_filters["aaSorting"]):
            filters["iSortCol_%d" % (idx)] = col
            filters["sSortDir_%d" % (idx)] = dir_
            filters["iSortingCols"] += 1

        filters["iDisplayLength"] = cookie_filters["iLength"]
        filters["iDisplayStart"] = cookie_filters["iStart"]
        filters["iDisplayEnd"] = cookie_filters["iEnd"]

        return filters

