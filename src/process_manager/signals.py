# code
from django.db.models.signals import post_save, pre_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import BaseModel, FormType
from django.utils import timezone
from django.contrib.auth import get_user_model


@receiver(pre_save, sender=FormType)
def set_common_fields(sender, instance, **kwargs):
    User = get_user_model()
    if not instance.pk:
        # Only set added_by during the first save.
        instance.created_on = timezone.now()
        # instance.created_by =
    instance.updated_on = timezone.now()
    # instance.updated_by =