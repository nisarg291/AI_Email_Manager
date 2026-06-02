# # """Helpers for calling the Gmail API once the user is connected."""
# # from datetime import timezone as _tz
# # from django.conf import settings
# # from django.utils import timezone
# # from google.oauth2.credentials import Credentials
# # from googleapiclient.discovery import build

# # from .models import GoogleAccount


# # def _credentials_for(google_acc: GoogleAccount) -> Credentials:
# #     return Credentials(
# #         token=google_acc.access_token,
# #         refresh_token=google_acc.refresh_token,
# #         token_uri="https://oauth2.googleapis.com/token",
# #         client_id=settings.GOOGLE_CLIENT_ID,
# #         client_secret=settings.GOOGLE_CLIENT_SECRET,
# #         scopes=google_acc.scopes.split() if google_acc.scopes else settings.GOOGLE_SCOPES,
# #     )


# # def gmail_service(user):
# #     """Returns an authenticated Gmail service for the given Django user."""
# #     google_acc = user.google_account
# #     creds = _credentials_for(google_acc)
# #     service = build("gmail", "v1", credentials=creds, cache_discovery=False)

# #     # If the lib refreshed the token, persist the new one.
# #     if creds.token and creds.token != google_acc.access_token:
# #         google_acc.access_token = creds.token
# #         if creds.expiry:
# #             google_acc.token_expiry = creds.expiry.replace(tzinfo=_tz.utc)
# #         google_acc.save(update_fields=["access_token", "token_expiry", "updated_at"])

# #     return service


# # def list_recent_messages(user, max_results: int = 10):
# #     svc = gmail_service(user)
# #     resp = svc.users().messages().list(userId="me", maxResults=max_results).execute()
# #     return resp.get("messages", [])


# """Gmail API + AI classification helpers."""
# import base64
# import json
# from datetime import datetime, timezone, timedelta
# from email.utils import parsedate_to_datetime

# from django.conf import settings
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from openai import OpenAI

# from .models import GoogleAccount, EmailCategory, ClassifiedEmail


# # --------------------- Gmail client ---------------------
# def _credentials_for(google_acc: GoogleAccount) -> Credentials:
#     return Credentials(
#         token=google_acc.access_token,
#         refresh_token=google_acc.refresh_token,
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=settings.GOOGLE_CLIENT_ID,
#         client_secret=settings.GOOGLE_CLIENT_SECRET,
#         scopes=google_acc.scopes.split() if google_acc.scopes else settings.GOOGLE_SCOPES,
#     )


# def gmail_service(user):
#     google_acc = user.google_account
#     creds = _credentials_for(google_acc)
#     svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
#     if creds.token and creds.token != google_acc.access_token:
#         google_acc.access_token = creds.token
#         if creds.expiry:
#             google_acc.token_expiry = creds.expiry.replace(tzinfo=timezone.utc)
#         google_acc.save(update_fields=["access_token", "token_expiry", "updated_at"])
#     return svc


# # --------------------- Read mail ---------------------
# def list_messages(user, query="in:inbox", max_results=50):
#     svc = gmail_service(user)
#     resp = svc.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
#     return resp.get("messages", [])


# def get_message_meta(svc, msg_id):
#     msg = svc.users().messages().get(
#         userId="me", id=msg_id, format="metadata",
#         metadataHeaders=["Subject", "From", "Date"],
#     ).execute()
#     headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
#     received = None
#     if headers.get("Date"):
#         try:
#             received = parsedate_to_datetime(headers["Date"])
#             if received and received.tzinfo is None:
#                 received = received.replace(tzinfo=timezone.utc)
#         except Exception:
#             pass
#     return {
#         "id":        msg["id"],
#         "thread_id": msg["threadId"],
#         "subject":   headers.get("Subject", "(no subject)"),
#         "from":      headers.get("From", ""),
#         "snippet":   msg.get("snippet", ""),
#         "received":  received,
#         "label_ids": msg.get("labelIds", []),
#     }


# # --------------------- Labels ---------------------
# LABEL_PREFIX = "AI/"   # All AI-generated labels live under "AI/<group>/<name>"

# def ensure_label(svc, name: str) -> str:
#     """Return the labelId, creating the label (and its parent path) if needed."""
#     labels = svc.users().labels().list(userId="me").execute().get("labels", [])
#     by_name = {l["name"]: l["id"] for l in labels}
#     if name in by_name:
#         return by_name[name]
#     body = {"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
#     return svc.users().labels().create(userId="me", body=body).execute()["id"]


# def apply_label(svc, msg_id, label_id):
#     svc.users().messages().modify(
#         userId="me", id=msg_id, body={"addLabelIds": [label_id]},
#     ).execute()


# def trash_message(svc, msg_id):
#     svc.users().messages().trash(userId="me", id=msg_id).execute()


