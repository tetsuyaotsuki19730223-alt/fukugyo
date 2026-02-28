from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Diagnosis(models.Model):
    RESULT_CHOICES = [
        ("stable", "安定型（制作代行）"),
        ("influence", "影響力型（コンテンツ）"),
        ("attack", "攻撃型（物販）"),
        ("build", "構築型（SaaS/ツール）"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="diagnoses",
        null=True,
        blank=True,
    )
    q1_status = models.CharField(max_length=20)
    q2_time = models.CharField(max_length=20)
    q3_strength = models.CharField(max_length=20)
    q4_risk = models.CharField(max_length=20)
    q5_goal = models.CharField(max_length=20)

    result_type = models.CharField(max_length=20, choices=RESULT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis({self.user_id}, {self.result_type})"
    
class Snippet(models.Model):
    title = models.CharField('タイトル', max_length=128)
    code = models.TextField('コード', blank=True)
    description = models.TextField('説明', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="snippets",
    )
    created_at = models.DateTimeField("投稿日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.title
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=255, blank=True, default="")
    stripe_subscription_id = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"Profile({self.user_id})"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)