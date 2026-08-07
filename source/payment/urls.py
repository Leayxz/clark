from django.urls import path
from . import api

urlpatterns = [
    path("api/v1/payment/create/sats", api.generate_qrcode_in_sats, name="generate_qrcode_in_sats"),
    path("api/v1/payment/create/pix", api.generate_qrcode_in_pix, name="generate_qrcode_in_pix"),
]
