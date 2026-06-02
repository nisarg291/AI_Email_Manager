from django.core.management.base import BaseCommand
from accounts.models import EmailCategory

# CATEGORIES = [
#     # group, slug, name, short_label, default_action, description
#     ("Urgent",        "urgent",             "Urgent / Time-sensitive",     "Urgent",     "keep",    "Needs action within 24-48 hours"),
#     ("Work",          "myorg",              "My Organization",             "MyOrg",      "keep",    "Emails from your current company"),
#     ("Work",          "work_internal",      "Internal Team",               "Work",       "keep",    "Colleagues, project threads"),
#     ("Work",          "work_client",        "Client / Vendor",             "Client",     "keep",    "External business contacts"),
#     ("Work",          "calendar_meeting",   "Meetings & Calendar",         "Meeting",    "keep",    "Calendar invites, agendas"),
#     ("Jobs",          "job_application",    "Job Applications",            "Jobs",       "keep",    "Confirmations, statuses"),
#     ("Jobs",          "recruiter",          "Recruiter Outreach",          "Recruiter",  "keep",    "Cold outreach from recruiters"),
#     ("Jobs",          "interview",          "Interview Invitations",       "Interview",  "keep",    "Interview scheduling"),
#     ("Jobs",          "assessment",         "Assessments / Tests",         "Assessment", "keep",    "Coding tests, take-homes"),
#     ("Jobs",          "offer_rejection",    "Offers & Rejections",         "Offer",      "keep",    "Offer letters, rejections"),
#     ("Personal",      "personal",           "Friends & Family",            "Personal",   "keep",    "Personal correspondence"),
#     ("Finance",       "finance",            "Bills, Banking & Receipts",   "Finance",    "keep",    "Invoices, statements, taxes"),
#     ("Travel",        "travel",             "Travel & Bookings",           "Travel",     "keep",    "Flights, hotels, itineraries"),
#     ("Education",     "education",          "Education & Learning",        "Education",  "keep",    "Courses, deadlines, classes"),
#     ("Health",        "health",             "Health & Insurance",          "Health",     "keep",    "Appointments, insurance"),
#     ("Events",        "events_invites",     "Events & Invitations",        "Event",      "keep",    "RSVPs, webinars"),
#     ("Notifications", "social",             "Social Media",                "Social",     "archive", "LinkedIn, Twitter, etc."),
#     ("Notifications", "transactional",      "Orders & Shipping",           "Order",      "keep",    "Order confirmations, deliveries"),
#     ("Notifications", "account_security",   "Account & Security",          "Security",   "keep",    "2FA codes, password resets"),
#     ("Notifications", "service_updates",    "Service Updates",             "Update",     "archive", "Terms changes, outages"),
#     ("Marketing",     "promo_sales",        "Sales & Discounts",           "Promo",      "trash",   "Promotional offers"),
#     ("Marketing",     "brand_newsletter",   "Brand Newsletters",           "Newsletter", "archive", "Brand updates, digests"),
#     ("Marketing",     "product_launch",     "Product Launches",            "Product",    "archive", "Feature announcements"),
#     ("Subscriptions", "newsletter_content", "Editorial Newsletters",       "Reading",    "archive", "Substack, news, blogs"),
#     ("Subscriptions", "forums_community",   "Forums & Communities",        "Forum",      "archive", "StackOverflow, GitHub, Reddit"),
#     ("Spam",          "spam_phishing",      "Spam & Phishing",             "Junk",       "trash",   "Phishing, scams, junk"),
# ]
# class Command(BaseCommand):
#     help = "Seed (or refresh) the EmailCategory table with short labels."

#     def handle(self, *args, **opts):
#         for group, slug, name, short, action, desc in CATEGORIES:
#             EmailCategory.objects.update_or_create(
#                 slug=slug,
#                 defaults={"name": name, "short_label": short, "group": group,
#                           "default_action": action, "description": desc},
#             )
#         self.stdout.write(self.style.SUCCESS(f"Seeded {len(CATEGORIES)} categories."))


