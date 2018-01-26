from django.conf.urls import url
from . import views

urlpatterns = [
    url('staff-list/$', views.StaffList.as_view(), name="staff-list"),
]
