from django.db import models
from userprofile_app.models import UserProfile


class Offer(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='uploads/', null=True, blank=True)
    description = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class OfferDetail(models.Model):
    OFFER_TYPE=(
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.IntegerField()
    features = models.JSONField()
    offer_type = models.CharField(max_length=255, choices=OFFER_TYPE)

    def __str__(self):
        return self.title



    
