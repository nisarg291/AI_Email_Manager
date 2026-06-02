from django import forms
from .models import UserProfile


class ProfileStep1Form(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["full_name", "current_role", "current_position",
                  "current_organization", "org_domain", "email_type"]
        widgets = {f: forms.TextInput(attrs={"class": "form-control"}) for f in
                   ["full_name", "current_position", "current_organization", "org_domain"]}


class ProfileStep2Form(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["education", "experience", "skills_interests",
                  "target_roles", "industries", "location",
                  "additional_context", "blocked_senders"]
        widgets = {
            "education":          forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "experience":         forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "skills_interests":   forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "target_roles":       forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "industries":         forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "additional_context": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "blocked_senders":    forms.Textarea(attrs={"rows": 3, "class": "form-control",
                                                        "placeholder": "one email or domain per line"}),
            "location":           forms.TextInput(attrs={"class": "form-control"}),
        }