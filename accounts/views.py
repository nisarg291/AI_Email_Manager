# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status
# from django.contrib.auth.models import User
# from django.contrib.auth import logout
# from .models import UserProfile
# from .serializers import UserDetailSerializer, UserProfileSerializer

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_user(request):
#     """Get current authenticated user profile"""
#     try:
#         profile = request.user.profile
#     except UserProfile.DoesNotExist:
#         profile = UserProfile.objects.create(user=request.user)
    
#     serializer = UserDetailSerializer(request.user)
#     return Response(serializer.data)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def update_user_preferences(request):
#     """Update user preferences and introduction"""
#     try:
#         profile = request.user.profile
#     except UserProfile.DoesNotExist:
#         profile = UserProfile.objects.create(user=request.user)
    
#     data = request.data
    
#     if 'introduction' in data:
#         profile.introduction = data['introduction']
#     if 'important_email_types' in data:
#         profile.important_email_types = data['important_email_types']
#     if 'unimportant_email_types' in data:
#         profile.unimportant_email_types = data['unimportant_email_types']
#     if 'personal_emails' in data:
#         profile.personal_emails = data['personal_emails']
#     if 'current_activities' in data:
#         profile.current_activities = data['current_activities']
    
#     profile.save()
#     serializer = UserProfileSerializer(profile)
#     return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def logout_user(request):
#     """Logout user"""
#     logout(request)
#     return Response({'message': 'Logged out successfully'})

# @api_view(['POST'])
# def oauth_login_callback(request):
#     """Handle OAuth login callback"""
#     user = request.user
#     if user.is_authenticated:
#         try:
#             profile = user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=user)
        
#         serializer = UserDetailSerializer(user)
#         return Response({
#             'status': 'success',
#             'user': serializer.data,
#         })
#     return Response({
#         'status': 'error',
#         'message': 'Not authenticated'
#     }, status=status.HTTP_401_UNAUTHORIZED)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def check_auth(request):
#     """Check if user is authenticated"""
#     try:
#         profile = request.user.profile
#     except UserProfile.DoesNotExist:
#         profile = UserProfile.objects.create(user=request.user)
    
#     serializer = UserDetailSerializer(request.user)
#     return Response({
#         'authenticated': True,
#         'user': serializer.data
#     })


# import os
# from datetime import timedelta, timezone as dt_timezone

# from django.conf import settings
# from django.contrib.auth import login, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.shortcuts import redirect, render
# from django.urls import reverse
# from django.utils import timezone

# from google_auth_oauthlib.flow import Flow
# from google.oauth2 import id_token as google_id_token
# from google.auth.transport import requests as google_requests

# from .models import GoogleAccount

# # Allow http://localhost during development (oauthlib otherwise refuses).
# if settings.DEBUG:
#     os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
#     os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"


# def _build_flow(state: str | None = None) -> Flow:
#     return Flow.from_client_config(
#         {
#             "web": {
#                 "client_id": settings.GOOGLE_CLIENT_ID,
#                 "client_secret": settings.GOOGLE_CLIENT_SECRET,
#                 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                 "token_uri": "https://oauth2.googleapis.com/token",
#                 "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
#             }
#         },
#         scopes=settings.GOOGLE_SCOPES,
#         state=state,
#     )


# def login_page(request):
#     """Single landing page: 'Continue with Google'."""
#     if request.user.is_authenticated:
#         return redirect("dashboard")
#     return render(request, "login.html")


# def google_start(request):
#     """Kick off the OAuth flow — both sign-in AND Gmail permissions in one go."""
#     flow = _build_flow()
#     flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

#     auth_url, state = flow.authorization_url(
#         access_type="offline",       # need a refresh token
#         include_granted_scopes="true",
#         prompt="consent",            # always show consent so refresh_token is returned
#     )

#     if not request.session.session_key:
#         request.session.create()
#     request.session["oauth_state"] = state
#     request.session.modified = True
#     request.session.save()

#     return redirect(auth_url)


# def google_callback(request):
#     """Google redirects here after the user grants permission."""
#     state = request.session.get("oauth_state")
#     if not state:
#         return redirect(f"{reverse('login')}?error=session_lost")

#     error = request.GET.get("error")
#     if error:
#         return redirect(f"{reverse('login')}?error={error}")

#     flow = _build_flow(state=state)
#     flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

#     try:
#         flow.fetch_token(authorization_response=request.build_absolute_uri())
#     except Exception as exc:
#         return redirect(f"{reverse('login')}?error=token_exchange_failed&detail={exc}")

#     creds = flow.credentials

#     # Verify the ID token and extract the user's identity.
#     try:
#         id_info = google_id_token.verify_oauth2_token(
#             creds.id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
#         )
#     except Exception:
#         return redirect(f"{reverse('login')}?error=id_token_invalid")

#     google_sub = id_info["sub"]
#     email = id_info.get("email")
#     first_name = id_info.get("given_name", "")
#     last_name = id_info.get("family_name", "")

#     # Find or create the Django user (keyed by email).
#     user, _ = User.objects.get_or_create(
#         username=email,
#         defaults={"email": email, "first_name": first_name, "last_name": last_name},
#     )

#     # Save / update the Google tokens.
#     expiry = (
#         creds.expiry.replace(tzinfo=dt_timezone.utc) if creds.expiry else
#         timezone.now() + timedelta(hours=1)
#     )
#     GoogleAccount.objects.update_or_create(
#         google_sub=google_sub,
#         defaults={
#             "user": user,
#             "email": email,
#             "access_token": creds.token,
#             "refresh_token": creds.refresh_token or
#                              GoogleAccount.objects.filter(google_sub=google_sub)
#                              .values_list("refresh_token", flat=True).first(),
#             "token_expiry": expiry,
#             "scopes": " ".join(creds.scopes or []),
#         },
#     )

