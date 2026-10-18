from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "登录")

    def test_register_page_renders(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "注册")

    def test_login_rejects_bad_password(self):
        User.objects.create_user(username="alice", password="password123")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "alice", "password": "wrong-pass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        User.objects.create_user(username="alice", password="password123")
        self.client.login(username="alice", password="password123")
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("pages:home"))

    def test_wechat_qr_ticket_flow(self):
        alice = User.objects.create_user(username="alice", password="password123")
        created = self.client.post(reverse("accounts:qr_create_wechat"))
        self.assertEqual(created.status_code, 200)
        ticket_id = created.json()["id"]
        image = self.client.get(reverse("accounts:qr_image", args=[ticket_id]))
        self.assertEqual(image.status_code, 200)
        self.assertIn("svg", image["Content-Type"])

        phone = self.client_class()
        phone.login(username="alice", password="password123")
        confirm = phone.post(reverse("accounts:qr_confirm", args=[ticket_id]))
        self.assertEqual(confirm.status_code, 200)
        self.assertContains(confirm, "已确认")

        claim = self.client.post(reverse("accounts:qr_claim", args=[ticket_id]))
        self.assertEqual(claim.status_code, 200)
        self.assertTrue(claim.wsgi_request.user.is_authenticated)
        self.assertEqual(claim.wsgi_request.user, alice)
