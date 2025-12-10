from django.db import models
from django.contrib.auth.models import User

class InvoicesPagos(models.Model):

      user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'invoices_pagos')
      id_invoice = models.TextField()
      timestamp = models.FloatField()
      status = models.BooleanField(default = False)
