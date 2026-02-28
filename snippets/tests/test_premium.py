from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class PremiumAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="pass12345")

    def test_premium_requires_login(self):
        res = self.client.get(reverse("premium_page"))
        self.assertEqual(res.status_code, 302)

    def test_premium_forbidden_when_not_premium(self):
        self.client.login(username="u", password="pass12345")
        res = self.client.get(reverse("premium_page"))
        self.assertEqual(res.status_code, 403)

    def test_premium_ok_when_premium(self):
        self.user.profile.is_premium = True
        self.user.profile.save()

        self.client.login(username="u", password="pass12345")
        res = self.client.get(reverse("premium_page"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "PREMIUM")