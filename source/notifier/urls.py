from django.urls import path
from . import views, api

urlpatterns = [
    path("telegram/", views.page_telegram, name="page_telegram"),
    path("api/v1/notifier/telegram", api.get_save_notifier, name="save_notifier"),
]
