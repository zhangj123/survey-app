from django.core.management.base import BaseCommand

from surveys.models import Question, QuestionType, Survey


SAMPLE = {
    "title": "产品使用体验调查问卷",
    "description": "本问卷用于了解您对我们产品的使用感受。填写大约需要 3 分钟，所有题目仅用于产品改进。",
    "estimated_minutes": 3,
    "questions": [
        {
            "order": 1,
            "qtype": QuestionType.SINGLE,
            "title": "您目前使用该产品的频率是？",
            "required": True,
            "options": ["每天", "每周几次", "每月几次", "几乎不用"],
        },
        {
            "order": 2,
            "qtype": QuestionType.SINGLE,
            "title": "您是通过哪种方式了解到本产品的？",
            "required": True,
            "options": ["搜索引擎", "朋友推荐", "社交媒体", "应用商店", "其他"],
        },
        {
            "order": 3,
            "qtype": QuestionType.MULTIPLE,
            "title": "您最常使用哪些功能？（可多选）",
            "required": True,
            "options": ["浏览内容", "搜索查找", "填写/提交", "数据导出", "消息通知", "账号设置"],
        },
        {
            "order": 4,
            "qtype": QuestionType.DROPDOWN,
            "title": "您所在的行业是？",
            "required": True,
            "options": ["互联网/软件", "教育", "医疗", "金融", "制造", "零售", "其他"],
        },
        {
            "order": 5,
            "qtype": QuestionType.RATING,
            "title": "总体来看，您对产品的满意度如何？",
            "hint": "1 分表示很不满意，5 分表示非常满意",
            "required": True,
            "scale_max": 5,
        },
        {
            "order": 6,
            "qtype": QuestionType.TEXT,
            "title": "如果方便，请留下您的城市。",
            "hint": "例如：上海",
            "required": False,
        },
        {
            "order": 7,
            "qtype": QuestionType.TEXTAREA,
            "title": "您希望我们优先改进什么？",
            "hint": "欢迎写下使用中的问题或建议",
            "required": False,
        },
    ],
}


class Command(BaseCommand):
    help = "写入一份问卷星风格的示例问卷"

    def handle(self, *args, **options):
        survey, created = Survey.objects.get_or_create(
            title=SAMPLE["title"],
            defaults={
                "description": SAMPLE["description"],
                "estimated_minutes": SAMPLE["estimated_minutes"],
                "is_published": True,
            },
        )
        if not created and survey.questions.exists():
            self.stdout.write(self.style.WARNING("示例问卷已存在，跳过。"))
            return

        survey.description = SAMPLE["description"]
        survey.estimated_minutes = SAMPLE["estimated_minutes"]
        survey.is_published = True
        survey.save()
        survey.questions.all().delete()

        for item in SAMPLE["questions"]:
            Question.objects.create(survey=survey, **item)

        self.stdout.write(self.style.SUCCESS(f"已写入问卷：{survey.title}（{survey.questions.count()} 题）"))
