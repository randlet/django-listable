from django.conf.urls import patterns, include, url
from django.views.generic import View
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url("foo/$", View.as_view(), name="foo"),
    url(r'^', include('staff.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
