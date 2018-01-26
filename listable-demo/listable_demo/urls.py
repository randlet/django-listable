from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^', include('staff.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
