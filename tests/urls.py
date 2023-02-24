from django.conf.urls import include
from django.urls import path
from django.views.generic import View
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    path("foo/", View.as_view(), name="foo"),
    path('', include('staff.urls')),
    path("admin/", admin.site.urls),
]
