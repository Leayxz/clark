from django.shortcuts import render
from ..authentication.decorators import authenticated


@authenticated
def page_telegram(request):
    return render(request, "telegram.html")
