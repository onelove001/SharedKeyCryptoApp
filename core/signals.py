from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender = User)
def create_profile(sender, created, instance, **kwargs):

    if created:
        Profile.objects.create(user = instance)


