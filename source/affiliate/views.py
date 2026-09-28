from django.shortcuts import render
from ..authentication.decorators import authenticated


@authenticated
def page_affiliate(request):
    return render(request, "affiliate.html")


@authenticated
def page_dashboard(request):
    return render(request, "affiliate_dashboard.html")

@authenticated
def page_affiliate_terms(request):
    return render(request, "terms.html")
