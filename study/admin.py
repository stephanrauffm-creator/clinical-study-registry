from django.contrib import admin

from .models import AuditEvent, InstructionDocument, StudyEntry


@admin.register(StudyEntry)
class StudyEntryAdmin(admin.ModelAdmin):
    list_display = (
        "piz",
        "examination_date",
        "liver_ambulance_link",
        "fibroscan_lsm_kpa",
        "fibroscan_cap_dbm",
        "created_at",
        "created_by",
    )
    list_filter = ("examination_date", "liver_ambulance_link")
    search_fields = ("piz",)


@admin.register(InstructionDocument)
class InstructionDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at", "uploaded_by")
    search_fields = ("title",)


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "entry", "instruction", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("action", "details")