#     # Log the user into Django.
#     login(request, user)

#     request.session.pop("oauth_state", None)
#     request.session.modified = True

#     return redirect("dashboard")


# @login_required
# def dashboard(request):
#     google_acc = getattr(request.user, "google_account", None)
#     return render(request, "dashboard.html", {"google_acc": google_acc})


# def logout_view(request):
#     logout(request)
#     return redirect("login")

import os
from datetime import timedelta, timezone as dt_timezone

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from .models import GoogleAccount, UserProfile, ClassifiedEmail, EmailCategory, UserCustomCategory, ClassificationJob
from . import services

if settings.DEBUG:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"]   = "1"

def _require_google_account(request):
    """Return None if user has Google linked, else a redirect to re-link."""
    if not hasattr(request.user, "google_account"):
        messages.warning(request, "Please reconnect your Google account to continue.")
        return redirect("google_start")
    return None


def _has_gmail_scope(user) -> bool:
    """True if the stored token includes the full Gmail scope."""
    try:
        return "mail.google.com" in (user.google_account.scopes or "")
    except Exception:
        return False

# ---------- OAuth (unchanged from before) ----------
def _build_flow(state=None):
    return Flow.from_client_config(
        {"web": {
            "client_id":     settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
            "token_uri":     "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }},
        scopes=settings.GOOGLE_SCOPES,
        state=state,
    )


def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "login.html")


def google_start(request):
    import secrets, hashlib, base64
    # Generate PKCE code verifier & challenge
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode()

    flow = _build_flow()
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )
    if not request.session.session_key:
        request.session.create()
    request.session["oauth_state"] = state
    request.session["code_verifier"] = code_verifier
    request.session.modified = True
    request.session.save()
    return redirect(auth_url)


def google_callback(request):
    state = request.session.get("oauth_state")
    if not state:
        return redirect(f"{reverse('login')}?error=session_lost")

    if request.GET.get("error"):
        return redirect(f"{reverse('login')}?error={request.GET['error']}")

    code_verifier = request.session.get("code_verifier")
    flow = _build_flow(state=state)
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    # Rebuild the absolute URI, forcing https for the proxy environment
    auth_response = request.build_absolute_uri()
    if auth_response.startswith("http://") and not auth_response.startswith("http://localhost"):
        auth_response = "https://" + auth_response[len("http://"):]
    fetch_kwargs = {"authorization_response": auth_response}
    if code_verifier:
        fetch_kwargs["code_verifier"] = code_verifier
    flow.fetch_token(**fetch_kwargs)
    creds = flow.credentials

    id_info = google_id_token.verify_oauth2_token(
        creds.id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID,
    )
    email = id_info.get("email")
    user, _ = User.objects.get_or_create(
        username=email,
        defaults={"email": email,
                  "first_name": id_info.get("given_name", ""),
                  "last_name":  id_info.get("family_name", "")},
    )
    UserProfile.objects.get_or_create(user=user, defaults={"full_name": user.get_full_name()})

    expiry = creds.expiry.replace(tzinfo=dt_timezone.utc) if creds.expiry else \
             timezone.now() + timedelta(hours=1)
    existing_refresh = (GoogleAccount.objects.filter(google_sub=id_info["sub"])
                        .values_list("refresh_token", flat=True).first())
    GoogleAccount.objects.update_or_create(
        google_sub=id_info["sub"],
        defaults={
            "user": user, "email": email,
            "access_token":  creds.token,
            "refresh_token": creds.refresh_token or existing_refresh,
            "token_expiry":  expiry,
            "scopes":        " ".join(creds.scopes or []),
        },
    )

    login(request, user)
    request.session.pop("oauth_state", None)
    request.session.modified = True

    profile_obj, _ = UserProfile.objects.get_or_create(
        user=user, defaults={"full_name": user.get_full_name()}
    )
    if not profile_obj.onboarded:
        return redirect("onboarding_step1")
    return redirect("dashboard")


def logout_view(request):
    logout(request)
    return redirect("login")

from django.db.models import Count, Max
from .tasks import classify_for_user


@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={"full_name": request.user.get_full_name()},
    )
    if not profile.onboarded:
        return redirect("profile")
    stats = {
        "total":     ClassifiedEmail.objects.filter(user=request.user).count(),
        "important": ClassifiedEmail.objects.filter(user=request.user, importance__gte=4).count(),
        "urgent":    ClassifiedEmail.objects.filter(user=request.user, is_urgent=True).count(),
        "trashed":   ClassifiedEmail.objects.filter(user=request.user, action_taken="trashed").count(),
    }
    return render(request, "dashboard.html", {
        "google_acc": getattr(request.user, "google_account", None),
        "profile": profile, "stats": stats,
    })


# @login_required
# def profile_view(request):
#     profile, _ = UserProfile.objects.get_or_create(user=request.user)
#     if request.method == "POST":
#         form = UserProfileForm(request.POST, instance=profile)
#         if form.is_valid():
#             obj = form.save(commit=False)
#             obj.onboarded = True
#             obj.save()
#             form.save_m2m()
#             messages.success(request, "Profile saved.")
#             return redirect("dashboard")
#     else:
#         form = UserProfileForm(instance=profile)
#     cat_groups = {}
#     for c in EmailCategory.objects.exclude(slug__in=["myorg", "urgent"]).order_by("group", "name"):
#         cat_groups.setdefault(c.group, []).append(c)
#     return render(request, "profile.html", {"form": form, "cat_groups": cat_groups, "profile": profile})


