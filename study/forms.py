from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import InstructionDocument, StudyEntry


class StudyEntryForm(forms.ModelForm):
    class Meta:
        model = StudyEntry
        fields = [
            "piz",
            "examination_date",
            "liver_ambulance_link",
            "fibroscan_lsm_kpa",
            "fibroscan_cap_dbm",
        ]
        widgets = {
            "examination_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_examination_date(self):
        examination_date = self.cleaned_data["examination_date"]
        max_allowed = timezone.localdate() + timedelta(days=30)
        if examination_date > max_allowed:
            raise forms.ValidationError(
                "Examination date is too far in the future."
            )
        return examination_date

    def clean_fibroscan_lsm_kpa(self):
        value = self.cleaned_data["fibroscan_lsm_kpa"]
        if value < 0 or value > 200:
            raise forms.ValidationError(
                "Fibroscan LSM must be between 0 and 200 kPa."
            )
        return value

    def clean_fibroscan_cap_dbm(self):
        value = self.cleaned_data["fibroscan_cap_dbm"]
        if value < 0 or value > 500:
            raise forms.ValidationError(
                "Fibroscan CAP must be between 0 and 500 dBm."
            )
        return value


class InstructionDocumentForm(forms.ModelForm):
    class Meta:
        model = InstructionDocument
        fields = ["title", "pdf"]

    def clean_pdf(self):
        pdf = self.cleaned_data["pdf"]
        if not pdf.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF uploads are allowed.")
        return pdf
