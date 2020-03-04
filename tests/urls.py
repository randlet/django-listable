from django.conf.urls import include, url
from django.views.generic import View
from django.contrib import admin

import sys
sys.path.append("listable_demo")
from staff import urls as staff_urls

admin.autodiscover()

urlpatterns = [
    url("foo/$", View.as_view(), name="foo"),
    url(r'^', include(staff_urls)),
    url(r'^admin/', admin.site.urls),
]