@login_required
def toggle_live(request):
    if not _has_gmail_scope(request.user):
        messages.error(request, "Please re-connect your Google account to enable Gmail access.")
        return redirect("manage_emails")
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={"full_name": request.user.get_full_name()}
    )
    profile.live_classification = not profile.live_classification
    profile.save(update_fields=["live_classification"])
    if profile.live_classification:
        services.start_live_thread(request.user.pk)
        messages.success(request, "Live mode ENABLED — new emails will be classified every 3 minutes.")
    else:
        services.stop_live_thread(request.user.pk)
        messages.success(request, "Live mode disabled.")
    return redirect("manage_emails")


# @login_required
# def manage_emails(request):
#     if request.method == "POST":
#         scope = request.POST.get("scope", "latest200")
#         try:
#             result = services.classify_emails(request.user, scope=scope)
#             messages.success(request,
#                 f"Scanned {result['scanned']} • {result['already_done']} skipped • "
#                 f"{result['newly_processed']} new.")
#         except Exception as exc:
#             messages.error(request, f"Failed: {exc}")
#         return redirect("manage_emails")

#     qs = (ClassifiedEmail.objects.filter(user=request.user)
#           .select_related("category").order_by("-received_at")[:300])
#     return render(request, "manage_emails.html", {
#         "emails": qs, "scopes": services.SCOPE_QUERIES,
#         "live": request.user.profile.live_classification,
#     })


@login_required
def urgent_view(request):
    qs = (ClassifiedEmail.objects.filter(user=request.user, is_urgent=True)
          .select_related("category").order_by("-received_at")[:100])
    return render(request, "urgent.html", {"emails": qs})


@login_required
def important_view(request):
    base = (ClassifiedEmail.objects.filter(user=request.user, importance__gte=4)
            .select_related("category"))
    events = base.filter(is_event=True).order_by("-importance", "-received_at")[:50]
    others = base.filter(is_event=False).order_by("-importance", "-received_at")[:50]
    return render(request, "important.html", {"events": events, "others": others})


@login_required
def trash_view(request):
    items, error = [], None
    try: items = services.list_by_query(request.user, "in:trash", max_results=200)
    except Exception as exc: error = str(exc)
    return render(request, "trash.html", {"items": items, "error": error})


@login_required
def trash_empty(request):
    if request.method != "POST": return redirect("trash")
    try:
        n = services.delete_all_trash(request.user)
        messages.success(request, f"Emptied trash: {n} message(s) permanently deleted.")
    except Exception as exc:
        messages.error(request, f"Failed: {exc}")
    return redirect("trash")


@login_required
def trash_restore(request, msg_id):
    services.untrash_message(services.gmail_service(request.user), msg_id)
    ClassifiedEmail.objects.filter(user=request.user, gmail_id=msg_id).update(action_taken="kept")
    return redirect("trash")


@login_required
def trash_delete(request, msg_id):
    services.delete_message(services.gmail_service(request.user), msg_id)
    ClassifiedEmail.objects.filter(user=request.user, gmail_id=msg_id).delete()
    return redirect("trash")


@login_required
def spam_view(request):
    items, error = [], None
    try: items = services.list_by_query(request.user, "in:spam", max_results=100)
    except Exception as exc: error = str(exc)
    return render(request, "spam.html", {"items": items, "error": error})


@login_required
def starred_view(request):
    items, error = [], None
    try: items = services.list_by_query(request.user, "is:starred", max_results=100)
    except Exception as exc: error = str(exc)
    return render(request, "starred.html", {"items": items, "error": error})


@login_required
def subscriptions_view(request):
    # Deduplicate by sender_email: one row per unique sending address
    grouped = (ClassifiedEmail.objects
               .filter(user=request.user)
               .exclude(sender_email="")
               .exclude(unsubscribe_url="")
               .values("sender_email")
               .annotate(count=Count("id"), last_received=Max("received_at"))
               .order_by("-count")[:200])

    enriched = []
    for row in grouped:
        latest = (ClassifiedEmail.objects
                  .filter(user=request.user, sender_email=row["sender_email"])
                  .exclude(unsubscribe_url="")
                  .order_by("-received_at")
                  .values("sender", "unsubscribe_url")
                  .first())
        enriched.append({
            "sender_email":    row["sender_email"],
            "count":           row["count"],
            "last_received":   row["last_received"],
            "sender":          latest["sender"] if latest else row["sender_email"],
            "unsubscribe_url": latest["unsubscribe_url"] if latest else "",
        })

    _sub_profile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={"full_name": request.user.get_full_name()}
    )
    return render(request, "subscriptions.html", {"rows": enriched,
                                                  "blocked": _sub_profile.blocked_set()})


@login_required
def subscription_unblock(request, sender_email):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={"full_name": request.user.get_full_name()}
    )
    lines = [l.strip() for l in profile.blocked_senders.splitlines() if l.strip().lower() != sender_email.lower()]
    profile.blocked_senders = "\n".join(lines)
    profile.save(update_fields=["blocked_senders"])
    messages.success(request, f"{sender_email} unblocked.")
    return redirect("subscriptions")


@login_required
def subscription_block(request, sender_email):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={"full_name": request.user.get_full_name()}
    )
    blocked = profile.blocked_senders
    if sender_email.lower() not in profile.blocked_set():
        profile.blocked_senders = (blocked + "\n" + sender_email).strip()
        profile.save(update_fields=["blocked_senders"])
        messages.success(request, f"{sender_email} blocked. Future emails will be auto-trashed.")
    return redirect("subscriptions")


