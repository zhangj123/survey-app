import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class ScanLoginTicket(models.Model):
    class Provider(models.TextChoices):
        WECHAT = "wechat", "微信"
        QQ = "qq", "QQ"

    class Status(models.TextChoices):
        PENDING = "pending", "待扫码"
        CONFIRMED = "confirmed", "已确认"
        CLAIMED = "claimed", "已登录"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=16, choices=Provider.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def expired(self):
        return timezone.now() - self.created_at > timedelta(minutes=3)
