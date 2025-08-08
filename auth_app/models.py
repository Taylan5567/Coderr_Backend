from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    TYPE_CHOICES = [
        ('business', 'Business'),
        ('customer', 'Customer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='customer')
    
    fields_to_display = ['username', 'email', 'password', 'type']


    def __str__(self):
        return self.username