# def untrash_message(svc, msg_id):
#     svc.users().messages().untrash(userId="me", id=msg_id).execute()


# def delete_message(svc, msg_id):
#     svc.users().messages().delete(userId="me", id=msg_id).execute()


# # --------------------- AI classification ---------------------
# _openai = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


# def _profile_blurb(profile):
#     if not profile:
#         return "No profile yet."
#     parts = [
#         f"Role: {profile.get_current_role_display()}",
#         f"Position: {profile.current_position or 'N/A'}",
#         f"Education: {profile.education or 'N/A'}",
#         f"Experience: {profile.experience or 'N/A'}",
#         f"Skills/Interests: {profile.skills_interests or 'N/A'}",
#         f"Email type: {profile.get_email_type_display()}",
#         f"Extra: {profile.additional_context or 'N/A'}",
#     ]
#     cats = list(profile.important_categories.values_list("name", flat=True))
#     parts.append(f"User cares about categories: {', '.join(cats) if cats else 'unspecified'}")
#     return "\n".join(parts)


# def classify_emails(user, max_results=50):
#     """Pull recent inbox messages, classify with AI, label in Gmail, store locally,
#     and trash low-value items per the user's preferences."""
#     if _openai is None:
#         raise RuntimeError("OPENAI_API_KEY is not set.")

#     svc = gmail_service(user)
#     profile = getattr(user, "profile", None)
#     profile_text = _profile_blurb(profile)

#     cats = list(EmailCategory.objects.all())
#     cat_lookup = {c.slug: c for c in cats}
#     cats_listing = "\n".join(f"- {c.slug}: {c.name} ({c.group}) — {c.description}" for c in cats)

#     msgs = list_messages(user, query="in:inbox", max_results=max_results)
#     results = []

#     for m in msgs:
#         # Skip ones we've already classified
#         if ClassifiedEmail.objects.filter(user=user, gmail_id=m["id"]).exists():
#             continue

#         meta = get_message_meta(svc, m["id"])

#         prompt = f"""You are an email triage assistant. Classify this email for the user below.

# USER PROFILE
# {profile_text}

# EMAIL
# From: {meta['from']}
# Subject: {meta['subject']}
# Snippet: {meta['snippet']}

# Choose ONE category slug from this list:
# {cats_listing}

# Decide:
# - importance: 1 (junk) to 5 (critical / time-sensitive for this user)
# - action: "keep" | "archive" | "trash" (trash only if clearly low-value or stale)
# - is_event: true if this email contains a meeting, interview, assessment, deadline,
#   or any time-bound thing the user must attend or do
# - event_when: short string describing when (if is_event=true), else ""
# - reason: 1 short sentence

# Respond with ONLY valid JSON:
# {{"category":"<slug>","importance":<1-5>,"action":"keep|archive|trash","is_event":<true|false>,"event_when":"<text>","reason":"<text>"}}
# """
#         try:
#             resp = _openai.chat.completions.create(
#                 model=settings.OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 response_format={"type": "json_object"},
#                 temperature=0.2,
#             )
#             data = json.loads(resp.choices[0].message.content)
#         except Exception as exc:
#             data = {"category": "newsletter_content", "importance": 2, "action": "keep",
#                     "is_event": False, "event_when": "", "reason": f"AI error: {exc}"}

#         cat = cat_lookup.get(data.get("category"))
#         importance = max(1, min(5, int(data.get("importance", 3))))
#         action = data.get("action", "keep")

#         # Decide cleanup based on age (>30 days for low-importance newsletters/marketing)
#         if cat and meta["received"]:
#             age_days = (datetime.now(timezone.utc) - meta["received"]).days
#             if cat.default_action == "trash" or (
#                 cat.default_action == "archive" and age_days >= 30 and importance <= 2
#             ):
#                 action = "trash"

#         # Apply Gmail label like  AI/Job-related/Interview Invitations
#         if cat:
#             label_name = f"{LABEL_PREFIX}{cat.group}/{cat.name}"
#             try:
#                 label_id = ensure_label(svc, label_name)
#                 apply_label(svc, m["id"], label_id)
#             except Exception:
#                 pass

#         if action == "trash":
#             try:
#                 trash_message(svc, m["id"])
#             except Exception:
#                 pass

#         ClassifiedEmail.objects.update_or_create(
#             user=user, gmail_id=m["id"],
#             defaults={
#                 "thread_id":   meta["thread_id"],
#                 "subject":     meta["subject"][:500],
#                 "sender":      meta["from"][:300],
#                 "snippet":     meta["snippet"],
#                 "received_at": meta["received"],
#                 "category":    cat,
#                 "importance":  importance,
#                 "reason":      data.get("reason", ""),
#                 "action_taken": "trashed" if action == "trash" else "labeled",
#                 "is_event":    bool(data.get("is_event", False)),
#                 "event_when":  (data.get("event_when") or "")[:120],
#             },
#         )
#         results.append(meta["id"])

