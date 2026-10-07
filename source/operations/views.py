from django.shortcuts import render
from ..authentication.decorators import authenticated


@authenticated
def page_operations(request):
    return render(request, "operations.html")
