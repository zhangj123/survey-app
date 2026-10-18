import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .models import OPTION_TYPES, Question, QuestionType, Response, Survey
from .views import _answer_map

TYPE_DEFAULTS = {
    QuestionType.SINGLE: {"title": "请选择题目标题", "options": ["选项1", "选项2", "选项3"]},
    QuestionType.MULTIPLE: {"title": "请选择本题可多选", "options": ["选项1", "选项2", "选项3"]},
    QuestionType.DROPDOWN: {"title": "请选择一项", "options": ["选项1", "选项2", "选项3"]},
    QuestionType.TEXT: {"title": "请填写", "options": []},
    QuestionType.TEXTAREA: {"title": "请详细说明", "options": []},
    QuestionType.RATING: {"title": "请评分", "options": [], "scale_max": 5},
}


def _owned_survey(request, pk):
    return get_object_or_404(Survey, pk=pk, owner=request.user)


def _json_body(request):
    try:
        return json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return None


def question_payload(question):
    return {
        "id": question.id,
        "order": question.order,
        "qtype": question.qtype,
        "qtype_label": question.get_qtype_display(),
        "title": question.title,
        "hint": question.hint,
        "required": question.required,
        "options": list(question.options or []),
        "scale_max": question.scale_max,
        "has_options": question.has_options,
        "has_scale": question.has_scale,
    }


def survey_payload(survey):
    questions = [question_payload(q) for q in survey.questions.all()]
    return {
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "estimated_minutes": survey.estimated_minutes,
        "is_published": survey.is_published,
        "questions": questions,
        "types": [{"value": value, "label": label} for value, label in QuestionType.choices],
    }


def _clean_options(raw):
    if not isinstance(raw, list):
        return []
    options = []
    for item in raw:
        text = str(item).strip()
        if text:
            options.append(text[:80])
    return options


def _apply_question_fields(question, data):
    if "title" in data:
        title = str(data.get("title") or "").strip()[:300]
        question.title = title or question.title or "未命名题目"
    if "hint" in data:
        question.hint = str(data.get("hint") or "").strip()[:200]
    if "required" in data:
        question.required = bool(data["required"])
    if "scale_max" in data:
        try:
            scale = int(data["scale_max"])
        except (TypeError, ValueError):
            scale = question.scale_max
        question.scale_max = min(10, max(2, scale))
    if "qtype" in data:
        qtype = data["qtype"]
        if qtype not in QuestionType.values:
            return "不支持的题型"
        question.qtype = qtype
        defaults = TYPE_DEFAULTS[qtype]
        if qtype in OPTION_TYPES and not question.options:
            question.options = list(defaults["options"])
        if qtype == QuestionType.RATING:
            question.scale_max = defaults.get("scale_max", 5)
    if "options" in data or question.qtype in OPTION_TYPES:
        if "options" in data:
            question.options = _clean_options(data["options"])
        if question.qtype in OPTION_TYPES and len(question.options) < 2:
            return "选择题至少需要 2 个选项"
    question.save()
    return None


@login_required
def survey_manage(request):
    surveys = (
        Survey.objects.filter(owner=request.user)
        .annotate(
            annotated_question_count=Count("questions", distinct=True),
            response_count=Count("responses", distinct=True),
        )
    )
    return render(request, "surveys/manage.html", {"surveys": surveys})


@login_required
@require_POST
def survey_create(request):
    survey = Survey.objects.create(
        owner=request.user,
        title="未命名问卷",
        description="",
        estimated_minutes=3,
        is_published=False,
    )
    return redirect("surveys:editor", pk=survey.pk)


@login_required
@require_POST
def survey_delete(request, pk):
    survey = _owned_survey(request, pk)
    survey.delete()
    return redirect("surveys:manage")


@login_required
@ensure_csrf_cookie
def survey_editor(request, pk):
    survey = _owned_survey(request, pk)
    return render(
        request,
        "surveys/editor.html",
        {"survey": survey, "payload": survey_payload(survey)},
    )


@login_required
def survey_preview(request, pk):
    survey = _owned_survey(request, pk)
    return render(
        request,
        "surveys/fill.html",
        {
            "survey": survey,
            "questions": list(survey.questions.all()),
            "errors": {},
            "posted": {},
            "readonly": False,
            "preview": True,
            "QuestionType": QuestionType,
        },
    )


