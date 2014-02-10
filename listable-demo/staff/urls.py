from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url('staff-list/$', views.StaffList.as_view(), name="staff-list"),
)
