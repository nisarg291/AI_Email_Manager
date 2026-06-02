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

from .models import GoogleAccount, UserProfile, ClassifiedEmail, EmailCategory
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

    if not user.profile.onboarded:
        return redirect("profile")
    return redirect("dashboard")


def logout_view(request):
    logout(request)
    return redirect("login")

from django.db.models import Count
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
    profile = request.user.profile
    profile.live_classification = not profile.live_classification
    profile.save(update_fields=["live_classification"])
    messages.success(request, f"Live classification {'ENABLED' if profile.live_classification else 'disabled'}.")
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
    rows = (ClassifiedEmail.objects.filter(user=request.user)
            .exclude(unsubscribe_url="")
            .values("sender", "sender_email", "unsubscribe_url")
            .annotate(count=Count("id"))
            .order_by("-count")[:100])
    return render(request, "subscriptions.html", {"rows": rows,
                                                  "blocked": request.user.profile.blocked_set()})


@login_required
def subscription_block(request, sender_email):
    profile = request.user.profile
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
        messages.error(request, f"Could not load email: {exc}")
        return redirect("manage_emails")
    ce = ClassifiedEmail.objects.filter(user=request.user, gmail_id=msg_id).first()
    back_to = request.GET.get("back", "manage_emails")
    if back_to not in {"manage_emails", "important", "urgent", "trash", "spam", "starred", "subscriptions"}:
        back_to = "manage_emails"
    return render(request, "email_detail.html", {"email": email, "ce": ce, "back_to": back_to})

from django.core.paginator import Paginator
from .forms import ProfileStep1Form, ProfileStep2Form
from .models import UserCategoryPreference, EmailCategory


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
        # Save tier for whatever was shown
        for cat_id in request.POST.getlist("shown_cat_ids"):
            t = request.POST.get(f"tier_{cat_id}")
            if t in {"critical", "important", "normal", "low", "ignore"}:
                UserCategoryPreference.objects.update_or_create(
                    user=request.user,
                    category_id=int(cat_id),
                    defaults={"tier": t},
                )
        # Auto-assign defaults to the rest (so AI classification uses them later)
        shown = set(map(int, request.POST.getlist("shown_cat_ids")))
        for cat in EmailCategory.objects.exclude(id__in=shown):
            UserCategoryPreference.objects.update_or_create(
                user=request.user, category=cat,
                defaults={"tier": cat.default_tier},
            )

        profile.onboarded = True
        profile.save(update_fields=["onboarded"])
        messages.success(request, "All set! Run AI classification to get started.")
        return redirect("dashboard")

    # GET: ask AI for relevant categories
    relevant = services.suggest_relevant_categories(profile, max_count=20)
    prefs = {p.category_id: p.tier for p in request.user.category_prefs.all()}

    cat_groups = {}
    for c in relevant:
        cat_groups.setdefault(c.group, []).append(
            {"obj": c, "tier": prefs.get(c.id, c.default_tier)}
        )

    return render(request, "onboarding_step3.html", {
        "cat_groups": cat_groups,
        "step": 3,
        "total_relevant": len(relevant),
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
    """Edit category tier preferences (post-onboarding)."""
    if request.method == "POST":
        for cat in EmailCategory.objects.all():
            t = request.POST.get(f"tier_{cat.id}")
            if t in {"critical","important","normal","low","ignore"}:
                UserCategoryPreference.objects.update_or_create(
                    user=request.user, category=cat, defaults={"tier": t},
                )
        messages.success(request, "Category preferences saved.")
        return redirect("categories")

    prefs = {p.category_id: p.tier for p in request.user.category_prefs.all()}
    cat_groups = {}
    for c in EmailCategory.objects.exclude(slug__in=["urgent","myorg"]).order_by("group","name"):
        cat_groups.setdefault(c.group, []).append(
            {"obj": c, "tier": prefs.get(c.id, c.default_tier)}
        )
    return render(request, "categories.html", {"cat_groups": cat_groups})


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
    return render(request, "dashboard.html", {
        "google_acc": request.user.google_account, "profile": profile,
        "stats": stats, "recent": recent,
    })



@login_required
def manage_emails(request):
    bail = _require_google_account(request)
    if bail: return bail

    if request.method == "POST":
        scope = request.POST.get("scope", "latest200")
        try:
            result = services.classify_emails(request.user, scope=scope)
            messages.success(request,
                f"Scanned {result['scanned']} • {result['already_done']} skipped • "
                f"{result['newly_processed']} newly processed.")
        except Exception as exc:
            messages.error(request, f"Failed: {exc}")
        return redirect("manage_emails")

    qs = (ClassifiedEmail.objects.filter(user=request.user)
          .select_related("category").order_by("-received_at"))

    # Filters
    cat_id = request.GET.get("category")
    imp = request.GET.get("importance")
    action = request.GET.get("action")
    q = request.GET.get("q", "").strip()
    if cat_id and cat_id.isdigit():    qs = qs.filter(category_id=int(cat_id))
    if imp and imp.isdigit():          qs = qs.filter(importance=int(imp))
    if action in {"labeled","trashed","kept"}: qs = qs.filter(action_taken=action)
    if q: qs = qs.filter(subject__icontains=q) | qs.filter(sender__icontains=q)

    qs = qs[:1000]                                         # cap at 1000
    page = Paginator(qs, 50).get_page(request.GET.get("page"))
    # Show only categories that have at least 1 classified email for this user
    used_cat_ids = (ClassifiedEmail.objects
                    .filter(user=request.user, category__isnull=False)
                    .values_list("category_id", flat=True).distinct())
    categories = EmailCategory.objects.filter(id__in=used_cat_ids).order_by("short_label")
    return render(request, "manage_emails.html", {
        "page": page, "categories": categories,
        "scopes": services.SCOPE_QUERIES,
        "live": request.user.profile.live_classification,
        "current": {"category": cat_id, "importance": imp, "action": action, "q": q},
    })