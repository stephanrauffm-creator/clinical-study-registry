from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.text import get_valid_filename
from django.db import models


def instruction_upload_to(instance, filename):
    stem = get_valid_filename(Path(filename).stem) or "instruction"
    ext = Path(filename).suffix.lower()
    if ext != ".pdf":
        ext = ".pdf"
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    candidate = f"instructions/{timestamp}_{stem}{ext}"
    return default_storage.get_available_name(candidate)


class StudyEntry(models.Model):
    piz = models.CharField(max_length=64)
    examination_date = models.DateField()
    liver_ambulance_link = models.BooleanField(default=False)
    fibroscan_lsm_kpa = models.DecimalField(max_digits=8, decimal_places=2)
    fibroscan_cap_dbm = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_entries_created",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_entries_updated",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["piz", "examination_date"],
                name="unique_study_entry_per_day",
            )
        ]
        ordering = ["-examination_date", "-updated_at"]

    def __str__(self):
        return f"{self.piz} ({self.examination_date})"


class InstructionDocument(models.Model):
    title = models.CharField(max_length=255)
    pdf = models.FileField(upload_to=instruction_upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="instruction_documents_uploaded",
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title


class AuditEvent(models.Model):
    action = models.CharField(max_length=64)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_audit_events",
    )
    entry = models.ForeignKey(
        StudyEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    instruction = models.ForeignKey(
        InstructionDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    details = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} at {self.created_at:%Y-%m-%d %H:%M:%S}"
