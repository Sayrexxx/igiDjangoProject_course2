from django.db import models
from django.contrib.auth.models import User

class MyUserLibModel(User):
    ROLE_CHOICES = (
        ("administrator", "administrator"),
        ("passenger", "passenger"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="passenger")
    phone_number = models.CharField(max_length=13)
    age = models.PositiveSmallIntegerField(default=30)
    secret_key = models.CharField(max_length=20, default='')

    user_ptr = models.OneToOneField(User, on_delete=models.CASCADE, parent_link=True, primary_key=True, default=None)

    def __str__(self):
        return self.username
