from .models import ClassificationJob


def active_job(request):
    if not request.user.is_authenticated:
        return {}
    job = (ClassificationJob.objects
           .filter(user=request.user, status__in=["pending", "running"])
           .order_by("-id").first())
    return {"global_active_job": job}