#     return results

# # --------------------- Trash listing / restore ---------------------
# def list_trash(user, max_results=50):
#     svc = gmail_service(user)
#     msgs = svc.users().messages().list(
#         userId="me", q="in:trash", maxResults=max_results,
#     ).execute().get("messages", [])
#     return [get_message_meta(svc, m["id"]) for m in msgs]



# import base64
# import json
# from datetime import datetime, timezone, timedelta
# from email.utils import parsedate_to_datetime

# from django.conf import settings
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from openai import OpenAI

# from .models import GoogleAccount, EmailCategory, ClassifiedEmail


# # -------- Gmail client --------
# def _credentials_for(ga: GoogleAccount) -> Credentials:
#     return Credentials(
#         token=ga.access_token, refresh_token=ga.refresh_token,
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=settings.GOOGLE_CLIENT_ID, client_secret=settings.GOOGLE_CLIENT_SECRET,
#         scopes=ga.scopes.split() if ga.scopes else settings.GOOGLE_SCOPES,
#     )


# def gmail_service(user):
#     ga = user.google_account
#     creds = _credentials_for(ga)
#     svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
#     if creds.token and creds.token != ga.access_token:
#         ga.access_token = creds.token
#         if creds.expiry:
#             ga.token_expiry = creds.expiry.replace(tzinfo=timezone.utc)
#         ga.save(update_fields=["access_token", "token_expiry", "updated_at"])
#     return svc


# # -------- Scope helpers --------
# SCOPE_QUERIES = {
#     # slug       : (Gmail query,                  max_results, label)
#     "latest200"  : ("in:inbox",                   200, "Latest 200 emails"),
#     "week1"      : ("in:inbox newer_than:7d",     300, "Last 1 week"),
#     "week2"      : ("in:inbox newer_than:14d",    400, "Last 2 weeks"),
#     "month1"     : ("in:inbox newer_than:30d",    500, "Last 1 month"),
# }


# # -------- Reading --------
# def list_messages(user, query="in:inbox", max_results=50):
#     svc = gmail_service(user)
#     out, token = [], None
#     while len(out) < max_results:
#         resp = svc.users().messages().list(
#             userId="me", q=query,
#             maxResults=min(500, max_results - len(out)),
#             pageToken=token,
#         ).execute()
#         out.extend(resp.get("messages", []))
#         token = resp.get("nextPageToken")
#         if not token:
#             break
#     return out[:max_results]


# def get_message_meta(svc, msg_id):
#     msg = svc.users().messages().get(
#         userId="me", id=msg_id, format="metadata",
#         metadataHeaders=["Subject", "From", "Date"],
#     ).execute()
#     headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
#     received = None
#     if headers.get("Date"):
#         try:
#             received = parsedate_to_datetime(headers["Date"])
#             if received and received.tzinfo is None:
#                 received = received.replace(tzinfo=timezone.utc)
#         except Exception:
#             pass
#     return {
#         "id": msg["id"], "thread_id": msg["threadId"],
#         "subject": headers.get("Subject", "(no subject)"),
#         "from": headers.get("From", ""), "snippet": msg.get("snippet", ""),
#         "received": received, "label_ids": msg.get("labelIds", []),
#     }


# def _b64url_decode(data: str) -> str:
#     return base64.urlsafe_b64decode(data.encode()).decode("utf-8", errors="replace")


# def _extract_body(payload):
#     mime = payload.get("mimeType", "")
#     if mime.startswith("multipart/"):
#         parts = payload.get("parts", [])
#         # Prefer HTML
#         for p in parts:
#             if p.get("mimeType") == "text/html" and p.get("body", {}).get("data"):
#                 return _b64url_decode(p["body"]["data"]), "html"
#         for p in parts:
#             if p.get("mimeType") == "text/plain" and p.get("body", {}).get("data"):
#                 return _b64url_decode(p["body"]["data"]), "plain"
#         for p in parts:  # Recurse nested multiparts
#             body, kind = _extract_body(p)
#             if body:
#                 return body, kind
#     else:
#         data = payload.get("body", {}).get("data")
#         if data:
#             return _b64url_decode(data), ("html" if mime == "text/html" else "plain")
#     return "", "plain"


# def get_message_full(user, msg_id):
#     svc = gmail_service(user)
#     msg = svc.users().messages().get(userId="me", id=msg_id, format="full").execute()
#     headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
#     body, kind = _extract_body(msg["payload"])
#     received = None
#     if headers.get("Date"):
#         try:
#             received = parsedate_to_datetime(headers["Date"])
#             if received and received.tzinfo is None:
#                 received = received.replace(tzinfo=timezone.utc)
#         except Exception:
#             pass
#     return {
#         "id": msg["id"], "subject": headers.get("Subject", "(no subject)"),
#         "from": headers.get("From", ""), "to": headers.get("To", ""),
#         "date": received, "body": body, "body_kind": kind,
#         "snippet": msg.get("snippet", ""), "in_trash": "TRASH" in msg.get("labelIds", []),
#     }


