from django.urls import path
from . import views

urlpatterns = [
    path('staff-list/', views.StaffList.as_view(), name="staff-list"),
    path(
        'staff-list-live-filters/',
        views.StaffListLiveFilters.as_view(),
        name="staff-list-live-filters",
    ),
    path(
        'staff-list-static-live-filters/',
        views.StaffListStaticLiveFilters.as_view(),
        name="staff-list-static-live-filters",
    ),
]
