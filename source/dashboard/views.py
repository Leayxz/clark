from django.shortcuts import render
from ..authentication.decorators import authenticated


@authenticated
def page_dashboard(request):
    return render(request, "dashboard.html")
