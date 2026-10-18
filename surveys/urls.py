from django.urls import path

from . import editor, views

app_name = "surveys"

urlpatterns = [
    path("fill/", views.survey_list, name="list"),
    path("manage/", editor.survey_manage, name="manage"),
    path("manage/new/", editor.survey_create, name="create"),
    path("surveys/<int:pk>/", views.survey_fill, name="fill"),
    path("surveys/<int:pk>/edit/", editor.survey_editor, name="editor"),
    path("surveys/<int:pk>/preview/", editor.survey_preview, name="preview"),
    path("surveys/<int:pk>/delete/", editor.survey_delete, name="delete"),
    path("surveys/<int:pk>/responses/", editor.survey_responses, name="responses"),
    path("surveys/<int:pk>/responses/<int:rid>/", editor.survey_owner_response, name="owner_response"),
    path("surveys/<int:pk>/thanks/", views.survey_thanks, name="thanks"),
    path("surveys/<int:pk>/result/", views.survey_result, name="result"),
    path("surveys/<int:pk>/editor/meta/", editor.editor_meta, name="editor_meta"),
    path("surveys/<int:pk>/editor/questions/", editor.editor_add_question, name="editor_add_question"),
    path("surveys/<int:pk>/editor/questions/reorder/", editor.editor_reorder, name="editor_reorder"),
    path("surveys/<int:pk>/editor/questions/<int:qid>/", editor.editor_question, name="editor_question"),
]
