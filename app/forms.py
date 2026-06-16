from django import forms
from django.core.exceptions import ValidationError

from .models import Election, Candidate


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = [
            "name",
            "description",
            "start_date",
            "end_date",
        ]
        widgets = {
            "start_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_date"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_date"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        if start and end and end <= start:
            raise ValidationError("End date must be after start date.")

        return cleaned_data


class ElectionUpdateForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = [
            "name",
            "description",
            "start_date",
            "end_date",
            "active",
        ]
        widgets = {
            "start_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_date"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_date"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        if start and end and end <= start:
            raise ValidationError("End date must be after start date.")

        return cleaned_data


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = [
            "user",
            "party",
            "symbol",
            "election",
        ]


class InvitationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )


class InvitationResponseForm(forms.Form):
    accept = forms.BooleanField(required=False)


class VoterRegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your name",
            }
        ),
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter mobile number",
            }
        ),
    )

    def clean_full_name(self):
        full_name = " ".join(str(self.cleaned_data["full_name"]).split()).strip()
        if not full_name:
            raise ValidationError("Name is required.")
        return full_name

    def clean_phone_number(self):
        phone = "".join(
            ch for ch in str(self.cleaned_data["phone_number"]) if ch.isdigit()
        )
        if len(phone) == 12 and phone.startswith("91"):
            phone = phone[2:]
        if len(phone) != 10:
            raise ValidationError("Enter a valid 10-digit mobile number.")
        return phone


class VoterVerificationForm(forms.Form):
    vid = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter VID",
            }
        ),
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter registered mobile number",
            }
        ),
    )

    def clean_vid(self):
        vid = "".join(str(self.cleaned_data["vid"]).split()).upper()
        if not vid:
            raise ValidationError("VID is required.")
        return vid

    def clean_phone_number(self):
        phone = "".join(
            ch for ch in str(self.cleaned_data["phone_number"]) if ch.isdigit()
        )
        if len(phone) == 12 and phone.startswith("91"):
            phone = phone[2:]
        if len(phone) != 10:
            raise ValidationError("Enter a valid 10-digit mobile number.")
        return phone


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter OTP",
            }
        ),
    )

    def clean_otp(self):
        otp = "".join(ch for ch in str(self.cleaned_data["otp"]) if ch.isdigit())
        if len(otp) != 6:
            raise ValidationError("Enter a valid 6-digit OTP.")
        return otp