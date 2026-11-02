from django.shortcuts import render

from ..authentication.decorators import authenticated
from ..constants import Automation


@authenticated
def page_payment(request):
    return render(request, "payment.html", {
        "price_full": Automation.FULL_PRICE_IN_BRL,
        "price_discounted": Automation.DISCOUNT_PRICE_IN_BRL,
    })
