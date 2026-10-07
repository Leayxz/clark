from . import views, api
from django.urls import path

urlpatterns = [
    path("operations/", views.page_operations, name="operations"),
    path("api/v1/operations", api.operations_overview, name="operations_overview"),
]
