from . import api, views
from django.urls import path


urlpatterns = [
    path("", views.page_login, name="page_login"),
    path("register/", views.page_register, name="page_register"),

    path("api/v1/login", api.authenticate, name="authenticate"),
    path("api/v1/register", api.register, name="register"),
    path("api/v1/logout", api.logout, name="logout"),
]
