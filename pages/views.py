from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from surveys.models import Question, Survey

from .catalog import TEMPLATES, get_template


def home(request):
    return render(request, "pages/home.html", {"templates": TEMPLATES[:3]})


def apps(request):
    return render(request, "pages/apps.html")


def templates(request):
    return render(request, "pages/templates.html", {"templates": TEMPLATES})


@login_required
@require_POST
def use_template(request, slug):
    spec = get_template(slug)
    if not spec:
        raise Http404("模板不存在")
    survey = Survey.objects.create(
        owner=request.user,
        title=spec["title"],
        description=spec["blurb"],
        estimated_minutes=spec["estimated_minutes"],
        is_published=False,
    )
    for item in spec["questions"]:
        Question.objects.create(survey=survey, **item)
    return redirect("surveys:editor", pk=survey.pk)
