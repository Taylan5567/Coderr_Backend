from django.db import models
from userprofile_app.models import UserProfile
from offers_app.models import OfferDetail

# Create your models here.

STATUS = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

class Order(models.Model):
    
    customer_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders_as_customer')
    business_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders_as_business')
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.PROTECT, related_name='orders')
    title = models.CharField(max_length=255, default="")
    revisions = models.PositiveIntegerField(default=1)
    delivery_time_in_days = models.PositiveIntegerField(default=1)
    price = models.IntegerField(default=0)
    features = models.JSONField(default=list, blank=True)  
    offer_type = models.CharField(max_length=50, choices=OfferDetail.OFFER_TYPE, default='basic') 

    status = models.CharField(max_length=20, choices=STATUS, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title