from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from surveys.models import Survey


class MarketingPagesTests(TestCase):
    def test_home_is_public(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "趣调研")
        self.assertContains(response, "首页")
        self.assertContains(response, "应用")
        self.assertContains(response, "问卷模版")
        self.assertContains(response, "免费注册")
        self.assertContains(response, "微信")
        self.assertContains(response, "QQ")

    def test_apps_and_templates_pages(self):
        self.assertEqual(self.client.get(reverse("pages:apps")).status_code, 200)
        response = self.client.get(reverse("pages:templates"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "聚会菜单投票")

    def test_use_template_creates_survey(self):
        User.objects.create_user(username="alice", password="password123")
        self.client.login(username="alice", password="password123")
        response = self.client.post(reverse("pages:use_template", args=["party"]))
        survey = Survey.objects.get(owner__username="alice", title="聚会菜单投票")
        self.assertRedirects(response, reverse("surveys:editor", args=[survey.pk]))
        self.assertEqual(survey.questions.count(), 3)
