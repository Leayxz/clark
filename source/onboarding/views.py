from django.shortcuts import render


def onboarding(request):
    return render(request, "onboarding.html")
