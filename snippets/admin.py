from django.contrib import admin
from .models import Profile, CoachMission, Snippet, Mission, SideJob

admin.site.register(Profile)
admin.site.register(CoachMission)
admin.site.register(Snippet)
admin.site.register(Mission)
admin.site.register(SideJob)