# Core Django imports.
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import *

# Python module imports
import os


@receiver(post_save, sender=ForumSession)
def save_last_visit(**kwargs):
    forum_session = kwargs['instance']
    profile = Profile.objects.get(user=forum_session.user_id)
    profile.last_visit = forum_session.last_visit
    profile.save()

# @receiver(post_save, sender=User)
# def update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#     instance.profile.save()

@receiver(pre_save, sender=Avatar)
def delete_old_avatar_image(sender, instance, **kwargs):
    try:
        old_avatar = Avatar.objects.get(pk=instance.pk)
    except Avatar.DoesNotExist:
        old_avatar = None

    if old_avatar is not None and old_avatar.image != instance.image and old_avatar.image_url:
        # old_avatar.image.delete(save=True)
        file_path = os.path.join(settings.MEDIA_ROOT, old_avatar.image_url)
        try:
            os.remove(file_path)
        except OSError as e:
            print("Error: %s : %s" % (file_path, e.strerror))