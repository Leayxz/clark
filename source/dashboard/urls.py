from . import api, views
from django.urls import path


urlpatterns = [
    path("dashboard/", views.page_dashboard, name="page_dashboard"),
    path("api/v1/dashboard/", api.dashboard, name="dashboard"),
]
