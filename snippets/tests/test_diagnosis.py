from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from snippets.models import Diagnosis

User = get_user_model()

class DiagnosisTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="pass12345")

    def test_diagnosis_creates_record(self):
        self.client.login(username="u", password="pass12345")
        res = self.client.post(
            reverse("diagnosis_start"),
            data={
                "q1_status": "employee",
                "q2_time": "h1",
                "q3_strength": "make",
                "q4_risk": "low",
                "q5_goal": "5",
            },
            follow=False,
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Diagnosis.objects.count(), 1)
        self.assertEqual(Diagnosis.objects.first().user, self.user)