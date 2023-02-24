from django.conf.urls import include
from django.urls import path
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    path('', include('staff.urls')),
    path('admin/', admin.site.urls),
]