# # -------- Labels / actions --------
# LABEL_PREFIX = "AI/"


# def ensure_label(svc, name):
#     labels = {l["name"]: l["id"] for l in svc.users().labels().list(userId="me").execute().get("labels", [])}
#     if name in labels:
#         return labels[name]
#     return svc.users().labels().create(userId="me", body={
#         "name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show",
#     }).execute()["id"]


# def apply_label(svc, msg_id, label_id):
#     svc.users().messages().modify(userId="me", id=msg_id, body={"addLabelIds": [label_id]}).execute()


# def trash_message(svc, msg_id):   svc.users().messages().trash(userId="me", id=msg_id).execute()
# def untrash_message(svc, msg_id): svc.users().messages().untrash(userId="me", id=msg_id).execute()
# def delete_message(svc, msg_id):  svc.users().messages().delete(userId="me", id=msg_id).execute()


# def delete_all_trash(user):
#     """Permanently delete every message in Trash. Returns count."""
#     svc = gmail_service(user)
#     total = 0
#     while True:
#         resp = svc.users().messages().list(userId="me", q="in:trash", maxResults=500).execute()
#         msgs = resp.get("messages", [])
#         if not msgs:
#             break
#         ids = [m["id"] for m in msgs]
#         svc.users().messages().batchDelete(userId="me", body={"ids": ids}).execute()
#         ClassifiedEmail.objects.filter(user=user, gmail_id__in=ids).delete()
#         total += len(ids)
#         if len(msgs) < 500:
#             break
#     return total


# # -------- AI classification --------
# _openai = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


# def _profile_blurb(profile):
#     if not profile:
#         return "No profile yet."
#     parts = [
#         f"Role: {profile.get_current_role_display()}",
#         f"Position: {profile.current_position or 'N/A'}",
#         f"Education: {profile.education or 'N/A'}",
#         f"Experience: {profile.experience or 'N/A'}",
#         f"Skills/Interests: {profile.skills_interests or 'N/A'}",
#         f"Email type: {profile.get_email_type_display()}",
#         f"Extra: {profile.additional_context or 'N/A'}",
#     ]
#     cats = list(profile.important_categories.values_list("name", flat=True))
#     parts.append(f"User cares about categories: {', '.join(cats) if cats else 'unspecified'}")
#     return "\n".join(parts)


# def classify_emails(user, scope="latest200"):
#     if _openai is None:
#         raise RuntimeError("OPENAI_API_KEY is not set.")
#     query, max_results, _label = SCOPE_QUERIES.get(scope, SCOPE_QUERIES["latest200"])

#     svc = gmail_service(user)
#     profile = getattr(user, "profile", None)
#     profile_text = _profile_blurb(profile)

#     cats = list(EmailCategory.objects.all())
#     cat_lookup = {c.slug: c for c in cats}
#     cats_listing = "\n".join(f"- {c.slug}: {c.name} ({c.group}) — {c.description}" for c in cats)

#     msgs = list_messages(user, query=query, max_results=max_results)

#     # Skip already-classified in bulk (fast)
#     all_ids = [m["id"] for m in msgs]
#     done = set(ClassifiedEmail.objects.filter(user=user, gmail_id__in=all_ids)
#                .values_list("gmail_id", flat=True))
#     new_msgs = [m for m in msgs if m["id"] not in done]

#     processed = []
#     for m in new_msgs:
#         meta = get_message_meta(svc, m["id"])

#         prompt = f"""You are an email triage assistant. Classify this email for the user below.

# USER PROFILE
# {profile_text}

# EMAIL
# From: {meta['from']}
# Subject: {meta['subject']}
# Snippet: {meta['snippet']}

# Choose ONE category slug from this list:
# {cats_listing}

# Decide:
# - importance: 1 (junk) to 5 (critical / time-sensitive for this user)
# - action: "keep" | "archive" | "trash" (trash only if clearly low-value or stale)
# - is_event: true if this email mentions a meeting, interview, assessment, deadline
# - event_when: short string describing when (if is_event=true), else ""
# - reason: 1 short sentence

# Respond with ONLY valid JSON:
# {{"category":"<slug>","importance":<1-5>,"action":"keep|archive|trash","is_event":<true|false>,"event_when":"<text>","reason":"<text>"}}
# """
#         try:
#             resp = _openai.chat.completions.create(
#                 model=settings.OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 response_format={"type": "json_object"},
#                 temperature=0.2,
#             )
#             data = json.loads(resp.choices[0].message.content)
#         except Exception as exc:
#             data = {"category": "newsletter_content", "importance": 2, "action": "keep",
#                     "is_event": False, "event_when": "", "reason": f"AI error: {exc}"}

