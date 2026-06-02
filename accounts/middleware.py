from django.shortcuts import redirect
from django.urls import resolve, reverse

GATE_EXEMPT = {
    "login", "logout", "google_start", "google_callback",
    "onboarding_step1", "onboarding_step2", "onboarding_step3",
}


class OnboardingGateMiddleware:
    """Redirect non-onboarded users to the right onboarding step."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                url_name = resolve(request.path_info).url_name
            except Exception:
                url_name = None

            if url_name and url_name not in GATE_EXEMPT:
                try:
                    profile = request.user.profile
                    if not profile.onboarded:
                        step = profile.onboarding_step or 1
                        if step <= 1:
                            target = "onboarding_step1"
                        elif step == 2:
                            target = "onboarding_step2"
                        else:
                            target = "onboarding_step3"
                        if url_name != target:
                            return redirect(reverse(target))
                except Exception:
                    if url_name != "onboarding_step1":
                        return redirect(reverse("onboarding_step1"))

        return self.get_response(request)
