from django.urls import path
from . import views

urlpatterns = [
    path("login/",            views.login_page,      name="login"),
    path("google/start/",     views.google_start,    name="google_start"),
    path("google/callback/",  views.google_callback, name="google_callback"),
    path("logout/",           views.logout_view,     name="logout"),

    path("dashboard/",        views.dashboard,       name="dashboard"),
    path("profile/",          views.profile_view,    name="profile"),

    path("emails/",           views.manage_emails,   name="manage_emails"),
    path("emails/live/toggle/", views.toggle_live,   name="toggle_live"),
    path("urgent/",           views.urgent_view,     name="urgent"),
    path("action-needed/",    views.action_needed_view, name="action_needed"),
    path("important/",        views.important_view,  name="important"),

    path("subscriptions/",    views.subscriptions_view,           name="subscriptions"),
    path("subscriptions/block/<path:sender_email>/",   views.subscription_block,   name="subscription_block"),
    path("subscriptions/unblock/<path:sender_email>/", views.subscription_unblock, name="subscription_unblock"),

    path("spam/",             views.spam_view,       name="spam"),
    path("starred/",          views.starred_view,    name="starred"),

    path("trash/",            views.trash_view,      name="trash"),
    path("trash/empty/",      views.trash_empty,     name="trash_empty"),
    path("trash/<str:msg_id>/restore/", views.trash_restore, name="trash_restore"),
    path("trash/<str:msg_id>/delete/",  views.trash_delete,  name="trash_delete"),

    path("email/<str:msg_id>/",               views.email_detail,        name="email_detail"),
    path("email/<str:msg_id>/trash/",         views.email_trash_action,  name="email_trash_action"),
    path("email/<str:msg_id>/delete/",        views.email_delete_action, name="email_delete_action"),
    path("emails/bulk/",                      views.bulk_action,         name="bulk_action"),
    path("onboarding/step1/", views.onboarding_step1, name="onboarding_step1"),
    path("onboarding/step2/", views.onboarding_step2, name="onboarding_step2"),
    path("onboarding/step3/", views.onboarding_step3, name="onboarding_step3"),
    path("categories/",       views.categories_view,  name="categories"),
    path("jobs/<int:job_id>/status/", views.job_status,  name="job_status"),
    path("jobs/<int:job_id>/cancel/", views.cancel_job,  name="cancel_job"),

    path("labels/",           views.labels_view,      name="labels"),
    path("manage-labels/",    views.manage_labels_view, name="manage_labels"),
    path("delete-emails/",    views.delete_emails_view, name="delete_emails"),
    path("email/<str:msg_id>/star/",        views.toggle_star,     name="toggle_star"),
    path("email/<str:msg_id>/ai-reply/",   views.ai_reply_view,   name="ai_reply"),
    path("email/<str:msg_id>/send-reply/", views.send_reply_view, name="send_reply"),
    path("compose/ai/",   views.compose_ai_view,   name="compose_ai"),
    path("compose/send/", views.send_compose_view, name="send_compose"),
    path("sent/",              views.sent_view,             name="sent"),
    path("summary/",           views.summary_view,          name="email_summary"),
    path("summary/generate/",  views.generate_summary_view, name="generate_summary"),
    path("emails/poll/",       views.poll_emails,           name="poll_emails"),
]