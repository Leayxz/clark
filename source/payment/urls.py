from django.urls import path
from . import api, views

urlpatterns = [
    path("payment/", views.page_payment, name="page_payment"),
    path("api/v1/coupon/validate", api.validate_coupon, name="validate_coupon"),
    path("api/v1/payment/create/pix", api.generate_qrcode_in_pix, name="generate_qrcode_in_pix"),
]
