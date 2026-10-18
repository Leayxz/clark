from django.shortcuts import render

from ..telemetry.metrics import page_views


def onboarding(request):
    page_views.add(1, {"route": "/"})
    return render(request, "onboarding.html")