#         cat = cat_lookup.get(data.get("category"))
#         importance = max(1, min(5, int(data.get("importance", 3))))
#         action = data.get("action", "keep")

#         if cat and meta["received"]:
#             age_days = (datetime.now(timezone.utc) - meta["received"]).days
#             if cat.default_action == "trash" or (
#                 cat.default_action == "archive" and age_days >= 30 and importance <= 2
#             ):
#                 action = "trash"

#         if cat:
#             try:
#                 label_id = ensure_label(svc, f"{LABEL_PREFIX}{cat.group}/{cat.name}")
#                 apply_label(svc, m["id"], label_id)
#             except Exception:
#                 pass

#         if action == "trash":
#             try:
#                 trash_message(svc, m["id"])
#             except Exception:
#                 pass

#         ClassifiedEmail.objects.update_or_create(
#             user=user, gmail_id=m["id"],
#             defaults={
#                 "thread_id":   meta["thread_id"],
#                 "subject":     meta["subject"][:500],
#                 "sender":      meta["from"][:300],
#                 "snippet":     meta["snippet"],
#                 "received_at": meta["received"],
#                 "category":    cat,
#                 "importance":  importance,
#                 "reason":      data.get("reason", ""),
#                 "action_taken": "trashed" if action == "trash" else "labeled",
#                 "is_event":    bool(data.get("is_event", False)),
#                 "event_when":  (data.get("event_when") or "")[:120],
#             },
#         )
#         processed.append(meta["id"])

#     return {"scanned": len(msgs), "already_done": len(done), "newly_processed": len(processed)}


# # -------- Trash listing --------
# def list_trash(user, max_results=200):
#     svc = gmail_service(user)
#     token, out = None, []
#     while len(out) < max_results:
#         resp = svc.users().messages().list(
#             userId="me", q="in:trash",
#             maxResults=min(100, max_results - len(out)), pageToken=token,
#         ).execute()
#         for m in resp.get("messages", []):
#             out.append(get_message_meta(svc, m["id"]))
#         token = resp.get("nextPageToken")
#         if not token:
#             break
#     return out


"""Gmail + AI helpers."""
import base64
import json
import re
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime, parseaddr

from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI

from .models import GoogleAccount, EmailCategory, ClassifiedEmail


# -------- Gmail client --------
def _credentials_for(ga: GoogleAccount) -> Credentials:
    return Credentials(
        token=ga.access_token, refresh_token=ga.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID, client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=ga.scopes.split() if ga.scopes else settings.GOOGLE_SCOPES,
    )


def gmail_service(user):
    ga = user.google_account
    creds = _credentials_for(ga)
    svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
    if creds.token and creds.token != ga.access_token:
        ga.access_token = creds.token
        if creds.expiry:
            ga.token_expiry = creds.expiry.replace(tzinfo=timezone.utc)
        ga.save(update_fields=["access_token", "token_expiry", "updated_at"])
    return svc


SCOPE_QUERIES = {
    "latest200" : ("in:inbox",               200, "Latest 200 emails"),
    "week1"     : ("in:inbox newer_than:7d", 300, "Last 1 week"),
    "week2"     : ("in:inbox newer_than:14d",400, "Last 2 weeks"),
    "month1"    : ("in:inbox newer_than:30d",500, "Last 1 month"),
    "live"      : ("in:inbox newer_than:1d", 50,  "New today"),  # used by Celery
}


# -------- Reading --------
def list_messages(user, query="in:inbox", max_results=50):
    svc = gmail_service(user)
    out, token = [], None
    while len(out) < max_results:
        resp = svc.users().messages().list(
            userId="me", q=query,
            maxResults=min(500, max_results - len(out)),
            pageToken=token,
        ).execute()
        out.extend(resp.get("messages", []))
        token = resp.get("nextPageToken")
        if not token:
            break
    return out[:max_results]


def get_message_meta(svc, msg_id):
    msg = svc.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["Subject", "From", "Date", "List-Unsubscribe"],
    ).execute()
    headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
    received = None
    if headers.get("Date"):
        try:
            received = parsedate_to_datetime(headers["Date"])
            if received and received.tzinfo is None:
                received = received.replace(tzinfo=timezone.utc)
        except Exception:
            pass
    name, email_addr = parseaddr(headers.get("From", ""))
    unsub = headers.get("List-Unsubscribe", "")
    m = re.search(r"<(https?://[^>]+)>", unsub)
    unsub_url = m.group(1) if m else ""
    return {
        "id": msg["id"], "thread_id": msg["threadId"],
        "subject": headers.get("Subject", "(no subject)"),
        "from": headers.get("From", ""), "from_email": email_addr.lower(),
        "snippet": msg.get("snippet", ""), "received": received,
        "label_ids": msg.get("labelIds", []), "unsubscribe_url": unsub_url,
    }


