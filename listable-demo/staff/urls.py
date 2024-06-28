from django.urls import path
from . import views

urlpatterns = [
    path('staff-list/', views.StaffList.as_view(), name="staff-list"),
    path(
        'staff-list-live-filters/',
        views.StaffListWithLiveFilters.as_view(),
        name="staff-list-live-filters",
    ),
]
