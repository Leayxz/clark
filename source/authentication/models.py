from django.db import models


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    hashed_password = models.TextField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
