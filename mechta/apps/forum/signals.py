from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *


@receiver(post_save, sender=ForumSession)
def save_last_visit(**kwargs):
    forum_session = kwargs['instance']
    profile = Profile.objects.get(user=forum_session.user_id)
    profile.last_visit = forum_session.last_visit
    profile.save()