from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Answer, Question, QuestionType, Response, Survey


def _collect_answers(request, questions):
    errors = {}
    answers = {}
    for question in questions:
        key = f"q_{question.id}"
        if question.qtype == QuestionType.MULTIPLE:
            value = request.POST.getlist(key)
        else:
            value = (request.POST.get(key) or "").strip()

        empty = not value
        if question.required and empty:
            errors[str(question.id)] = "这是必答题"
            continue
        if empty:
            continue
        answers[str(question.id)] = value
    return answers, errors


def _answer_map(response):
    return {str(answer.question_id): answer.value for answer in response.answers.all()}


@login_required
def survey_list(request):
    surveys = Survey.objects.filter(is_published=True).annotate(
        annotated_question_count=Count("questions")
    )
    submitted_ids = set(
        Response.objects.filter(user=request.user).values_list("survey_id", flat=True)
    )
    return render(
        request,
        "surveys/list.html",
        {"surveys": surveys, "submitted_ids": submitted_ids},
    )


@login_required
@require_http_methods(["GET", "POST"])
def survey_fill(request, pk):
    survey = get_object_or_404(Survey, pk=pk, is_published=True)
    questions = list(survey.questions.all())
    existing = Response.objects.filter(survey=survey, user=request.user).first()
    if existing:
        return redirect("surveys:result", pk=survey.pk)

    errors = {}
    posted = {}
    if request.method == "POST":
        posted, errors = _collect_answers(request, questions)
        if not errors:
            response = Response.objects.create(survey=survey, user=request.user)
            Answer.objects.bulk_create(
                [
                    Answer(response=response, question=question, value=posted[str(question.id)])
                    for question in questions
                    if str(question.id) in posted
                ]
            )
            return redirect("surveys:thanks", pk=survey.pk)

    return render(
        request,
        "surveys/fill.html",
        {
            "survey": survey,
            "questions": questions,
            "errors": errors,
            "posted": posted,
            "readonly": False,
            "QuestionType": QuestionType,
        },
    )


@login_required
def survey_thanks(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    get_object_or_404(Response, survey=survey, user=request.user)
    return render(request, "surveys/thanks.html", {"survey": survey})


@login_required
def survey_result(request, pk):
    survey = get_object_or_404(
        Survey.objects.prefetch_related(
            Prefetch("questions", queryset=Question.objects.all()),
        ),
        pk=pk,
    )
    response = get_object_or_404(
        Response.objects.prefetch_related("answers"),
        survey=survey,
        user=request.user,
    )
    return render(
        request,
        "surveys/fill.html",
        {
            "survey": survey,
            "questions": list(survey.questions.all()),
            "errors": {},
            "posted": _answer_map(response),
            "readonly": True,
            "QuestionType": QuestionType,
        },
    )