CATEGORIES = [

    # =========================================================
    # System / Fixed
    # =========================================================
    ("System", "urgent",                    "Urgent / Time-sensitive",      "Urgent",       "critical",  "Action needed in 24-48h"),
    ("System", "myorg",                     "My Organization",              "MyOrg",        "important", "Emails from your company domain"),

    # =========================================================
    # Work — General
    # =========================================================
    ("Work — General", "internal_team",     "Internal Team",                "Team",         "important", "Colleagues and project discussions"),
    ("Work — General", "cross_team",        "Cross-team",                   "CrossTeam",    "important", "Cross-functional collaboration"),
    ("Work — General", "exec_leadership",   "Executive / Leadership",       "Exec",         "critical",  "Leadership or management communication"),
    ("Work — General", "project_update",    "Project Updates",              "Project",      "normal",    "Project status updates"),
    ("Work — General", "approval_needed",   "Approval Needed",              "Approve",      "important", "Requests requiring approval"),
    ("Work — General", "decision_needed",   "Decision Needed",              "Decision",     "important", "Requires business decision"),
    ("Work — General", "meeting_notes",     "Meeting Notes",                "Notes",        "normal",    "Meeting summaries and recaps"),
    ("Work — General", "action_item",       "Action Items",                 "Todo",         "important", "Tasks assigned to you"),
    ("Work — General", "fyi_work",          "FYI / Informational",          "FYI",          "low",       "No immediate action required"),

    # =========================================================
    # Work — Collaboration
    # =========================================================
    ("Work — Collaboration", "slack_mentions",  "Slack Mentions",           "Slack",        "normal",    "Slack mentions or replies"),
    ("Work — Collaboration", "jira_update",     "Jira Updates",             "Jira",         "normal",    "Issue tracking notifications"),
    ("Work — Collaboration", "task_assignment", "Task Assignment",          "Task",         "important", "Assigned tasks"),
    ("Work — Collaboration", "document_review", "Document Review",          "Review",       "important", "Document review requests"),
    ("Work — Collaboration", "file_shared",     "File Shared",              "File",         "normal",    "Shared files or folders"),

    # =========================================================
    # Work — Operations
    # =========================================================
    ("Work — Operations", "incident_alert",     "Incident / Outage",        "Incident",     "critical",  "System outage or incidents"),
    ("Work — Operations", "deployment",         "Deployment",               "Deploy",       "important", "Deployment notifications"),
    ("Work — Operations", "system_monitoring",  "System Monitoring",        "Monitor",      "important", "Infrastructure alerts"),
    ("Work — Operations", "maintenance",        "Maintenance Window",       "Maint",        "normal",    "Scheduled maintenance notifications"),

    # =========================================================
    # Work — Customer
    # =========================================================
    ("Work — Customer", "client",               "Client / Customer",        "Client",       "important", "Customer communication"),
    ("Work — Customer", "prospect",             "Prospect / Lead",          "Prospect",     "important", "Potential customers"),
    ("Work — Customer", "support_ticket",       "Support Ticket",           "Support",      "important", "Customer support requests"),
    ("Work — Customer", "complaint",            "Complaint / Escalation",   "Complaint",    "critical",  "Escalated customer issue"),
    ("Work — Customer", "renewal",              "Renewal",                  "Renewal",      "important", "Subscription or contract renewal"),
    ("Work — Customer", "upsell",               "Upsell / Expansion",       "Upsell",       "normal",    "Expansion opportunities"),
    ("Work — Customer", "customer_onboard",     "Customer Onboarding",      "Onboard",      "important", "New customer onboarding"),
    ("Work — Customer", "feedback",             "Customer Feedback",        "Feedback",     "normal",    "Customer reviews and feedback"),

    # =========================================================
    # Work — Vendor
    # =========================================================
    ("Work — Vendor", "vendor",                 "Vendor / Partner",         "Vendor",       "normal",    "Vendor communication"),
    ("Work — Vendor", "contract",               "Contract",                 "Contract",     "important", "Contracts and agreements"),
    ("Work — Vendor", "vendor_invoice",         "Vendor Invoice",           "VInvoice",     "important", "Invoices from vendors"),
    ("Work — Vendor", "saas_billing",           "SaaS Billing",             "SaaS",         "low",       "Software subscription billing"),

    # =========================================================
    # Work — HR
    # =========================================================
    ("Work — HR", "hr",                         "HR — General",             "HR",           "important", "HR communication"),
    ("Work — HR", "recruiting",                 "Recruiting",               "Recruit",      "important", "Hiring and recruitment"),
    ("Work — HR", "employee_onboard",           "Employee Onboarding",      "EmpOnboard",   "important", "New employee onboarding"),
    ("Work — HR", "performance",                "Performance / Review",     "Perf",         "important", "Performance reviews"),
    ("Work — HR", "benefits_payroll",           "Benefits / Payroll",       "Payroll",      "important", "Payroll and benefits"),
    ("Work — HR", "policy_update",              "Policy Update",            "Policy",       "low",       "Company policy updates"),

    # =========================================================
    # Jobs / Career
    # =========================================================
    ("Jobs", "job_applied",                     "Applied Jobs",             "Applied",      "important", "Application confirmations"),
    ("Jobs", "application_update",              "Application Update",       "AppUpdate",    "important", "Application progress updates"),
    ("Jobs", "recruiter",                       "Recruiter Outreach",       "Recruiter",    "important", "Recruiter communication"),
    ("Jobs", "interview",                       "Interview Invitations",    "Interview",    "critical",  "Interview scheduling"),
    ("Jobs", "assessment",                      "Assessments",              "Assessment",   "critical",  "Coding tests and assessments"),
    ("Jobs", "take_home",                       "Take-home Tasks",          "TakeHome",     "critical",  "Assignments with deadlines"),
    ("Jobs", "offer",                           "Offer",                    "Offer",        "critical",  "Job offers"),
    ("Jobs", "salary_negotiation",              "Salary Negotiation",       "Salary",       "important", "Compensation discussions"),
    ("Jobs", "background_check",                "Background Check",         "BGCheck",      "important", "Verification processes"),
    ("Jobs", "reference_check",                 "Reference Check",          "RefCheck",     "important", "Reference verification"),
    ("Jobs", "onboarding",                      "Onboarding",               "Onboarding",   "important", "Joining process"),
    ("Jobs", "job_discovery",                   "Job Discovery / Alerts",   "JobAlert",     "normal",    "Job alerts and recommendations"),
    ("Jobs", "networking",                      "Networking",               "Network",      "normal",    "Professional networking"),
    ("Jobs", "career_event",                    "Career Event",             "CareerEvt",    "normal",    "Career fairs and hiring events"),
    ("Jobs", "visa_sponsorship",                "Visa Sponsorship",         "Visa",         "important", "Immigration sponsorship"),
    ("Jobs", "rejection",                       "Rejection",                "Reject",       "low",       "Application rejection"),

    # =========================================================
    # Finance — Personal
    # =========================================================
    ("Finance — Personal", "bank",              "Banking",                  "Bank",         "important", "Bank accounts and statements"),
    ("Finance — Personal", "credit_card",       "Credit Card",              "Card",         "important", "Credit card activity"),
    ("Finance — Personal", "investment",        "Investments",              "Invest",       "important", "Investment updates"),
    ("Finance — Personal", "tax",               "Tax",                      "Tax",          "critical",  "Tax documents and filings"),
    ("Finance — Personal", "bill",              "Bills / Utilities",        "Bill",         "important", "Recurring bills"),
    ("Finance — Personal", "payment_due",       "Payment Due",              "Due",          "critical",  "Upcoming payment deadlines"),
    ("Finance — Personal", "payment_received",  "Payment Received",         "Received",     "normal",    "Received payments"),
    ("Finance — Personal", "fraud_alert",       "Fraud Alert",              "Fraud",        "critical",  "Suspicious account activity"),
    ("Finance — Personal", "receipt",           "Receipt",                  "Receipt",      "low",       "Purchase receipts"),
    ("Finance — Personal", "refund",            "Refund",                   "Refund",       "normal",    "Refund notifications"),
    ("Finance — Personal", "insurance",         "Insurance",                "Insurance",    "important", "Insurance communication"),
    ("Finance — Personal", "subscription_renewal","Subscription Renewal",  "Renewal",      "normal",    "Recurring subscription renewals"),
    ("Finance — Personal", "crypto",            "Crypto",                   "Crypto",       "normal",    "Crypto wallet or exchange alerts"),

    # =========================================================
    # Finance — Business
    # =========================================================
    ("Finance — Business", "invoice_out",       "Invoice Sent",             "InvoiceOut",   "important", "Invoices sent"),
    ("Finance — Business", "invoice_in",        "Invoice Received",         "InvoiceIn",    "important", "Invoices received"),
    ("Finance — Business", "purchase_order",    "Purchase Order",           "PO",           "important", "Purchase order workflows"),
    ("Finance — Business", "expense_report",    "Expense Report",           "Expense",      "important", "Expense reimbursement"),
    ("Finance — Business", "stripe_payments",   "Payments Processor",       "Payments",     "important", "Stripe/PayPal/Square alerts"),
    ("Finance — Business", "accounting",        "Accounting",               "Accounting",   "important", "Business accounting"),

    # =========================================================
    # Calendar / Events
    # =========================================================
    ("Calendar", "meeting_invite",              "Meeting Invite",           "Meeting",      "important", "Meeting invitations"),
    ("Calendar", "reschedule",                  "Reschedule",               "Reschedule",   "important", "Meeting rescheduling"),
    ("Calendar", "cancellation",                "Cancellation",             "Cancelled",    "important", "Meeting cancellations"),
    ("Calendar", "reminder",                    "Reminder",                 "Reminder",     "important", "Event or task reminders"),
    ("Calendar", "availability_request",        "Availability Request",     "Avail",        "normal",    "Scheduling coordination"),
    ("Calendar", "booking_confirmation",        "Booking Confirmation",     "Booking",      "normal",    "Appointment confirmations"),
    ("Calendar", "conference",                  "Conference",               "Conference",   "normal",    "Conference invitations"),
    ("Calendar", "webinar",                     "Webinar",                  "Webinar",      "low",       "Online events"),
    ("Calendar", "rsvp",                        "RSVP",                     "RSVP",         "normal",    "Event responses"),

    # =========================================================
    # Travel
    # =========================================================
    ("Travel", "flight",                        "Flight",                   "Flight",       "critical",  "Flights and boarding passes"),
    ("Travel", "hotel",                         "Hotel",                    "Hotel",        "important", "Hotel bookings"),
    ("Travel", "itinerary",                     "Itinerary",                "Itinerary",    "important", "Travel itineraries"),
    ("Travel", "travel_alert",                  "Travel Alert",             "TravelAlert",  "important", "Flight or travel changes"),
    ("Travel", "visa",                          "Visa / Immigration",       "Visa",         "critical",  "Visa and immigration updates"),
    ("Travel", "car_ride",                      "Car / Ride",               "Ride",         "normal",    "Ride-sharing and rentals"),
    ("Travel", "trip_planning",                 "Trip Planning",            "Trip",         "normal",    "Travel planning"),
    ("Travel", "loyalty_program",               "Loyalty Program",          "Rewards",      "low",       "Travel rewards"),

    # =========================================================
    # Education
    # =========================================================
    ("Education", "course_update",              "Course Update",            "Course",       "important", "Course announcements"),
    ("Education", "assignment",                 "Assignment",               "Homework",     "critical",  "Assignments and deadlines"),
    ("Education", "exam",                       "Exam / Test",              "Exam",         "critical",  "Exam schedules"),
    ("Education", "grade",                      "Grade",                    "Grade",        "important", "Grades and results"),
    ("Education", "admission",                  "Admission",                "Admission",    "critical",  "Admission decisions"),
    ("Education", "certificate",                "Certificate",              "Cert",         "normal",    "Certificates and completions"),
    ("Education", "tuition_scholarship",        "Tuition / Scholarship",    "Tuition",      "important", "Tuition and aid"),
    ("Education", "research",                   "Research",                 "Research",     "normal",    "Research collaboration"),
    ("Education", "mentor",                     "Mentor / Advisor",         "Mentor",       "important", "Advisor communication"),

    # =========================================================
    # Health
    # =========================================================
    ("Health", "health_appointment",        "Appointment",               "Appt",         "important", "Doctor and clinic appointments"),
    ("Health", "lab_result",                "Lab / Test Result",         "Lab",          "important", "Medical test results"),
    ("Health", "prescription",              "Prescription",              "Rx",           "important", "Medication and prescription updates"),
    ("Health", "insurance_claim",           "Insurance Claim",           "Claim",        "important", "Health insurance claims"),
    ("Health", "fitness",                   "Fitness / Wellness",        "Fitness",      "low",       "Fitness apps and wellness programs"),

    # =========================================================
    # Personal
    # =========================================================
    ("Personal", "family",                  "Family",                    "Family",       "important", "Family communication"),
    ("Personal", "friend",                  "Friends",                   "Friends",      "important", "Personal friend communication"),
    ("Personal", "romantic",                "Romantic",                  "Romantic",     "important", "Partner or dating communication"),
    ("Personal", "government",              "Government",                "Gov",          "important", "Official government communication"),
    ("Personal", "legal",                   "Legal",                     "Legal",        "important", "Legal matters and lawyers"),
    ("Personal", "immigration",             "Immigration",               "Immigration",  "critical",  "PR, visa, citizenship"),
    ("Personal", "real_estate",             "Real Estate / Housing",     "Housing",      "important", "Housing, rent, mortgage"),
    ("Personal", "shopping",                "Shopping",                  "Shopping",     "low",       "Shopping confirmations"),
    ("Personal", "delivery",                "Delivery",                  "Delivery",     "normal",    "Package delivery updates"),
    ("Personal", "appointment",             "Personal Appointment",      "PAppointment", "important", "Salon, repair, service bookings"),
    ("Personal", "subscription",            "Subscription",              "Sub",          "low",       "Membership and subscription renewals"),

    # =========================================================
    # Community
    # =========================================================
    ("Community", "volunteer",              "Volunteer",                 "Volunteer",    "low",       "Volunteer organizations"),
    ("Community", "mailing_list",           "Mailing List",              "List",         "low",       "Community or group mailing lists"),

    # =========================================================
    # Content & Learning
    # =========================================================
    ("Content", "newsletter_industry",      "Industry Newsletter",       "IndustryNL",   "normal",    "Industry and tech newsletters"),
    ("Content", "newsletter_lifestyle",     "Lifestyle Newsletter",      "LifeNL",       "low",       "Lifestyle and hobby newsletters"),
    ("Content", "blog_digest",              "Blog Digest",               "Blog",         "low",       "Blog and article digests"),
    ("Content", "news_alert",               "News Alert",                "News",         "low",       "Breaking news alerts"),

    # =========================================================
    # Notifications
    # =========================================================
    ("Notifications", "social_linkedin",    "LinkedIn",                  "LinkedIn",     "low",       "LinkedIn notifications"),
    ("Notifications", "social_other",       "Social Media",              "Social",       "low",       "Twitter, Facebook, Instagram"),
    ("Notifications", "github",             "GitHub / Code",             "GitHub",       "normal",    "Repository and PR notifications"),
    ("Notifications", "ci_cd",              "CI / CD",                   "CI",           "low",       "Build and deployment alerts"),
    ("Notifications", "productivity_tool",  "Productivity Tool",         "Tool",         "low",       "Slack, Notion, Jira, Asana"),
    ("Notifications", "service_update",     "Service Update",            "Update",       "low",       "Feature or outage notifications"),
    ("Notifications", "order_shipping",     "Order / Shipping",          "Order",        "normal",    "Shipping and tracking updates"),
    ("Notifications", "ai_tool",            "AI Tool Notifications",     "AI",           "low",       "AI platform notifications"),
    ("Notifications", "domain_hosting",     "Domain / Hosting",          "Hosting",      "important", "Hosting, SSL, DNS alerts"),
    ("Notifications", "app_update",         "App Update",                "AppUpdate",    "low",       "Software and app updates"),
    ("Notifications", "storage_alert",      "Storage Alert",             "Storage",      "low",       "Cloud or storage quota warnings"),

    # =========================================================
    # Security
    # =========================================================
    ("Security", "two_fa",                  "2FA / Verification",        "2FA",          "critical",  "OTP and verification codes"),
    ("Security", "login_alert",             "Login Alert",               "Login",        "important", "New login or device alerts"),
    ("Security", "device_alert",            "Device Security Alert",     "Device",       "important", "Unknown or suspicious device access"),
    ("Security", "password_reset",          "Password Reset",            "Password",     "important", "Password reset requests"),
    ("Security", "breach",                  "Breach / Alert",            "Breach",       "critical",  "Security breaches or incidents"),
    ("Security", "security_report",         "Security Report",           "SecReport",    "important", "Security summary reports"),
    ("Security", "access_request",          "Access Request",            "Access",       "important", "Permission/access approvals"),
    ("Security", "compliance",              "Compliance",                "Compliance",   "important", "Policy or compliance notifications"),

    # =========================================================
    # Marketing
    # =========================================================
    ("Marketing", "promo",                  "Promo / Discount",          "Promo",        "ignore",    "Sales and discount promotions"),
    ("Marketing", "newsletter",             "Marketing Newsletter",      "Newsletter",   "ignore",    "Promotional newsletters"),
    ("Marketing", "product_update",         "Product / Feature Update",  "Product",      "low",       "Product launches and features"),
    ("Marketing", "event_promo",            "Event / Webinar Promo",     "EventPromo",   "ignore",    "Marketing events and webinars"),
    ("Marketing", "survey",                 "Survey / Feedback",         "Survey",       "ignore",    "Feedback and survey requests"),
    ("Marketing", "trial_offer",            "Trial / Upgrade Offer",     "Trial",        "ignore",    "Trials and upgrade promotions"),

    # =========================================================
    # Documents / Signatures
    # =========================================================
    ("Documents", "esign_request",          "E-sign Request",            "ESign",        "important", "Electronic signature requests"),
    ("Documents", "document_expiry",        "Document Expiry",           "Expiry",       "critical",  "Passport/license expiry alerts"),
    ("Documents", "document_generated",     "Document Generated",        "Document",     "normal",    "Generated reports/statements"),

    # =========================================================
    # Delivery / Mail System
    # =========================================================
    ("Delivery", "email_bounce",            "Email Bounce",              "Bounce",       "important", "Delivery failure notifications"),
    ("Delivery", "delivery_failure",        "Delivery Failure",          "DeliveryFail", "important", "Package/mail delivery issue"),
    ("Delivery", "mailbox_storage",         "Mailbox Storage",           "Storage",      "normal",    "Mailbox quota warnings"),
    ("Delivery", "auto_reply",              "Auto Reply / OOO",          "OOO",          "low",       "Out-of-office responses"),

    # =========================================================
    # Follow-ups
    # =========================================================
    ("FollowUp", "follow_up_needed",        "Follow-up Needed",          "FollowUp",     "important", "Requires follow-up action"),
    ("FollowUp", "pending_response",        "Pending Response",          "Pending",      "important", "Awaiting your reply"),
    ("FollowUp", "no_response",             "No Response",               "NoReply",      "low",       "Inactive conversation"),

    # =========================================================
    # E-commerce
    # =========================================================
    ("Ecommerce", "wishlist",               "Wishlist Update",           "Wishlist",     "low",       "Wishlist stock or price updates"),
    ("Ecommerce", "return_exchange",        "Return / Exchange",         "Return",       "important", "Return and exchange processing"),

    # =========================================================
    # Spam
    # =========================================================
    ("Spam", "phishing",                    "Phishing / Credential Scam","Phishing",    "ignore",    "Credential theft attempts"),
    ("Spam", "financial_scam",              "Financial / Investment Scam","Fraud",      "ignore",    "Fake banking or investment scams"),
    ("Spam", "fake_job",                    "Fake Job / Recruiter Scam", "JobScam",     "ignore",    "Fraudulent job opportunities"),
    ("Spam", "malware",                     "Malware / Dangerous Link",  "Malware",     "ignore",    "Malicious links or attachments"),
    ("Spam", "spoofing",                    "Spoofed Sender",            "Spoof",       "ignore",    "Impersonated sender/domain"),
    ("Spam", "bulk_spam",                   "Bulk Spam / Junk",          "Junk",        "ignore",    "Mass unsolicited email"),
    ("Spam", "adult_gambling",              "Adult / Gambling Spam",     "AdultSpam",   "ignore",    "Adult or betting spam"),

]

class Command(BaseCommand):
    help = "Seed (or refresh) the EmailCategory table."

    def handle(self, *args, **opts):
        for group, slug, name, short, tier, desc in CATEGORIES:
            EmailCategory.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "short_label": short, "group": group,
                          "default_tier": tier, "description": desc},
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(CATEGORIES)} categories."))


        