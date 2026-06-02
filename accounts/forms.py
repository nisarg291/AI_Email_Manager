from django import forms
from .models import UserProfile


class ProfileStep1Form(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["full_name", "current_role", "current_position",
                  "current_organization", "org_domain", "email_type"]
        widgets = {
            "full_name":            forms.TextInput(attrs={"class": "form-control ob-input", "placeholder": "e.g. Jane Smith"}),
            "current_role":         forms.Select(attrs={"class": "form-select ob-input"}),
            "current_position":     forms.TextInput(attrs={"class": "form-control ob-input", "placeholder": "e.g. Senior Software Engineer"}),
            "current_organization": forms.TextInput(attrs={"class": "form-control ob-input", "placeholder": "e.g. Acme Corp"}),
            "org_domain":           forms.TextInput(attrs={"class": "form-control ob-input", "placeholder": "e.g. acme.com"}),
            "email_type":           forms.Select(attrs={"class": "form-select ob-input"}),
        }


class ProfileStep2Form(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["education", "experience", "skills_interests",
                  "target_roles", "industries", "location",
                  "additional_context", "blocked_senders"]
        widgets = {
            "education":          forms.Textarea(attrs={"rows": 2, "class": "form-control ob-input", "placeholder": "Degrees, schools, fields of study…"}),
            "experience":         forms.Textarea(attrs={"rows": 3, "class": "form-control ob-input", "placeholder": "Brief summary of past roles and companies…"}),
            "skills_interests":   forms.Textarea(attrs={"rows": 2, "class": "form-control ob-input", "placeholder": "e.g. Python, product design, machine learning…"}),
            "target_roles":       forms.Textarea(attrs={"rows": 2, "class": "form-control ob-input", "placeholder": "e.g. Product Manager, Data Scientist (leave blank if not job-seeking)"}),
            "industries":         forms.Textarea(attrs={"rows": 2, "class": "form-control ob-input", "placeholder": "e.g. FinTech, Healthcare, SaaS…"}),
            "location":           forms.TextInput(attrs={"class": "form-control ob-input", "placeholder": "e.g. San Francisco, CA"}),
            "additional_context": forms.Textarea(attrs={"rows": 3, "class": "form-control ob-input", "placeholder": "Anything else the AI should know about your email habits or priorities…"}),
            "blocked_senders":    forms.Textarea(attrs={"rows": 3, "class": "form-control ob-input",
                                                        "placeholder": "one email address or domain per line\nexample@spam.com\nnewsletter.net"}),
        }
