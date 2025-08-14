from django.db import models
from userprofile_app.models import UserProfile


class Offer(models.Model):
    """
    Represents a base offer created by a user.

    Relationships:
        user (FK UserProfile, nullable): The owner of this offer. If the user
            is deleted, the offer will also be deleted (on_delete=CASCADE).

    Core fields:
        title (str): Human-friendly name of the offer.
        image (File): Optional file upload (e.g., preview image).
        description (text): Free-form description of the offer.

    Timestamps:
        created_at (datetime): Auto-set when the offer is created.
        updated_at (datetime): Auto-updated on each modification.

    String representation:
        Returns the offer title.
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='uploads/', null=True, blank=True)
    description = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class OfferDetail(models.Model):
    """
    Represents a concrete variant (package) of an Offer.

    Typical variants:
        - basic
        - standard
        - premium

    Relationships:
        offer (FK Offer): Parent offer. When the offer is deleted, all of its
            details are deleted as well (on_delete=CASCADE).

    Core fields (snapshot-like values clients can choose from):
        title (str): Display name of this variant (e.g., "Basic Design").
        revisions (int): Number of revisions included.
        delivery_time_in_days (int): Estimated delivery time in days.
        price (int): Price for this variant (integer-based; adapt if you need decimals).
        features (JSON): List of included features (e.g., ["Logo", "Business Card"]).
        offer_type (choice): One of ('basic', 'standard', 'premium').

    String representation:
        Returns the detail title.
    """
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



    