@login_required
def email_detail(request, msg_id):
    try:
        email = services.get_message_full(request.user, msg_id)
    except Exception as exc:
        err_str = str(exc)
        if "404" in err_str or "notFound" in err_str:
            messages.warning(request, "This email no longer exists in Gmail — it may have been permanently deleted.")
        elif "401" in err_str or "403" in err_str:
            messages.error(request, "Access denied. Please reconnect your Gmail account.")
        else:
            messages.error(request, "Could not load this email. Please try again later.")
        back_to = request.GET.get("back", "manage_emails")
        if back_to not in {"manage_emails", "important", "urgent", "trash", "spam", "starred", "subscriptions"}:
            back_to = "manage_emails"
        return redirect(back_to)
    ce = ClassifiedEmail.objects.filter(user=request.user, gmail_id=msg_id).first()
    back_to = request.GET.get("back", "manage_emails")
    if back_to not in {"manage_emails", "important", "urgent", "trash", "spam", "starred", "subscriptions"}:
        back_to = "manage_emails"
    return render(request, "email_detail.html", {"email": email, "ce": ce, "back_to": back_to})


_BULK_BACK_ALLOWED = {"manage_emails", "important", "urgent", "starred"}

@login_required
def bulk_action(request):
    if request.method != "POST":
        return redirect("manage_emails")
    action = request.POST.get("action")
    ids = request.POST.getlist("gmail_ids")
    back_to = request.POST.get("back", "manage_emails")
    if back_to not in _BULK_BACK_ALLOWED:
        back_to = "manage_emails"
    if not ids or action not in ("trash", "delete_permanent"):
        messages.warning(request, "No emails selected.")
        return redirect(back_to)
    try:
        svc = services.gmail_service(request.user)
        count = 0
        for gid in ids:
            try:
                if action == "trash":
                    services.trash_message(svc, gid)
                    ClassifiedEmail.objects.filter(user=request.user, gmail_id=gid).update(action_taken="trashed")
                else:
                    services.delete_message(svc, gid)
                    ClassifiedEmail.objects.filter(user=request.user, gmail_id=gid).delete()
                count += 1
            except Exception:
                pass
        verb = "Moved to trash" if action == "trash" else "Permanently deleted"
        messages.success(request, f"{verb}: {count} email(s).")
    except Exception as exc:
        messages.error(request, f"Action failed: {exc}")
    return redirect(back_to)


@login_required
def email_trash_action(request, msg_id):
    if request.method != "POST":
        return redirect("manage_emails")
    back_to = request.POST.get("back", "manage_emails")
    if back_to not in {"manage_emails", "important", "urgent", "starred", "trash"}:
        back_to = "manage_emails"
    try:
        services.trash_message(services.gmail_service(request.user), msg_id)
        ClassifiedEmail.objects.filter(user=request.user, gmail_id=msg_id).update(action_taken="trashed")
        messages.success(request, "Moved to trash.")
    except Exception as exc:
        messages.error(request, f"Failed: {exc}")
    return redirect(back_to)


@login_required
def email_delete_action(request, msg_id):
    if request.method != "POST":
        return redirect("manage_emails")
    back_to = request.POST.get("back", "manage_emails")
    if back_to not in {"manage_emails", "important", "urgent", "starred", "trash"}:
        back_to = "manage_emails"
    try:
        services.delete_message(services.gmail_service(request.user), msg_id)
        ClassifiedEmail.objects.filter(user=request.user, gmail_id=msg_id).delete()
        messages.success(request, "Permanently deleted.")
    except Exception as exc:
        messages.error(request, f"Failed: {exc}")
    return redirect(back_to)

import json as _json
import re as _re
from django.http import JsonResponse
from django.core.paginator import Paginator
from .forms import ProfileStep1Form, ProfileStep2Form
from .models import UserCategoryPreference, EmailCategory


@login_required
def job_status(request, job_id):
    """JSON endpoint for polling classification job progress."""
    job = ClassificationJob.objects.filter(user=request.user, pk=job_id).first()
    if not job:
        return JsonResponse({"error": "not found"}, status=404)
    pct = 0
    if job.total > 0:
        pct = round(job.processed / job.total * 100)
    return JsonResponse({
        "status": job.status,
        "total": job.total,
        "processed": job.processed,
        "already_done": job.already_done,
        "pct": pct,
        "error_msg": job.error_msg,
    })


def _ensure_profile(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={"full_name": request.user.get_full_name()},
    )
    return profile


