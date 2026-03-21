from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

class CommunityPost(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(auto_now=True)
    
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
    
def generate_ref_code():
    return uuid.uuid4().hex[:10]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    is_premium = models.BooleanField(default=False)

    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak = models.IntegerField(default=0)

    last_login_date = models.DateField(null=True, blank=True)
    streak_freeze = models.BooleanField(default=False)

    ai_count = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


def add_xp(profile, xp):
    profile.xp += xp
    profile.level = profile.xp // 100 + 1
    profile.save()


class Snippet(models.Model):

    title = models.CharField(max_length=200)

    code = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CoachMission(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    xp_reward = models.IntegerField(default=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class DiagnosisResult(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    result = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.result
    

class Diagnosis(models.Model):

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
    )

    result = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)


class Referral(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    code = models.CharField(max_length=20, unique=True)

    invited_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.code:

            self.code = uuid.uuid4().hex[:8]

        super().save(*args, **kwargs)


class Roadmap(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

class AIChat(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


class DailyMission(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    created_at = models.DateField(auto_now_add=True)

class SideJob(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    income_min = models.IntegerField(default=0)
    income_max = models.IntegerField(default=0)
    difficulty = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

class SideJobApply(models.Model):

    job = models.ForeignKey(SideJob, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


class Template(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    price = models.IntegerField()

    content = models.TextField()

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

class TemplatePurchase(models.Model):

    template = models.ForeignKey(Template, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

class Mission(models.Model):

    title = models.CharField(max_length=200)

    xp = models.IntegerField(default=10)

    created_at = models.DateTimeField(default=timezone.now)
    
class AISearch(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    query = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

class SuccessStory(models.Model):

    name = models.CharField(max_length=100)

    job = models.CharField(max_length=100)

    sidejob = models.CharField(max_length=200)

    income = models.IntegerField()

    story = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


class BlogPost(models.Model):

    title = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

class UserMission(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)

class AIChatLog(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

