from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from snippets.models import Snippet


User = get_user_model()


class SnippetViewsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", password="pass12345")
        self.user2 = User.objects.create_user(username="u2", password="pass12345")

    def test_list_view_shows_snippet(self):
        Snippet.objects.create(title="t1", code="print('hi')", created_by=self.user1)

        res = self.client.get(reverse("snippet_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "t1")

    def test_create_requires_login(self):
        res = self.client.get(reverse("snippet_create"))
        self.assertEqual(res.status_code, 302)
        self.assertIn("/accounts/login/", res["Location"])

    def test_create_sets_created_by(self):
        self.client.login(username="u1", password="pass12345")
        res = self.client.post(
            reverse("snippet_create"),
            data={"title": "new", "code": "x = 1"},
            follow=False,
        )
        self.assertEqual(res.status_code, 302)
        s = Snippet.objects.get(title="new")
        self.assertEqual(s.created_by, self.user1)

    def test_update_only_owner_can_update(self):
        s = Snippet.objects.create(title="before", code="a=1", created_by=self.user1)

        self.client.login(username="u2", password="pass12345")
        res = self.client.post(
            reverse("snippet_update", kwargs={"pk": s.pk}),
            data={"title": "after", "code": "a=2"},
            follow=False,
        )
        # UserPassesTestMixinは通常 403
        self.assertIn(res.status_code, [403, 404])

        s.refresh_from_db()
        self.assertEqual(s.title, "before")

    def test_delete_only_owner_can_delete(self):
        s = Snippet.objects.create(title="del", code="x", created_by=self.user1)

        self.client.login(username="u2", password="pass12345")
        res = self.client.post(reverse("snippet_delete", kwargs={"pk": s.pk}), follow=False)
        self.assertIn(res.status_code, [403, 404])
        self.assertTrue(Snippet.objects.filter(pk=s.pk).exists())