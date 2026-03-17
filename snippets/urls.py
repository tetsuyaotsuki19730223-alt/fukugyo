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
from snippets.views.payment_views import success
from snippets.views.diagnosis_views import diagnosis, history, ai_report, roadmap_result
from django.contrib.auth import views as auth_views
from snippets.views.simulator_views import simulator
from snippets.views.landing_views import diagnosis_lp
from snippets.views.template_views import templates
from snippets.views.roadmap_views import ai_roadmap_generator
from snippets.views.success_views import success_stories
from snippets.views.ai_sidejob_views import ai_sidejobs
from snippets.views.ai_diagnosis_views import ai_personal_diagnosis
from snippets.views.referral_views import referral_page
from snippets.views.ai_score_views import ai_sidejob_score
from snippets.views.guide_views import sidejob_guide

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

    path("success/", success, name="success"),

    path("diagnosis/", diagnosis, name="diagnosis"),
    path("history/", history, name="history"),
    path("ai-report/", ai_report, name="ai_report"),
    path("roadmap-result/", roadmap_result, name="roadmap_result"),

    path("login/", auth_views.LoginView.as_view(
        template_name="snippets/login.html"
    ), name="login"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="snippets/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("sidejob-ranking/", ranking, name="sidejob_ranking"),

    path("simulator/", simulator, name="simulator"),

    path("ai-sidejob-diagnosis/", diagnosis_lp, name="diagnosis_lp"),

    path("templates/", templates, name="templates"),

    path("ai-roadmap-generator/", ai_roadmap_generator, name="ai_roadmap_generator"),

    path("success-stories/", success_stories, name="success_stories"),

    path("ai-sidejobs/", ai_sidejobs, name="ai_sidejobs"),

    path("ai-personal-diagnosis/", ai_personal_diagnosis, name="ai_personal_diagnosis"),

    path("referral/", referral_page, name="referral"),

    path("ai-score/", ai_sidejob_score, name="ai_sidejob_score"),

    path("sidejob-guide/", sidejob_guide, name="sidejob_guide"),
]