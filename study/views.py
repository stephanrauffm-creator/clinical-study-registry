from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from .forms import InstructionDocumentForm, StudyEntryForm
from .models import InstructionDocument, StudyEntry
from .services import ExportLockError, export_to_network, log_audit_event, workbook_to_bytes


def _filtered_entries(request):
    queryset = StudyEntry.objects.select_related("created_by", "updated_by")
    piz = request.GET.get("piz", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    if piz:
        queryset = queryset.filter(piz__icontains=piz)

    parsed_from = parse_date(date_from) if date_from else None
    parsed_to = parse_date(date_to) if date_to else None

    if parsed_from:
        queryset = queryset.filter(examination_date__gte=parsed_from)
    if parsed_to:
        queryset = queryset.filter(examination_date__lte=parsed_to)

    return queryset, {"piz": piz, "date_from": date_from, "date_to": date_to}


@login_required
def entry_list(request):
    entries, filters = _filtered_entries(request)
    return render(
        request,
        "study/entry_list.html",
        {"entries": entries, "filters": filters},
    )


@login_required
def entry_create(request):
    if request.method == "POST":
        form = StudyEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.updated_by = request.user
            entry.save()
            log_audit_event(
                action="create_entry",
                actor=request.user,
                entry=entry,
                details=f"piz={entry.piz} examination_date={entry.examination_date}",
            )
            messages.success(request, "Entry created.")
            return redirect("study:entry_list")
    else:
        form = StudyEntryForm()

    return render(
        request,
        "study/entry_form.html",
        {"form": form, "page_title": "New Entry", "submit_label": "Create Entry"},
    )


@login_required
def entry_edit(request, entry_id):
    entry = get_object_or_404(StudyEntry, id=entry_id)
    if not (request.user.is_staff or entry.created_by_id == request.user.id):
        return HttpResponseForbidden("You are not allowed to edit this entry.")

    if request.method == "POST":
        form = StudyEntryForm(request.POST, instance=entry)
        if form.is_valid():
            updated_entry = form.save(commit=False)
            updated_entry.updated_by = request.user
            updated_entry.save()
            log_audit_event(
                action="update_entry",
                actor=request.user,
                entry=updated_entry,
                details=f"piz={updated_entry.piz} examination_date={updated_entry.examination_date}",
            )
            messages.success(request, "Entry updated.")
            return redirect("study:entry_list")
    else:
        form = StudyEntryForm(instance=entry)

    return render(
        request,
        "study/entry_form.html",
        {"form": form, "page_title": "Edit Entry", "submit_label": "Save Changes"},
    )


@login_required
def export_excel(request):
    entries, _ = _filtered_entries(request)
    entry_list_data = list(entries)
    try:
        workbook = export_to_network(entry_list_data, actor=request.user)
    except ExportLockError as exc:
        return HttpResponse(str(exc), status=409)

    payload = workbook_to_bytes(workbook)
    filename = f"study_entries_{date.today().isoformat()}.xlsx"
    response = HttpResponse(
        payload,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def instruction_list(request):
    documents = InstructionDocument.objects.select_related("uploaded_by")
    return render(
        request,
        "study/instruction_list.html",
        {"documents": documents},
    )


@login_required
def instruction_upload(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only staff users can upload instruction PDFs.")

    if request.method == "POST":
        form = InstructionDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            log_audit_event(
                action="upload_instruction",
                actor=request.user,
                instruction=document,
                details=f"title={document.title}",
            )
            messages.success(request, "Instruction uploaded.")
            return redirect("study:instruction_list")
    else:
        form = InstructionDocumentForm()

    return render(request, "study/instruction_upload.html", {"form": form})


@login_required
def instruction_download(request, document_id):
    document = get_object_or_404(InstructionDocument, id=document_id)
    as_attachment = request.GET.get("download") == "1"
    log_audit_event(
        action="download_instruction",
        actor=request.user,
        instruction=document,
        details=f"title={document.title} as_attachment={as_attachment}",
    )
    return FileResponse(
        document.pdf.open("rb"),
        as_attachment=as_attachment,
        filename=document.pdf.name.split("/")[-1],
    )
