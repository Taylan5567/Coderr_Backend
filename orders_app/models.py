from django.db import models
from userprofile_app.models import UserProfile
from offers_app.models import OfferDetail



class Order(models.Model):
    """
    A single purchase of an OfferDetail, with snapshot fields.

    Fields:
        customer_user (FK UserProfile): Buyer of the order.
        business_user (FK UserProfile): Owner of the offer (seller).
        offer_detail (FK OfferDetail): Variant used to create this order.
        title (str): Snapshot of the offer detail title at creation time.
        revisions (int): Snapshot of how many revisions are included.
        delivery_time_in_days (int): Snapshot of promised delivery time (days).
        price (int): Snapshot of the price at creation time.
        features (JSON list): Snapshot of included features.
        offer_type (str): Snapshot of the variant type (basic/standard/premium).
        status (str): Current status of the order.
        created_at (datetime): When the order was created.
        updated_at (datetime): When the order was last updated.
    """
    
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled")
    ]



    customer_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders_as_customer')
    business_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders_as_business')
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name='orders')
    title = models.CharField(max_length=255, default="")
    revisions = models.PositiveIntegerField(default=1)
    delivery_time_in_days = models.PositiveIntegerField(default=1)
    price = models.IntegerField(default=0)
    features = models.JSONField(default=list, blank=True)  
    offer_type = models.CharField(max_length=50, choices=OfferDetail.OFFER_TYPE, default='basic') 

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title