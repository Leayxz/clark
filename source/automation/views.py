from django.shortcuts import render
from ..authentication.decorators import authenticated


@authenticated
def page_automation(request):
    return render(request, "automation.html")
