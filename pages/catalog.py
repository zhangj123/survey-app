from surveys.models import QuestionType

TEMPLATES = [
    {
        "slug": "product",
        "title": "产品使用体验",
        "emoji": "🧁",
        "blurb": "3 分钟摸清用户喜好，适合产品体验回访。",
        "estimated_minutes": 3,
        "questions": [
            {"order": 1, "qtype": QuestionType.SINGLE, "title": "你使用产品的频率？", "required": True, "options": ["每天", "每周几次", "偶尔", "第一次"]},
            {"order": 2, "qtype": QuestionType.RATING, "title": "整体满意度？", "required": True, "scale_max": 5},
            {"order": 3, "qtype": QuestionType.TEXTAREA, "title": "最想吐槽或安利的一点？", "required": False},
        ],
    },
    {
        "slug": "event",
        "title": "活动报名意向",
        "emoji": "🎉",
        "blurb": "周末约局、线下活动都能用的轻量报名表。",
        "estimated_minutes": 2,
        "questions": [
            {"order": 1, "qtype": QuestionType.SINGLE, "title": "你想参加哪场活动？", "required": True, "options": ["下午茶", "桌游夜", "户外走走", "还没想好"]},
            {"order": 2, "qtype": QuestionType.TEXT, "title": "怎么称呼你？", "required": True},
            {"order": 3, "qtype": QuestionType.MULTIPLE, "title": "需要我们准备？", "required": False, "options": ["素食", "不含酒精", "亲子座位", "无"]},
        ],
    },
    {
        "slug": "class",
        "title": "课程反馈小纸条",
        "emoji": "📚",
        "blurb": "课后收集感受，老师看了也会微笑。",
        "estimated_minutes": 3,
        "questions": [
            {"order": 1, "qtype": QuestionType.RATING, "title": "这节课有趣吗？", "required": True, "scale_max": 5},
            {"order": 2, "qtype": QuestionType.SINGLE, "title": "节奏怎么样？", "required": True, "options": ["刚刚好", "有点快", "有点慢"]},
            {"order": 3, "qtype": QuestionType.TEXTAREA, "title": "还想听什么？", "required": False},
        ],
    },
    {
        "slug": "team",
        "title": "团队心情温度计",
        "emoji": "🌤️",
        "blurb": "匿名也行，看看大家这周的能量值。",
        "estimated_minutes": 2,
        "questions": [
            {"order": 1, "qtype": QuestionType.RATING, "title": "这周工作心情", "required": True, "scale_max": 5},
            {"order": 2, "qtype": QuestionType.DROPDOWN, "title": "最需要的支持", "required": True, "options": ["更清晰的目标", "少一点会议", "结对帮忙", "休息一下"]},
            {"order": 3, "qtype": QuestionType.TEXT, "title": "想对团队说的一句话", "required": False},
        ],
    },
    {
        "slug": "profile",
        "title": "有趣的用户画像",
        "emoji": "🧸",
        "blurb": "轻松问兴趣爱好，不像在填户籍。",
        "estimated_minutes": 4,
        "questions": [
            {"order": 1, "qtype": QuestionType.MULTIPLE, "title": "空闲时你通常？", "required": True, "options": ["刷剧", "出门逛", "打游戏", "发呆充电", "运动"]},
            {"order": 2, "qtype": QuestionType.SINGLE, "title": "更喜欢哪种问卷？", "required": True, "options": ["短而萌", "认真专业", "有奖励", "看心情"]},
            {"order": 3, "qtype": QuestionType.TEXTAREA, "title": "用三个词形容你自己", "required": False},
        ],
    },
    {
        "slug": "party",
        "title": "聚会菜单投票",
        "emoji": "🧋",
        "blurb": "吃什么别再 99+ 未读了，投完就定。",
        "estimated_minutes": 1,
        "questions": [
            {"order": 1, "qtype": QuestionType.SINGLE, "title": "主食投谁？", "required": True, "options": ["火锅", "日料", "披萨", "家常菜"]},
            {"order": 2, "qtype": QuestionType.MULTIPLE, "title": "饮料可以多选", "required": True, "options": ["奶茶", "咖啡", "汽水", "白开水也行"]},
            {"order": 3, "qtype": QuestionType.TEXT, "title": "过敏或忌口", "required": False},
        ],
    },
]


def get_template(slug):
    return next((item for item in TEMPLATES if item["slug"] == slug), None)
