from django.urls import path

from snippets.views.landing_views import landing
from snippets.views.dashboard_views import dashboard
from snippets.views.ai_views import ai_chat, ai_roadmap
from snippets.views.auth_views import signup
from snippets.views.diagnosis_views import type_diagnosis
from snippets.views.mission_views import mission
from snippets.views.payment_views import pricing, checkout
from snippets.views.legal_views import privacy, terms, legal, contact

# 追加
from snippets.views.community_views import community
from snippets.views.mypage_views import my_page
from snippets.views.ranking_views import ranking

urlpatterns = [

    path("", landing, name="landing"),

    path("dashboard/", dashboard, name="dashboard"),

    path("signup/", signup, name="signup"),

    path("type-diagnosis/", type_diagnosis, name="type_diagnosis"),

    path("ai-chat/", ai_chat, name="ai_chat"),

    path("ai-roadmap/", ai_roadmap, name="ai_roadmap"),

    path("mission/", mission, name="mission"),

    path("pricing/", pricing, name="pricing"),

    path("checkout/", checkout, name="checkout"),

    # 追加
    path("community/", community, name="community"),
    path("my-page/", my_page, name="my_page"),
    path("ranking/", ranking, name="ranking"),

    path("privacy/", privacy, name="privacy"),
    path("terms/", terms, name="terms"),
    path("legal/", legal, name="legal"),
    path("contact/", contact, name="contact"),

]