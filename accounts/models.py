# from django.db import models
# from django.contrib.auth.models import User


# class GoogleAccount(models.Model):
#     """Stores Google OAuth tokens for a Django user."""
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="google_account")
#     google_sub = models.CharField(max_length=64, unique=True)   # stable Google user id
#     email = models.EmailField()
#     access_token = models.TextField()
#     refresh_token = models.TextField(blank=True, null=True)
#     token_expiry = models.DateTimeField(null=True, blank=True)
#     scopes = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"GoogleAccount({self.email})"

# from django.db import models
# from django.contrib.auth.models import User


# class GoogleAccount(models.Model):
#     user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name="google_account")
#     google_sub     = models.CharField(max_length=64, unique=True)
#     email          = models.EmailField()
#     access_token   = models.TextField()
#     refresh_token  = models.TextField(blank=True, null=True)
#     token_expiry   = models.DateTimeField(null=True, blank=True)
#     scopes         = models.TextField(blank=True)
#     created_at     = models.DateTimeField(auto_now_add=True)
#     updated_at     = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"GoogleAccount({self.email})"


# class EmailCategory(models.Model):
#     """The 22 fixed categories the AI can choose from."""
#     slug   = models.SlugField(max_length=64, unique=True)
#     name   = models.CharField(max_length=120)
#     group  = models.CharField(max_length=64)              # e.g. "Job-related"
#     description = models.TextField(blank=True)
#     default_action = models.CharField(
#         max_length=16,
#         choices=[("keep", "Keep"), ("archive", "Archive"), ("trash", "Trash")],
#         default="keep",
#     )

#     def __str__(self):
#         return f"{self.group} / {self.name}"


# class UserProfile(models.Model):
#     ROLE_CHOICES = [
#         ("student", "Student"),
#         ("job_seeker", "Job Seeker"),
#         ("working_pro", "Working Professional"),
#         ("hr", "HR / Recruiter"),
#         ("manager", "Manager / Leadership"),
#         ("freelancer", "Freelancer / Consultant"),
#         ("entrepreneur", "Entrepreneur / Founder"),
#         ("other", "Other"),
#     ]
#     EMAIL_TYPE_CHOICES = [("personal", "Personal"), ("work", "Work"), ("mixed", "Mixed")]

#     user                 = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
#     full_name            = models.CharField(max_length=200, blank=True)
#     current_role         = models.CharField(max_length=32, choices=ROLE_CHOICES, default="other")
#     current_position     = models.CharField(max_length=200, blank=True, help_text="e.g. Software Engineer at XYZ")
#     education            = models.TextField(blank=True, help_text="Degrees, schools, fields")
#     experience           = models.TextField(blank=True, help_text="Brief summary of past work")
#     skills_interests     = models.TextField(blank=True)
#     email_type           = models.CharField(max_length=16, choices=EMAIL_TYPE_CHOICES, default="mixed")
#     additional_context   = models.TextField(blank=True, help_text="Anything else the AI should know")
#     important_categories = models.ManyToManyField(EmailCategory, blank=True, related_name="users_who_care")
#     onboarded            = models.BooleanField(default=False)
#     updated_at           = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Profile({self.user.email})"


# class ClassifiedEmail(models.Model):
#     """Cache of AI classification per Gmail message id."""
#     user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="classified_emails")
#     gmail_id    = models.CharField(max_length=64)
#     thread_id   = models.CharField(max_length=64, blank=True)
#     subject     = models.CharField(max_length=500, blank=True)
#     sender      = models.CharField(max_length=300, blank=True)
#     snippet     = models.TextField(blank=True)
#     received_at = models.DateTimeField(null=True, blank=True)
#     category    = models.ForeignKey(EmailCategory, on_delete=models.SET_NULL, null=True)
#     importance  = models.IntegerField(default=3)         # 1 (low) – 5 (critical)
#     reason      = models.TextField(blank=True)
#     action_taken = models.CharField(max_length=16, default="kept")  # kept / labeled / trashed
#     is_event    = models.BooleanField(default=False)
#     event_when  = models.CharField(max_length=120, blank=True)      # free-form, e.g. "Mon 3pm"
#     classified_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = [("user", "gmail_id")]
#         indexes = [models.Index(fields=["user", "-received_at"])]

