from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url('^$', views.StaffList.as_view(),name="staff-list"),
)
