from django.urls import path
from . import views

urlpatterns = [
    path("", views.onboarding, name="onboarding"),
    path("onboarding/", views.onboarding, name="onboarding_alias"),
]
