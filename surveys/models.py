from django.conf import settings
from django.db import models


class QuestionType(models.TextChoices):
    SINGLE = "single", "单选题"
    MULTIPLE = "multiple", "多选题"
    DROPDOWN = "dropdown", "下拉题"
    TEXT = "text", "填空题"
    TEXTAREA = "textarea", "简答题"
    RATING = "rating", "评分题"


OPTION_TYPES = {
    QuestionType.SINGLE,
    QuestionType.MULTIPLE,
    QuestionType.DROPDOWN,
}


class Survey(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建者",
        related_name="owned_surveys",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title = models.CharField("标题", max_length=200)
    description = models.TextField("说明", blank=True)
    estimated_minutes = models.PositiveSmallIntegerField("预计用时（分钟）", default=3)
    is_published = models.BooleanField("已发布", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        annotated = getattr(self, "annotated_question_count", None)
        if annotated is not None:
            return annotated
        return self.questions.count()


class Question(models.Model):
    survey = models.ForeignKey(Survey, related_name="questions", on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField("序号", default=1)
    qtype = models.CharField("题型", max_length=20, choices=QuestionType.choices)
    title = models.CharField("题目", max_length=300)
    hint = models.CharField("提示", max_length=200, blank=True)
    required = models.BooleanField("必填", default=True)
    options = models.JSONField("选项", default=list, blank=True)
    scale_max = models.PositiveSmallIntegerField("评分上限", default=5)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.order}. {self.title}"

    @property
    def has_options(self):
        return self.qtype in OPTION_TYPES

    @property
    def has_scale(self):
        return self.qtype == QuestionType.RATING


class Response(models.Model):
    survey = models.ForeignKey(Survey, related_name="responses", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("survey", "user")
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user} / {self.survey}"


class Answer(models.Model):
    response = models.ForeignKey(Response, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.JSONField("作答")

    class Meta:
        unique_together = ("response", "question")
