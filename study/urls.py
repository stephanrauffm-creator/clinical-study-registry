from django.urls import path

from . import views

app_name = "study"

urlpatterns = [
    path("entries", views.entry_list, name="entry_list"),
    path("entries/new", views.entry_create, name="entry_create"),
    path("entries/<int:entry_id>/edit", views.entry_edit, name="entry_edit"),
    path("export/excel", views.export_excel, name="export_excel"),
    path("instructions", views.instruction_list, name="instruction_list"),
    path("instructions/upload", views.instruction_upload, name="instruction_upload"),
    path(
        "instructions/<int:document_id>/download",
        views.instruction_download,
        name="instruction_download",
    ),
]
