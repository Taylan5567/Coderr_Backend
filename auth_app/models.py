from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=User.types, default='customer')

    types = [
        ('business', 'Business'),
        ('customer', 'Customer'),
    ]

    def __init__(self, username, email, password, type):
        self.username = username
        self.email = email
        self.password = password
        self.type = type
    
    def __str__(self):
        return self.username