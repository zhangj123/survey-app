from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .management.commands.seed_survey import SAMPLE
from .models import Question, QuestionType, Response, Survey


class SurveyFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.survey = Survey.objects.create(
            title=SAMPLE["title"],
            description=SAMPLE["description"],
            estimated_minutes=3,
            is_published=True,
        )
        for item in SAMPLE["questions"]:
            Question.objects.create(survey=self.survey, **item)

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("surveys:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_register_then_see_survey_list(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "bob",
                "email": "bob@example.com",
                "password1": "password123",
                "password2": "password123",
            },
        )
        self.assertRedirects(response, reverse("surveys:list"))
        follow = self.client.get(reverse("surveys:list"))
        self.assertContains(follow, self.survey.title)

    def test_login_with_next_returns_to_fill_page(self):
        fill_url = reverse("surveys:fill", args=[self.survey.pk])
        login_url = reverse("accounts:login")
        response = self.client.post(
            f"{login_url}?next={fill_url}",
            {"username": "alice", "password": "password123", "next": fill_url},
        )
        self.assertRedirects(response, fill_url)

    def test_required_answers_block_submit(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(reverse("surveys:fill", args=[self.survey.pk]), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "这是必答题")
        self.assertFalse(Response.objects.filter(user=self.user, survey=self.survey).exists())

    def test_submit_survey_and_view_result(self):
        self.client.login(username="alice", password="password123")
        questions = {q.order: q for q in self.survey.questions.all()}
        payload = {
            f"q_{questions[1].id}": "每天",
            f"q_{questions[2].id}": "朋友推荐",
            f"q_{questions[3].id}": ["浏览内容", "搜索查找"],
            f"q_{questions[4].id}": "教育",
            f"q_{questions[5].id}": "4",
            f"q_{questions[6].id}": "上海",
            f"q_{questions[7].id}": "希望导出更快",
        }
        response = self.client.post(reverse("surveys:fill", args=[self.survey.pk]), payload)
        self.assertRedirects(response, reverse("surveys:thanks", args=[self.survey.pk]))
        self.assertTrue(Response.objects.filter(user=self.user, survey=self.survey).exists())

        thanks = self.client.get(reverse("surveys:thanks", args=[self.survey.pk]))
        self.assertContains(thanks, "提交成功")

        result = self.client.get(reverse("surveys:result", args=[self.survey.pk]))
        self.assertContains(result, "仅供查看")
        self.assertContains(result, "上海")
        self.assertContains(result, "浏览内容")

        refill = self.client.get(reverse("surveys:fill", args=[self.survey.pk]))
        self.assertRedirects(refill, reverse("surveys:result", args=[self.survey.pk]))

    def test_unpublished_survey_is_hidden(self):
        self.survey.is_published = False
        self.survey.save()
        self.client.login(username="alice", password="password123")
        response = self.client.get(reverse("surveys:list"))
        self.assertNotContains(response, self.survey.title)


class EditorTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="password123")
        self.other = User.objects.create_user(username="other", password="password123")
        self.client.login(username="owner", password="password123")

    def test_create_survey_opens_editor(self):
        response = self.client.post(reverse("surveys:create"))
        survey = Survey.objects.get(owner=self.owner)
        self.assertFalse(survey.is_published)
        self.assertRedirects(response, reverse("surveys:editor", args=[survey.pk]))

    def test_add_update_reorder_and_publish(self):
        survey = Survey.objects.create(owner=self.owner, title="草稿")
        add = self.client.post(
            reverse("surveys:editor_add_question", args=[survey.pk]),
            data='{"qtype": "single"}',
            content_type="application/json",
        )
        self.assertEqual(add.status_code, 200)
        qid = add.json()["question"]["id"]

        update = self.client.post(
            reverse("surveys:editor_question", args=[survey.pk, qid]),
            data='{"title": "你的职业？", "options": ["学生", "在职", "其他"], "required": true}',
            content_type="application/json",
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.json()["question"]["title"], "你的职业？")

        second = self.client.post(
            reverse("surveys:editor_add_question", args=[survey.pk]),
            data='{"qtype": "text"}',
            content_type="application/json",
        )
        qid2 = second.json()["question"]["id"]
        reorder = self.client.post(
            reverse("surveys:editor_reorder", args=[survey.pk]),
            data=f'{{"ids": [{qid2}, {qid}]}}',
            content_type="application/json",
        )
        self.assertEqual(reorder.status_code, 200)
        ids = [item["id"] for item in reorder.json()["survey"]["questions"]]
        self.assertEqual(ids, [qid2, qid])

        publish = self.client.post(
            reverse("surveys:editor_meta", args=[survey.pk]),
            data='{"is_published": true, "title": "职业调查"}',
            content_type="application/json",
        )
        self.assertEqual(publish.status_code, 200)
        survey.refresh_from_db()
        self.assertTrue(survey.is_published)
        self.assertEqual(survey.title, "职业调查")

        self.client.logout()
        self.client.login(username="other", password="password123")
        listing = self.client.get(reverse("surveys:list"))
        self.assertContains(listing, "职业调查")

    def test_cannot_edit_others_survey(self):
        survey = Survey.objects.create(owner=self.owner, title="别人的")
        self.client.logout()
        self.client.login(username="other", password="password123")
        response = self.client.get(reverse("surveys:editor", args=[survey.pk]))
        self.assertEqual(response.status_code, 404)

    def test_cannot_publish_empty_survey(self):
        survey = Survey.objects.create(owner=self.owner, title="空问卷")
        response = self.client.post(
            reverse("surveys:editor_meta", args=[survey.pk]),
            data='{"is_published": true}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class QuestionTypeTests(TestCase):
    def test_question_types_cover_wjx_basics(self):
        self.assertEqual(
            {choice.value for choice in QuestionType},
            {"single", "multiple", "dropdown", "text", "textarea", "rating"},
        )
