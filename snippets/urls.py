from django.urls import path
from . import views

urlpatterns = [
    path("", views.SnippetListView.as_view(), name="snippet_list"),
    path("<int:pk>/", views.SnippetDetailView.as_view(), name="snippet_detail"),
    path("new/", views.SnippetCreateView.as_view(), name="snippet_create"),
    path("<int:pk>/edit/", views.SnippetUpdateView.as_view(), name="snippet_update"),
    path("<int:pk>/delete/", views.SnippetDeleteView.as_view(), name="snippet_delete"),

    # Premium
    path("premium/", views.premium_page, name="premium_page"),

    # Billing
    path("billing/create-checkout-session/", views.create_checkout_session, name="create_checkout_session"),
    path("billing/success/", views.billing_success, name="billing_success"),
    path("billing/cancel/", views.billing_cancel, name="billing_cancel"),

    # Webhook
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),

    path("diagnosis/", views.diagnosis_start, name="diagnosis_start"),
    path("diagnosis/<int:pk>/", views.diagnosis_result, name="diagnosis_result"),
    path("premium/download/stable/", views.premium_download_stable, name="premium_download_stable"),
]
