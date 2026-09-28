from django.urls import path
from . import views
from . import api

urlpatterns = [
    path("affiliate/", views.page_affiliate, name="page_affiliate"),
    path("affiliate/overview/", views.page_overview, name="page_overview"),
    path("affiliate/terms/", views.page_affiliate_terms, name="page_affiliate_terms"),
    path("api/v1/affiliates/register", api.register_affiliate, name="api_affiliate_register"),
    path("api/v1/affiliates/validate", api.validate_affiliate, name="api_affiliate_validate"),
]
