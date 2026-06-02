from celery import shared_task
from django.contrib.auth.models import User
from .services import classify_emails


@shared_task(name="accounts.tasks.classify_for_user")
def classify_for_user(user_id, scope="live"):
    user = User.objects.get(pk=user_id)
    return classify_emails(user, scope=scope)


@shared_task(name="accounts.tasks.classify_new_for_all_live_users")
def classify_new_for_all_live_users():
    qs = User.objects.filter(profile__live_classification=True,
                             google_account__isnull=False)
    results = {}
    for u in qs:
        try:
            results[u.email] = classify_emails(u, scope="live")
        except Exception as exc:
            results[u.email] = {"error": str(exc)}
    return results