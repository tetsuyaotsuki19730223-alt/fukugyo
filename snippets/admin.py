from django import forms
from django.contrib import admin
from .models import (
    Profile,
    Mission,
    UserMission,
    CommunityPost,
    DiagnosisResult,
    Diagnosis,
    Roadmap,
    AIChat,
    DailyMission,
    SideJob,
    SideJobApply,
    Template,
    TemplatePurchase,
    SuccessStory,
    BlogPost,
    AIChatLog,
    Referral,
)


class ProfileAdminForm(forms.ModelForm):
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.user:
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)

        email = self.cleaned_data.get("email", "")
        if profile.user:
            profile.user.email = email
            profile.user.save()

        if commit:
            profile.save()

        return profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm

    list_display = (
        "user",
        "email_display",
        "is_premium",
        "xp",
        "level",
        "streak",
        "ai_count",
        "last_login_date",
    )
    list_filter = ("is_premium", "level", "streak")
    search_fields = ("user__username", "user__email")
    list_editable = ("is_premium",)
    ordering = ("-is_premium", "-xp")

    fields = (
        "user",
        "email",
        "is_premium",
        "xp",
        "level",
        "streak",
        "streak_freeze",
        "ai_count",
        "last_login_date",
    )

    def email_display(self, obj):
        return obj.user.email
    email_display.short_description = "Email"


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("title", "xp", "created_at")


@admin.register(UserMission)
class UserMissionAdmin(admin.ModelAdmin):
    list_display = ("user", "mission", "completed")
    list_filter = ("completed",)


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")


@admin.register(DiagnosisResult)
class DiagnosisResultAdmin(admin.ModelAdmin):
    list_display = ("user", "result", "created_at")


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ("user", "result", "created_at")


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")


@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")


@admin.register(DailyMission)
class DailyMissionAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")


@admin.register(SideJob)
class SideJobAdmin(admin.ModelAdmin):
    list_display = ("title", "income_min", "income_max", "difficulty", "created_at")


@admin.register(SideJobApply)
class SideJobApplyAdmin(admin.ModelAdmin):
    list_display = ("job", "user", "created_at")


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "created_by", "created_at")


@admin.register(TemplatePurchase)
class TemplatePurchaseAdmin(admin.ModelAdmin):
    list_display = ("template", "user", "created_at")


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ("name", "job", "sidejob", "income", "created_at")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(AIChatLog)
class AIChatLogAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "invited_count", "created_at")