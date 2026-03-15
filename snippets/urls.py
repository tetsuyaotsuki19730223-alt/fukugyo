from django.urls import path

from snippets.views.landing_views import landing
from snippets.views.dashboard_views import dashboard
from snippets.views.ai_views import ai_chat, ai_roadmap
from snippets.views.auth_views import signup_view
from snippets.views.diagnosis_views import type_diagnosis
from snippets.views.mission_views import mission
from snippets.views.payment_views import pricing, checkout
from snippets.views.legal_views import privacy, terms, legal, contact


urlpatterns = [

    path("", landing, name="landing"),

    path("dashboard/", dashboard, name="dashboard"),

    path("signup/", signup_view, name="signup"),

    path("type-diagnosis/", type_diagnosis, name="type_diagnosis"),

    path("ai-chat/", ai_chat, name="ai_chat"),

    path("ai-roadmap/", ai_roadmap, name="ai_roadmap"),

    path("mission/", mission, name="mission"),

    path("pricing/", pricing, name="pricing"),

    path("checkout/", checkout, name="checkout"),

    path("privacy/", privacy, name="privacy"),
    path("terms/", terms, name="terms"),
    path("legal/", legal, name="legal"),
    path("contact/", contact, name="contact"),

]