def _b64url(data): return base64.urlsafe_b64decode(data.encode()).decode("utf-8", errors="replace")


def _extract_body(payload):
    mime = payload.get("mimeType", "")
    if mime.startswith("multipart/"):
        parts = payload.get("parts", [])
        for p in parts:
            if p.get("mimeType") == "text/html" and p.get("body", {}).get("data"):
                return _b64url(p["body"]["data"]), "html"
        for p in parts:
            if p.get("mimeType") == "text/plain" and p.get("body", {}).get("data"):
                return _b64url(p["body"]["data"]), "plain"
        for p in parts:
            body, kind = _extract_body(p)
            if body: return body, kind
    else:
        data = payload.get("body", {}).get("data")
        if data:
            return _b64url(data), ("html" if mime == "text/html" else "plain")
    return "", "plain"


def get_message_full(user, msg_id):
    svc = gmail_service(user)
    msg = svc.users().messages().get(userId="me", id=msg_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
    body, kind = _extract_body(msg["payload"])
    received = None
    if headers.get("Date"):
        try:
            received = parsedate_to_datetime(headers["Date"])
            if received and received.tzinfo is None:
                received = received.replace(tzinfo=timezone.utc)
        except Exception: pass
    return {
        "id": msg["id"], "subject": headers.get("Subject", "(no subject)"),
        "from": headers.get("From", ""), "to": headers.get("To", ""),
        "date": received, "body": body, "body_kind": kind,
        "snippet": msg.get("snippet", ""), "in_trash": "TRASH" in msg.get("labelIds", []),
    }


# -------- Labels / actions --------
def ensure_label(svc, name):
    labels = {l["name"]: l["id"] for l in svc.users().labels().list(userId="me").execute().get("labels", [])}
    if name in labels: return labels[name]
    return svc.users().labels().create(userId="me", body={
        "name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show",
    }).execute()["id"]


def apply_labels(svc, msg_id, label_ids):
    if not label_ids: return
    svc.users().messages().modify(userId="me", id=msg_id, body={"addLabelIds": list(label_ids)}).execute()


def trash_message(svc, msg_id):   svc.users().messages().trash(userId="me", id=msg_id).execute()
def untrash_message(svc, msg_id): svc.users().messages().untrash(userId="me", id=msg_id).execute()
def delete_message(svc, msg_id):  svc.users().messages().delete(userId="me", id=msg_id).execute()


def delete_all_trash(user):
    svc = gmail_service(user)
    total = 0
    while True:
        resp = svc.users().messages().list(userId="me", q="in:trash", maxResults=500).execute()
        msgs = resp.get("messages", [])
        if not msgs: break
        ids = [m["id"] for m in msgs]
        svc.users().messages().batchDelete(userId="me", body={"ids": ids}).execute()
        ClassifiedEmail.objects.filter(user=user, gmail_id__in=ids).delete()
        total += len(ids)
        if len(msgs) < 500: break
    return total


# -------- AI classification --------
_openai = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

def _profile_blurb(profile):
    if not profile:
        return "No profile yet."
    parts = [
        f"Role: {profile.get_current_role_display()}",
        f"Position: {profile.current_position or 'N/A'}",
        f"Current organization: {profile.current_organization or 'N/A'}",
        f"Org domain: {profile.org_domain or 'N/A'}",
        f"Education: {profile.education or 'N/A'}",
        f"Experience: {profile.experience or 'N/A'}",
        f"Skills/Interests: {profile.skills_interests or 'N/A'}",
        f"Target roles: {profile.target_roles or 'N/A'}",
        f"Industries: {profile.industries or 'N/A'}",
        f"Location: {profile.location or 'N/A'}",
        f"Email type: {profile.get_email_type_display()}",
        f"Extra: {profile.additional_context or 'N/A'}",
    ]

    # NEW: get user's tier preferences instead of important_categories
    prefs = (profile.user.category_prefs
             .filter(tier__in=["critical", "important"])
             .select_related("category"))
    high_priority = [f"{p.category.short_label} ({p.tier})" for p in prefs]
    parts.append(f"User cares about: {', '.join(high_priority) if high_priority else 'unspecified'}")

    return "\n".join(parts)

def classify_emails(user, scope="latest200"):
    if _openai is None:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    query, max_results, _ = SCOPE_QUERIES.get(scope, SCOPE_QUERIES["latest200"])

    svc = gmail_service(user)
    profile = getattr(user, "profile", None)
    profile_text = _profile_blurb(profile)
    org_domain = (profile.org_domain or "").lower().strip() if profile else ""
    blocked = profile.blocked_set() if profile else set()

    cats = list(EmailCategory.objects.all())
    cat_by_slug = {c.slug: c for c in cats}

    cats_listing = "\n".join(
        f"- {c.slug}: {c.short_label} ({c.group}) — {c.description}"
        for c in cats
        if c.slug not in {"myorg", "urgent"}
    )

    msgs = list_messages(user, query=query, max_results=max_results)

    all_ids = [m["id"] for m in msgs]

    done = set(
        ClassifiedEmail.objects.filter(
            user=user,
            gmail_id__in=all_ids
        ).values_list("gmail_id", flat=True)
    )

    new_msgs = [m for m in msgs if m["id"] not in done]

    myorg_cat = cat_by_slug.get("myorg")
    urgent_cat = cat_by_slug.get("urgent")

    processed = []

    for m in new_msgs:

        meta = get_message_meta(svc, m["id"])

        sender_domain = (
            meta["from_email"].split("@")[-1]
            if "@" in meta["from_email"]
            else ""
        )

        # =====================================================
        # QUICK BLOCK CHECK
        # =====================================================
        if (
            meta["from_email"] in blocked
            or sender_domain in blocked
        ):
            try:
                trash_message(svc, m["id"])
            except Exception:
                pass

            ClassifiedEmail.objects.update_or_create(
                user=user,
                gmail_id=m["id"],
                defaults={
                    "subject": meta["subject"][:500],
                    "sender": meta["from"][:300],
                    "sender_email": meta["from_email"],
                    "snippet": meta["snippet"],
                    "received_at": meta["received"],
                    "action_taken": "trashed",
                    "reason": "Blocked sender.",
                },
            )

            continue

        # =====================================================
        # AI PROMPT
        # =====================================================
        prompt = f"""
You are an enterprise email triage assistant.

Tailor classification to the user profile.

USER PROFILE
{profile_text}

EMAIL
From: {meta['from']}
Subject: {meta['subject']}
Snippet: {meta['snippet']}

Pick EXACTLY ONE category slug from this list:

{cats_listing}

Also decide:

- importance: 1 (junk) to 5 (critical)
- is_urgent: true ONLY if action is needed within 24-48h
- action:
    "keep"
    "archive"
    "trash"

Guidelines:
- Never trash personal, financial, security, legal,
  healthcare, interview, or government emails.
- Trash only obvious spam, promotions,
  low-value newsletters, or irrelevant marketing.
- Use archive for informational low-priority content.

Also return:
- is_event: true if it references a meeting,
  interview, appointment, deadline, webinar, etc.
- event_when: short time/date text if available
- reason: one short sentence

Respond ONLY with valid JSON:

{{
  "category": "<slug>",
  "importance": 1,
  "is_urgent": false,
  "action": "keep",
  "is_event": false,
  "event_when": "",
  "reason": ""
}}
"""

        # =====================================================
        # AI CLASSIFICATION
        # =====================================================
        try:
            resp = _openai.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )

            data = json.loads(resp.choices[0].message.content)

        except Exception as exc:

            data = {
                "category": "newsletter_industry",
                "importance": 2,
                "is_urgent": False,
                "action": "keep",
                "is_event": False,
                "event_when": "",
                "reason": f"AI error: {exc}",
            }

        # =====================================================
        # CATEGORY
        # =====================================================
        cat = cat_by_slug.get(data.get("category"))

        ai_importance = max(
            1,
            min(5, int(data.get("importance", 3)))
        )

        is_urgent = bool(data.get("is_urgent", False))

        ai_action = data.get("action", "keep")

        # =====================================================
        # USER TIER PREFERENCE
        # =====================================================
        user_tier = (
            profile.tier_for(cat)
            if (profile and cat)
            else (
                cat.default_tier
                if cat
                else "normal"
            )
        )

        # =====================================================
        # TIER -> ACTION + IMPORTANCE
        # =====================================================
        if user_tier == "critical":

            final_action = "keep"
            importance = max(ai_importance, 5)

        elif user_tier == "important":

            final_action = "keep"
            importance = max(ai_importance, 4)

        elif user_tier == "normal":

            final_action = (
                ai_action
                if ai_action != "trash"
                else "keep"
            )

            importance = ai_importance

        elif user_tier == "low":

            final_action = (
                "archive"
                if ai_action == "keep"
                else ai_action
            )

            importance = min(ai_importance, 3)

        else:  # ignore

            final_action = "trash"
            importance = 1

        # =====================================================
        # AUTO CLEANUP FOR OLD EMAILS
        # =====================================================
        if cat and meta["received"]:

            age_days = (
                datetime.now(timezone.utc)
                - meta["received"]
            ).days

            if (
                cat.default_action == "trash"
                or (
                    cat.default_action == "archive"
                    and age_days >= 30
                    and importance <= 2
                )
            ):
                final_action = "trash"

        # =====================================================
        # LABELS
        # =====================================================
        label_ids = []

        try:

            # Main category label
            if cat:
                label_ids.append(
                    ensure_label(svc, cat.short_label)
                )

            # MyOrg label
            if (
                org_domain
                and sender_domain == org_domain
                and myorg_cat
            ):
                label_ids.append(
                    ensure_label(svc, myorg_cat.short_label)
                )

            # Urgent label
            if is_urgent and urgent_cat:
                label_ids.append(
                    ensure_label(svc, urgent_cat.short_label)
                )

            # Optional tier labels
            if user_tier == "critical":
                label_ids.append(
                    ensure_label(svc, "Critical")
                )

            elif user_tier == "important":
                label_ids.append(
                    ensure_label(svc, "Important")
                )

            apply_labels(
                svc,
                m["id"],
                label_ids
            )

        except Exception:
            pass

        # =====================================================
        # ACTION EXECUTION
        # =====================================================
        try:

            if final_action == "trash":

                trash_message(svc, m["id"])

            elif final_action == "archive":

                svc.users().messages().modify(
                    userId="me",
                    id=m["id"],
                    body={
                        "removeLabelIds": ["INBOX"]
                    }
                ).execute()

        except Exception:
            pass

        # =====================================================
        # SAVE DATABASE
        # =====================================================
        ClassifiedEmail.objects.update_or_create(
            user=user,
            gmail_id=m["id"],
            defaults={

                "thread_id": meta["thread_id"],

                "subject": meta["subject"][:500],

                "sender": meta["from"][:300],

                "sender_email": meta["from_email"],

                "snippet": meta["snippet"],

                "received_at": meta["received"],

                "category": cat,

                "importance": importance,

                "is_urgent": is_urgent,

                "reason": data.get("reason", ""),

                "action_taken": (
                    "trashed"
                    if final_action == "trash"
                    else (
                        "archived"
                        if final_action == "archive"
                        else "labeled"
                    )
                ),

                "is_event": bool(
                    data.get("is_event", False)
                ),

                "event_when": (
                    (data.get("event_when") or "")[:120]
                ),

                "unsubscribe_url": (
                    meta["unsubscribe_url"][:1000]
                    if meta.get("unsubscribe_url")
                    else ""
                ),
            },
        )

        processed.append(meta["id"])

    return {
        "scanned": len(msgs),
        "already_done": len(done),
        "newly_processed": len(processed),
    }

