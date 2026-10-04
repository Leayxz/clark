from . import api, views
from django.urls import path


urlpatterns = [
    path("dashboard/", views.page_dashboard, name="home_dashboard"),
    path("api/v1/dashboard", api.overview, name="overview"),
    path("api/v1/dashboard/period", api.overview_period, name="overview_period"),
    path("api/v1/dashboard/goal", api.update_goal_target, name="update_goal"),
]