#     def __str__(self):
#         return f"{self.subject[:50]} → {self.category}"


from django.db import models
from django.contrib.auth.models import User


class GoogleAccount(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name="google_account")
    google_sub     = models.CharField(max_length=64, unique=True)
    email          = models.EmailField()
    access_token   = models.TextField()
    refresh_token  = models.TextField(blank=True, null=True)
    token_expiry   = models.DateTimeField(null=True, blank=True)
    scopes         = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)


TIER_CHOICES = [
    ("critical",  "🔥 Critical"),
    ("important", "⭐ Important"),
    ("normal",    "📌 Normal"),
    ("low",       "📥 Low"),
    ("ignore",    "🗑️ Ignore"),
]


class EmailCategory(models.Model):
    slug         = models.SlugField(max_length=64, unique=True)
    name         = models.CharField(max_length=120)
    short_label  = models.CharField(max_length=32)
    group        = models.CharField(max_length=64)
    description  = models.TextField(blank=True)
    default_tier = models.CharField(max_length=16, choices=TIER_CHOICES, default="normal")

    def __str__(self): return self.short_label


class UserCategoryPreference(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="category_prefs")
    category = models.ForeignKey(EmailCategory, on_delete=models.CASCADE)
    tier     = models.CharField(max_length=16, choices=TIER_CHOICES)

    class Meta:
        unique_together = [("user", "category")]


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("student","Student"),("job_seeker","Job Seeker"),
        ("working_pro","Working Professional"),("hr","HR / Recruiter"),
        ("manager","Manager / Leadership"),("freelancer","Freelancer / Consultant"),
        ("sales","Sales"),("support","Customer Support"),
        ("entrepreneur","Entrepreneur / Founder"),("other","Other"),
    ]
    EMAIL_TYPE_CHOICES = [("personal","Personal"),("work","Work"),("mixed","Mixed")]

    user                 = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name            = models.CharField(max_length=200, blank=True)
    current_role         = models.CharField(max_length=32, choices=ROLE_CHOICES, default="other")
    current_position     = models.CharField(max_length=200, blank=True)
    current_organization = models.CharField(max_length=200, blank=True)
    org_domain           = models.CharField(max_length=120, blank=True)
    education            = models.TextField(blank=True)
    experience           = models.TextField(blank=True)
    skills_interests     = models.TextField(blank=True)
    target_roles         = models.TextField(blank=True)
    industries           = models.TextField(blank=True)
    location             = models.CharField(max_length=200, blank=True)
    email_type           = models.CharField(max_length=16, choices=EMAIL_TYPE_CHOICES, default="mixed")
    additional_context   = models.TextField(blank=True)
    onboarded            = models.BooleanField(default=False)
    onboarding_step      = models.IntegerField(default=1)
    live_classification  = models.BooleanField(default=False)
    blocked_senders      = models.TextField(blank=True)
    updated_at           = models.DateTimeField(auto_now=True)

    def blocked_set(self):
        return {x.strip().lower() for x in self.blocked_senders.splitlines() if x.strip()}

    def tier_for(self, category):
        pref = self.user.category_prefs.filter(category=category).first()
        return pref.tier if pref else category.default_tier


# class EmailCategory(models.Model):
#     slug         = models.SlugField(max_length=64, unique=True)
#     name         = models.CharField(max_length=120)              # display name
#     short_label  = models.CharField(max_length=32)               # actual Gmail label
#     group        = models.CharField(max_length=64)               # for grouping in UI
#     description  = models.TextField(blank=True)
#     default_action = models.CharField(
#         max_length=16,
#         choices=[("keep", "Keep"), ("archive", "Archive"), ("trash", "Trash")],
#         default="keep",
#     )