def list_by_query(user, query, max_results=100):
    """Generic Gmail query → metadata list. Used for Trash/Spam/Starred pages."""
    svc = gmail_service(user)
    out, token = [], None
    while len(out) < max_results:
        resp = svc.users().messages().list(
            userId="me", q=query,
            maxResults=min(100, max_results - len(out)), pageToken=token,
        ).execute()
        for m in resp.get("messages", []):
            out.append(get_message_meta(svc, m["id"]))
        token = resp.get("nextPageToken")
        if not token: break
    return out


def suggest_relevant_categories(profile, max_count=20):
    """Use AI to pick the most relevant categories for this user."""
    if _openai is None or not profile:
        return []

    cats = list(EmailCategory.objects.exclude(slug__in=["urgent", "myorg"]))
    cats_listing = "\n".join(f"- {c.slug}: {c.name} ({c.group})" for c in cats)

    prompt = f"""You are helping an email-triage app personalize onboarding.
Given the user's profile, pick the {max_count} email categories they most likely care about.

USER PROFILE
Role: {profile.get_current_role_display()}
Position: {profile.current_position or 'N/A'}
Organization: {profile.current_organization or 'N/A'}
Education: {profile.education or 'N/A'}
Experience: {profile.experience or 'N/A'}
Skills/Interests: {profile.skills_interests or 'N/A'}
Target roles: {profile.target_roles or 'N/A'}
Industries: {profile.industries or 'N/A'}
Email type: {profile.get_email_type_display()}
Extra: {profile.additional_context or 'N/A'}

CATEGORIES (slug: name (group))
{cats_listing}

Pick {max_count} slugs that this specific user will most benefit from customizing.
Always include important universal ones (2fa, fraud, breach if security relevant).
Skip obviously irrelevant ones for their role.

Respond with ONLY valid JSON: {{"slugs": ["slug1", "slug2", ...]}}
"""
    try:
        resp = _openai.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        data = json.loads(resp.choices[0].message.content)
        slugs = data.get("slugs", [])
        return list(EmailCategory.objects.filter(slug__in=slugs))
    except Exception as exc:
        print(f"AI suggest failed: {exc}")
        # Fallback: return important + critical default ones
        return list(EmailCategory.objects.filter(default_tier__in=["critical", "important"])[:max_count])