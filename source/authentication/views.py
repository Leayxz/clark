from django.shortcuts import render

def page_register(request):
    return render(request, "register.html")


def page_login(request):
    return render(request, "login.html")