#     def __str__(self):
#         return f"{self.short_label}"


# class UserProfile(models.Model):
#     ROLE_CHOICES = [
#         ("student", "Student"),
#         ("job_seeker", "Job Seeker"),
#         ("working_pro", "Working Professional"),
#         ("hr", "HR / Recruiter"),
#         ("manager", "Manager / Leadership"),
#         ("freelancer", "Freelancer / Consultant"),
#         ("entrepreneur", "Entrepreneur / Founder"),
#         ("other", "Other"),
#     ]
#     EMAIL_TYPE_CHOICES = [("personal", "Personal"), ("work", "Work"), ("mixed", "Mixed")]

#     user                 = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
#     full_name            = models.CharField(max_length=200, blank=True)
#     current_role         = models.CharField(max_length=32, choices=ROLE_CHOICES, default="other")
#     current_position     = models.CharField(max_length=200, blank=True)
#     current_organization = models.CharField(max_length=200, blank=True)
#     org_domain           = models.CharField(max_length=120, blank=True,
#                             help_text="e.g. acme.com — emails from this domain get the MyOrg label.")
#     education            = models.TextField(blank=True)
#     experience           = models.TextField(blank=True)
#     skills_interests     = models.TextField(blank=True)
#     target_roles         = models.TextField(blank=True, help_text="(Job seekers) What roles are you targeting?")
#     industries           = models.TextField(blank=True)
#     location             = models.CharField(max_length=200, blank=True)
#     email_type           = models.CharField(max_length=16, choices=EMAIL_TYPE_CHOICES, default="mixed")
#     additional_context   = models.TextField(blank=True)
#     important_categories = models.ManyToManyField(EmailCategory, blank=True, related_name="users_who_care")
#     onboarded            = models.BooleanField(default=False)
#     live_classification  = models.BooleanField(default=False)
#     blocked_senders      = models.TextField(blank=True, help_text="One email/domain per line — auto-trashed")
#     updated_at           = models.DateTimeField(auto_now=True)

#     def blocked_set(self):
#         return {x.strip().lower() for x in self.blocked_senders.splitlines() if x.strip()}


class UserCustomCategory(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="custom_categories")
    name        = models.CharField(max_length=100)
    slug        = models.SlugField(max_length=100)
    description = models.TextField(blank=True, help_text="Describe what kinds of emails belong here")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "slug")]

    def __str__(self): return self.name


class ClassificationJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("done",    "Done"),
        ("error",   "Error"),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="classification_jobs")
    scope      = models.CharField(max_length=32)
    status     = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    total      = models.IntegerField(default=0)
    processed  = models.IntegerField(default=0)
    already_done = models.IntegerField(default=0)
    error_msg  = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"Job({self.user_id}, {self.scope}, {self.status})"


class ClassifiedEmail(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name="classified_emails")
    gmail_id        = models.CharField(max_length=64)
    thread_id       = models.CharField(max_length=64, blank=True)
    subject         = models.CharField(max_length=500, blank=True)
    sender          = models.CharField(max_length=300, blank=True)
    sender_email    = models.CharField(max_length=200, blank=True)
    snippet         = models.TextField(blank=True)
    received_at     = models.DateTimeField(null=True, blank=True)
    category        = models.ForeignKey(EmailCategory, on_delete=models.SET_NULL, null=True, blank=True)
    custom_category = models.ForeignKey(UserCustomCategory, on_delete=models.SET_NULL, null=True, blank=True)
    importance      = models.IntegerField(default=3)
    is_urgent       = models.BooleanField(default=False)
    is_event        = models.BooleanField(default=False)
    event_when      = models.CharField(max_length=120, blank=True)
    reason          = models.TextField(blank=True)
    action_taken    = models.CharField(max_length=16, default="kept")
    unsubscribe_url = models.URLField(max_length=1000, blank=True)
    classified_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "gmail_id")]
        indexes = [models.Index(fields=["user", "-received_at"])]