@login_required
def onboarding_step1(request):
    profile = _ensure_profile(request)
    if request.method == "POST":
        form = ProfileStep1Form(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            profile.onboarding_step = 2
            profile.save(update_fields=["onboarding_step"])
            return redirect("onboarding_step2")
    else:
        form = ProfileStep1Form(instance=profile)
    return render(request, "onboarding_step1.html", {"form": form, "step": 1})


@login_required
def onboarding_step2(request):
    profile = _ensure_profile(request)
    if request.method == "POST":
        form = ProfileStep2Form(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            profile.onboarding_step = 3
            profile.save(update_fields=["onboarding_step"])
            return redirect("onboarding_step3")
    else:
        form = ProfileStep2Form(instance=profile)
    return render(request, "onboarding_step2.html", {"form": form, "step": 2})


# @login_required
# def onboarding_step3(request):
#     profile = _ensure_profile(request)

#     if request.method == "POST":
#         # POST data: tier_<cat_id> = critical|important|normal|low|ignore
#         for cat in EmailCategory.objects.all():
#             t = request.POST.get(f"tier_{cat.id}")
#             if t in {"critical", "important", "normal", "low", "ignore"}:
#                 UserCategoryPreference.objects.update_or_create(
#                     user=request.user, category=cat, defaults={"tier": t},
#                 )
#         profile.onboarded = True
#         profile.save(update_fields=["onboarded"])
#         messages.success(request, "All set! Run AI classification to get started.")
#         return redirect("dashboard")

#     # Build current prefs (or default tier)
#     prefs = {p.category_id: p.tier for p in request.user.category_prefs.all()}
#     cat_groups = {}
#     for c in EmailCategory.objects.exclude(slug__in=["urgent","myorg"]).order_by("group","name"):
#         cat_groups.setdefault(c.group, []).append(
#             {"obj": c, "tier": prefs.get(c.id, c.default_tier)}
#         )
#     return render(request, "onboarding_step3.html", {"cat_groups": cat_groups, "step": 3})

@login_required
def onboarding_step3(request):
    profile = _ensure_profile(request)

    if request.method == "POST":
        # Save tier ONLY for the 20 categories that were shown — these become the user's active set
        for cat_id in request.POST.getlist("shown_cat_ids"):
            try:
                cat_id_int = int(cat_id)
            except ValueError:
                continue
            t = request.POST.get(f"tier_{cat_id}", "normal")
            if t not in {"critical", "important", "normal", "low", "ignore"}:
                t = "normal"
            UserCategoryPreference.objects.update_or_create(
                user=request.user,
                category_id=cat_id_int,
                defaults={"tier": t},
            )

        profile.onboarded = True
        profile.save(update_fields=["onboarded"])
        # Pre-create Gmail labels and kick off first batch classification
        import threading as _t
        _t.Thread(target=services.ensure_user_labels, args=(request.user,), daemon=True).start()
        # Auto-start a Latest 200 batch job so the inbox is classified right away
        try:
            job = services.start_batch_job(request.user, "latest200")
            messages.success(request, "All set! Classifying your inbox now — check Manage Emails to see progress.")
            return redirect(f"{reverse('manage_emails')}?job={job.pk}")
        except Exception:
            messages.success(request, "All set! Your labels are being created in Gmail.")
            return redirect("dashboard")

    # GET: ask AI for relevant categories
    relevant = services.suggest_relevant_categories(profile, max_count=20)
    prefs = {p.category_id: p.tier for p in request.user.category_prefs.all()}

    cat_groups = {}
    for c in relevant:
        cat_groups.setdefault(c.group, []).append(
            {"obj": c, "tier": prefs.get(c.id, c.default_tier)}
        )

    from .models import EmailCategory as _EC
    tier_options = [
        ("critical", "🔥", "crit", "Critical — always in inbox"),
        ("important", "⭐", "imp",  "Important — stays in inbox"),
        ("normal",    "📌", "norm", "Normal — label & keep"),
        ("low",       "📥", "low",  "Low — file away"),
        ("ignore",    "🗑️", "ign",  "Ignore — auto-trash"),
    ]
    return render(request, "onboarding_step3.html", {
        "cat_groups": cat_groups,
        "step": 3,
        "total_relevant": len(relevant),
        "total_pool": _EC.objects.count(),
        "tier_options": tier_options,
    })

@login_required
def profile_view(request):
    """Edit basic profile (post-onboarding)."""
    profile = _ensure_profile(request)
    if request.method == "POST":
        f1 = ProfileStep1Form(request.POST, instance=profile, prefix="s1")
        f2 = ProfileStep2Form(request.POST, instance=profile, prefix="s2")
        if f1.is_valid() and f2.is_valid():
            f1.save(); f2.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        f1 = ProfileStep1Form(instance=profile, prefix="s1")
        f2 = ProfileStep2Form(instance=profile, prefix="s2")
    return render(request, "profile.html", {"f1": f1, "f2": f2, "profile": profile})


@login_required
def categories_view(request):
    """
    Show & manage a user's active categories (their personal ~20 set).
    Actions: save_tiers | remove_cat | add_system_cat | add_custom | delete_custom
    """
    if request.method == "POST":
        action = request.POST.get("action", "save_tiers")

        # ── Custom label: add ─────────────────────────────────────
        if action == "add_custom":
            name = request.POST.get("name", "").strip()
            desc = request.POST.get("description", "").strip()
            if name:
                from django.utils.text import slugify
                slug = slugify(name)[:100]
                if slug:
                    obj, created = UserCustomCategory.objects.get_or_create(
                        user=request.user, slug=slug,
                        defaults={"name": name, "description": desc},
                    )
                    if created:
                        try:
                            svc = services.gmail_service(request.user)
                            services.ensure_label(svc, f"Custom/{name}")
                        except Exception:
                            pass
                        messages.success(request, f'Custom label "{name}" added.')
                    else:
                        messages.warning(request, "A label with that name already exists.")
            return redirect("categories")

        # ── Custom label: delete ──────────────────────────────────
        if action == "delete_custom":
            cid = request.POST.get("custom_id")
            if cid and cid.isdigit():
                cc = UserCustomCategory.objects.filter(user=request.user, pk=cid).first()
                if cc:
                    label_name = f"Custom/{cc.name}"
                    cc.delete()
                    try:
                        svc = services.gmail_service(request.user)
                        services.delete_user_label(svc, label_name)
                    except Exception:
                        pass
                    messages.success(request, "Custom label deleted.")
            return redirect("categories")

        # ── Remove a system category from user's active set ───────
        if action == "remove_cat":
            pref_id = request.POST.get("pref_id")
            if pref_id and pref_id.isdigit():
                pref = UserCategoryPreference.objects.select_related("category").filter(
                    user=request.user, pk=pref_id
                ).first()
                if pref:
                    label_name = pref.category.short_label
                    pref.delete()
                    try:
                        svc = services.gmail_service(request.user)
                        services.delete_user_label(svc, label_name)
                    except Exception:
                        pass
                    messages.success(request, "Category removed from your active set.")
            return redirect("categories")

        # ── Add a system category from the pool ───────────────────
        if action == "add_system_cat":
            cat_id = request.POST.get("cat_id")
            if cat_id and cat_id.isdigit():
                cat = EmailCategory.objects.filter(pk=cat_id).first()
                if cat:
                    pref, created = UserCategoryPreference.objects.get_or_create(
                        user=request.user, category=cat,
                        defaults={"tier": cat.default_tier},
                    )
                    if created:
                        try:
                            svc = services.gmail_service(request.user)
                            services.ensure_label(svc, cat.short_label)
                        except Exception:
                            pass
                        messages.success(request, f'"{cat.name}" added to your labels.')
                    else:
                        messages.info(request, f'"{cat.name}" is already in your labels.')
            return redirect("categories")

        # ── Save tier preferences ─────────────────────────────────
        for pref in UserCategoryPreference.objects.filter(user=request.user):
            t = request.POST.get(f"tier_{pref.category_id}")
            if t in {"critical", "important", "normal", "low", "ignore"}:
                pref.tier = t
                pref.save(update_fields=["tier"])
        messages.success(request, "Preferences saved.")
        return redirect("categories")

    # ── GET ───────────────────────────────────────────────────────
    active_prefs = (
        UserCategoryPreference.objects
        .filter(user=request.user)
        .select_related("category")
        .order_by("category__group", "category__name")
    )
    # Group by category group for display
    active_groups = {}
    active_cat_ids = set()
    for p in active_prefs:
        active_groups.setdefault(p.category.group, []).append(p)
        active_cat_ids.add(p.category_id)

    # Pool: all categories the user hasn't added yet
    pool_cats = (
        EmailCategory.objects
        .exclude(id__in=active_cat_ids)
        .exclude(slug__in=["urgent", "myorg", "other"])
        .order_by("group", "name")
    )
    pool_groups = {}
    for c in pool_cats:
        pool_groups.setdefault(c.group, []).append(c)

    custom_cats = request.user.custom_categories.order_by("name")
    tier_choices = [
        ("critical",  "Critical"),
        ("important", "Important"),
        ("normal",    "Normal"),
        ("low",       "Low"),
        ("ignore",    "Ignore"),
    ]
    return render(request, "categories.html", {
        "active_groups": active_groups,
        "pool_groups":   pool_groups,
        "custom_cats":   custom_cats,
        "active_count":  len(active_cat_ids),
        "pool_count":    pool_cats.count(),
        "tier_choices":  tier_choices,
    })


@login_required
def dashboard(request):
    profile = _ensure_profile(request)
    if not profile.onboarded:
        return redirect("onboarding_step1")
    if not hasattr(request.user, "google_account"):
        return redirect("google_start")
    stats = {
        "total":     ClassifiedEmail.objects.filter(user=request.user).count(),
        "important": ClassifiedEmail.objects.filter(user=request.user, importance__gte=4).count(),
        "urgent":    ClassifiedEmail.objects.filter(user=request.user, is_urgent=True).count(),
        "trashed":   ClassifiedEmail.objects.filter(user=request.user, action_taken="trashed").count(),
    }
    recent = (ClassifiedEmail.objects.filter(user=request.user)
              .select_related("category").order_by("-received_at")[:8])
    label_counts = (ClassifiedEmail.objects
                    .filter(user=request.user, category__isnull=False)
                    .values("category__id", "category__short_label")
                    .annotate(count=Count("id"))
                    .order_by("-count")[:12])
    custom_label_counts = (ClassifiedEmail.objects
                           .filter(user=request.user, custom_category__isnull=False)
                           .values("custom_category__id", "custom_category__name")
                           .annotate(count=Count("id"))
                           .order_by("-count")[:6])
    return render(request, "dashboard.html", {
        "google_acc": request.user.google_account, "profile": profile,
        "stats": stats, "recent": recent,
        "label_counts": label_counts,
        "custom_label_counts": custom_label_counts,
    })



@login_required
def manage_emails(request):
    bail = _require_google_account(request)
    if bail: return bail

    if request.method == "POST":
        if not _has_gmail_scope(request.user):
            messages.error(request, "Your Google account needs to be reconnected for Gmail access.")
            return redirect("google_start")
        scope = request.POST.get("scope", "latest200")
        try:
            job = services.start_batch_job(request.user, scope)
            return redirect(f"{reverse('manage_emails')}?job={job.pk}")
        except Exception as exc:
            messages.error(request, f"Failed to start job: {exc}")
            return redirect("manage_emails")

    qs = (ClassifiedEmail.objects.filter(user=request.user)
          .select_related("category", "custom_category").order_by("-received_at"))

    cat_id   = request.GET.get("category")
    cust_id  = request.GET.get("custom_category")
    imp      = request.GET.get("importance")
    action   = request.GET.get("action")
    q        = request.GET.get("q", "").strip()
    if cat_id and cat_id.isdigit():   qs = qs.filter(category_id=int(cat_id))
    if cust_id and cust_id.isdigit(): qs = qs.filter(custom_category_id=int(cust_id))
    if imp and imp.isdigit():         qs = qs.filter(importance=int(imp))
    if action in {"labeled","trashed","kept","archived"}: qs = qs.filter(action_taken=action)
    if q: qs = qs.filter(subject__icontains=q) | qs.filter(sender__icontains=q)

    total_count = qs.count()
    qs   = qs[:2000]
    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get("page"))

    # Compute visible page numbers (±2 around current, clamped)
    curr_pg    = page.number
    num_pgs    = paginator.num_pages
    page_range = list(range(max(1, curr_pg - 2), min(num_pgs, curr_pg + 2) + 1))

    used_cat_ids = (ClassifiedEmail.objects.filter(user=request.user, category__isnull=False)
                    .values_list("category_id", flat=True).distinct())
    categories      = EmailCategory.objects.filter(id__in=used_cat_ids).order_by("name")
    custom_cats     = request.user.custom_categories.all()
    # Always surface any currently running/pending job regardless of URL param
    active_job = (ClassificationJob.objects
                  .filter(user=request.user, status__in=["pending", "running"])
                  .order_by("-created_at").first())
    if not active_job:
        active_job_id = request.GET.get("job")
        if active_job_id and active_job_id.isdigit():
            active_job = ClassificationJob.objects.filter(user=request.user, pk=active_job_id).first()

    profile_obj, _ = UserProfile.objects.get_or_create(
        user=request.user, defaults={"full_name": request.user.get_full_name()}
    )
    label_counts = (ClassifiedEmail.objects
                    .filter(user=request.user, category__isnull=False)
                    .values("category__id", "category__short_label", "category__name")
                    .annotate(lc=Count("id"))
                    .order_by("-lc")[:20])
    custom_label_counts = (ClassifiedEmail.objects
                           .filter(user=request.user, custom_category__isnull=False)
                           .values("custom_category__id", "custom_category__name")
                           .annotate(lc=Count("id"))
                           .order_by("-lc")[:5])

    return render(request, "manage_emails.html", {
        "page": page, "categories": categories, "custom_cats": custom_cats,
        "scopes": services.SCOPE_QUERIES,
        "live": profile_obj.live_classification,
        "live_running": services.is_live_running(request.user.pk),
        "current": {"category": cat_id, "importance": imp, "action": action,
                    "q": q, "custom_category": cust_id},
        "active_job": active_job,
        "needs_reauth": not _has_gmail_scope(request.user),
        "total_count": total_count,
        "page_range":  page_range,
        "num_pages":   num_pgs,
        "label_counts":        label_counts,
        "custom_label_counts": custom_label_counts,
    })


@login_required
def labels_view(request):
    sys_labels = (ClassifiedEmail.objects
                  .filter(user=request.user, category__isnull=False)
                  .values("category__id", "category__name", "category__group", "category__short_label")
                  .annotate(count=Count("id"))
                  .order_by("-count"))
    custom_labels = (ClassifiedEmail.objects
                     .filter(user=request.user, custom_category__isnull=False)
                     .values("custom_category__id", "custom_category__name")
                     .annotate(count=Count("id"))
                     .order_by("-count"))
    uncategorised = ClassifiedEmail.objects.filter(
        user=request.user, category__isnull=True, custom_category__isnull=True
    ).count()
    total = ClassifiedEmail.objects.filter(user=request.user).count()
    return render(request, "labels.html", {
        "sys_labels": sys_labels,
        "custom_labels": custom_labels,
        "uncategorised": uncategorised,
        "total": total,
    })


@login_required
def delete_emails_view(request):
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "older_1month":
                count = services.delete_emails_query(request.user, "older_than:30d")
            elif action == "older_1year":
                count = services.delete_emails_query(request.user, "older_than:1y")
            elif action == "daterange":
                from_date = request.POST.get("from_date", "").strip()
                to_date   = request.POST.get("to_date", "").strip()
                if not from_date or not to_date:
                    messages.error(request, "Please select both start and end dates.")
                    return redirect("delete_emails")
                gmail_from = from_date.replace("-", "/")
                gmail_to   = to_date.replace("-", "/")
                query = f"after:{gmail_from} before:{gmail_to}"
                count = services.delete_emails_query(request.user, query)
            else:
                messages.error(request, "Unknown action.")
                return redirect("delete_emails")
            messages.success(request, f"Permanently deleted {count} email(s) from Gmail.")
        except Exception as exc:
            messages.error(request, f"Deletion failed: {exc}")
        return redirect("delete_emails")
    return render(request, "delete_emails.html", {})


@login_required
def ai_reply_view(request, msg_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    user_intent = request.POST.get("intent", "").strip()
    if not user_intent:
        return JsonResponse({"error": "Please describe what you want to say."}, status=400)
    try:
        email = services.get_message_full(request.user, msg_id)
        profile = UserProfile.objects.filter(user=request.user).first()
        sender_name = (profile.full_name if profile and profile.full_name
                       else request.user.get_full_name() or request.user.email.split("@")[0])
        body_text = email.get("body", "")
        if email.get("body_kind") == "html":
            body_text = _re.sub(r"<[^>]+>", " ", body_text)
        reply = services.generate_ai_reply(
            original_from    = email.get("from", ""),
            original_subject = email.get("subject", ""),
            original_body    = body_text[:2000],
            user_intent      = user_intent,
            sender_name      = sender_name,
            sender_email     = request.user.email,
        )
        return JsonResponse({"reply": reply})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


@login_required
def send_reply_view(request, msg_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    reply_body = request.POST.get("body", "").strip()
    if not reply_body:
        return JsonResponse({"error": "Reply body cannot be empty."}, status=400)
    try:
        email = services.get_message_full(request.user, msg_id)
        raw_from = email.get("from", "")
        m = _re.search(r"<([^>]+)>", raw_from)
        to_email = m.group(1) if m else raw_from
        subject = email.get("subject", "")
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"
        thread_id = email.get("thread_id") or email.get("id")
        services.send_email_reply(request.user, to_email, subject, reply_body, thread_id)
        return JsonResponse({"success": True, "message": "Reply sent successfully!"})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


@login_required
def sent_view(request):
    bail = _require_google_account(request)
    if bail: return bail
    sent_messages = []
    error = None
    try:
        sent_messages = services.list_sent_messages(request.user, max_results=50)
    except Exception as exc:
        error = str(exc)
    return render(request, "sent.html", {"sent_messages": sent_messages, "error": error})


@login_required
def summary_view(request):
    return render(request, "email_summary.html", {})


@login_required
def generate_summary_view(request):
    """AJAX POST: generate AI digest for a chosen time range."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    from django.utils import timezone as tz
    from datetime import timedelta
    time_range = request.POST.get("range", "24h")
    now = tz.now()
    if time_range == "24h":
        since = now - timedelta(hours=24)
        label = "Last 24 hours"
        fetch_limit = 60
    elif time_range == "week":
        since = now - timedelta(days=7)
        label = "Last 7 days"
        fetch_limit = 80
    elif time_range == "month":
        since = now - timedelta(days=30)
        label = "Last 30 days"
        fetch_limit = 120
    else:
        since = now - timedelta(hours=24)
        label = "Last 24 hours"
        fetch_limit = 60

    # Security and spam category slugs — excluded from summary
    _EXCLUDE_SLUGS = {
        "two_fa", "login_alert", "device_alert", "password_reset",
        "breach", "security_report", "access_request", "compliance",
        "phishing", "financial_scam", "fake_job", "malware",
        "spoofing", "bulk_spam", "adult_gambling",
    }

    emails_qs = (ClassifiedEmail.objects
                 .filter(user=request.user, received_at__gte=since, importance__gte=3)
                 .exclude(category__slug__in=_EXCLUDE_SLUGS)
                 .select_related("category", "custom_category")
                 .order_by("-is_urgent", "-importance", "-received_at")[:fetch_limit])

    profile = getattr(request.user, "profile", None)
    profile_text = services._profile_blurb(profile)

    emails_data = []
    for e in emails_qs:
        emails_data.append({
            "gmail_id":   e.gmail_id,
            "from":       e.sender,
            "subject":    e.subject,
            "importance": e.importance,
            "is_urgent":  e.is_urgent,
            "category":   (e.category.name if e.category
                           else (e.custom_category.name if e.custom_category else "Other")),
            "snippet":    e.snippet or "",
        })

    if not emails_data:
        return JsonResponse({
            "items": [],
            "count": 0,
            "label": label,
            "empty_msg": f"No important emails found in the {label.lower()}. Your inbox looks quiet!",
        })

    try:
        items = services.generate_ai_summary(emails_data, profile_text=profile_text)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({"items": items, "count": len(items), "label": label})


@login_required
def compose_ai_view(request):
    """AJAX POST: generate a new email draft with AI."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    to_email = request.POST.get("to_email", "").strip()
    intent   = request.POST.get("intent", "").strip()
    if not to_email:
        return JsonResponse({"error": "Recipient email is required."}, status=400)
    if not intent:
        return JsonResponse({"error": "Please describe what you want to say."}, status=400)
    try:
        profile = UserProfile.objects.filter(user=request.user).first()
        sender_name = (profile.full_name if profile and profile.full_name
                       else request.user.get_full_name() or request.user.email.split("@")[0])
        result = services.generate_ai_compose(
            to_email    = to_email,
            intent      = intent,
            sender_name = sender_name,
            sender_email= request.user.email,
        )
        return JsonResponse(result)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


@login_required
def send_compose_view(request):
    """AJAX POST: send a brand-new email composed with AI."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    to_email = request.POST.get("to_email", "").strip()
    subject  = request.POST.get("subject", "").strip()
    body     = request.POST.get("body", "").strip()
    if not to_email or not body:
        return JsonResponse({"error": "Recipient and body are required."}, status=400)
    try:
        services.send_new_email(request.user, to_email, subject, body)
        return JsonResponse({"success": True, "message": "Email sent successfully!"})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


@login_required
def manage_labels_view(request):
    """
    List all Gmail labels with show/hide toggles.
    POST (AJAX): patch a single label's visibility.
    """
    if request.method == "POST":
        action   = request.POST.get("action", "update_visibility")
        label_id = request.POST.get("label_id", "").strip()
        if not label_id:
            return JsonResponse({"ok": False, "error": "Missing label_id"}, status=400)

        # ── Delete label from Gmail ───────────────────────────────
        if action == "delete_label":
            try:
                svc = services.gmail_service(request.user)
                svc.users().labels().delete(userId="me", id=label_id).execute()
                return JsonResponse({"ok": True})
            except Exception as exc:
                return JsonResponse({"ok": False, "error": str(exc)}, status=500)

        # ── Update visibility ─────────────────────────────────────
        list_vis = request.POST.get("list_visibility") or None
        msg_vis  = request.POST.get("message_visibility") or None
        valid_list = {"labelShow", "labelShowIfUnread", "labelHide", None}
        valid_msg  = {"show", "hide", None}
        if list_vis not in valid_list or msg_vis not in valid_msg:
            return JsonResponse({"ok": False, "error": "Invalid value"}, status=400)
        try:
            services.update_label_visibility(request.user, label_id, list_vis, msg_vis)
            return JsonResponse({"ok": True})
        except Exception as exc:
            return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    labels_error  = None
    system_labels = []
    user_labels   = []
    try:
        all_labels  = services.list_all_labels(request.user)
        system_labels = [l for l in all_labels if l.get("type") == "system"]
        raw_user    = [l for l in all_labels if l.get("type") == "user"]
        enriched    = []
        for lbl in raw_user:
            try:
                enriched.append(services.get_label_detail(request.user, lbl["id"]))
            except Exception:
                enriched.append(lbl)
        user_labels = enriched
    except Exception as exc:
        labels_error = str(exc)

    return render(request, "manage_labels.html", {
        "system_labels": system_labels,
        "user_labels":   user_labels,
        "labels_error":  labels_error,
    })