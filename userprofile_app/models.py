from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    objects = UserManager()
    TYPE_CHOICES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )

    email = models.EmailField(max_length=255, blank=True)
    file = models.FileField(upload_to="uploads/", null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    working_hours = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="customer")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username 