@login_required
def survey_responses(request, pk):
    survey = _owned_survey(request, pk)
    responses = survey.responses.select_related("user").prefetch_related("answers")
    return render(
        request,
        "surveys/responses.html",
        {"survey": survey, "responses": responses},
    )


@login_required
def survey_owner_response(request, pk, rid):
    survey = _owned_survey(request, pk)
    response = get_object_or_404(Response, pk=rid, survey=survey)
    return render(
        request,
        "surveys/fill.html",
        {
            "survey": survey,
            "questions": list(survey.questions.all()),
            "errors": {},
            "posted": _answer_map(response),
            "readonly": True,
            "preview": False,
            "owner_view": True,
            "respondent": response.user,
            "QuestionType": QuestionType,
        },
    )


@login_required
@require_http_methods(["POST"])
def editor_meta(request, pk):
    survey = _owned_survey(request, pk)
    data = _json_body(request)
    if data is None:
        return JsonResponse({"error": "无效的数据"}, status=400)

    if "title" in data:
        title = str(data.get("title") or "").strip()[:200]
        survey.title = title or "未命名问卷"
    if "description" in data:
        survey.description = str(data.get("description") or "").strip()[:2000]
    if "estimated_minutes" in data:
        try:
            survey.estimated_minutes = min(180, max(1, int(data["estimated_minutes"])))
        except (TypeError, ValueError):
            pass
    if "is_published" in data:
        publish = bool(data["is_published"])
        if publish:
            questions = list(survey.questions.all())
            if not questions:
                return JsonResponse({"error": "至少添加 1 道题目后再发布"}, status=400)
            if any(not q.title.strip() for q in questions):
                return JsonResponse({"error": "还有题目未填写标题"}, status=400)
            if any(q.qtype in OPTION_TYPES and len(q.options or []) < 2 for q in questions):
                return JsonResponse({"error": "选择题至少需要 2 个选项"}, status=400)
        survey.is_published = publish
    survey.save()
    return JsonResponse({"ok": True, "survey": survey_payload(survey)})


@login_required
@require_http_methods(["POST"])
def editor_add_question(request, pk):
    survey = _owned_survey(request, pk)
    data = _json_body(request) or {}
    qtype = data.get("qtype") or QuestionType.SINGLE
    if qtype not in QuestionType.values:
        return JsonResponse({"error": "不支持的题型"}, status=400)
    defaults = TYPE_DEFAULTS[qtype]
    order = (survey.questions.count() or 0) + 1
    question = Question.objects.create(
        survey=survey,
        order=order,
        qtype=qtype,
        title=defaults["title"],
        options=list(defaults.get("options") or []),
        scale_max=defaults.get("scale_max", 5),
        required=True,
    )
    survey.save()
    return JsonResponse({"ok": True, "question": question_payload(question)})


@login_required
@require_http_methods(["POST"])
def editor_reorder(request, pk):
    survey = _owned_survey(request, pk)
    data = _json_body(request)
    if not data or not isinstance(data.get("ids"), list):
        return JsonResponse({"error": "无效的排序"}, status=400)
    questions = {q.id: q for q in survey.questions.all()}
    ids = [int(i) for i in data["ids"] if int(i) in questions]
    if len(ids) != len(questions):
        return JsonResponse({"error": "题目列表不完整"}, status=400)
    for index, qid in enumerate(ids, start=1):
        question = questions[qid]
        if question.order != index:
            question.order = index
            question.save(update_fields=["order"])
    survey.save()
    return JsonResponse({"ok": True, "survey": survey_payload(survey)})


@login_required
@require_http_methods(["POST", "DELETE"])
def editor_question(request, pk, qid):
    survey = _owned_survey(request, pk)
    question = get_object_or_404(Question, pk=qid, survey=survey)
    if request.method == "DELETE":
        question.delete()
        for index, item in enumerate(survey.questions.all(), start=1):
            if item.order != index:
                item.order = index
                item.save(update_fields=["order"])
        survey.save()
        return JsonResponse({"ok": True, "survey": survey_payload(survey)})

    data = _json_body(request)
    if data is None:
        return JsonResponse({"error": "无效的数据"}, status=400)
    error = _apply_question_fields(question, data)
    if error:
        return JsonResponse({"error": error}, status=400)
    survey.save()
    return JsonResponse({"ok": True, "question": question_payload(question)})
