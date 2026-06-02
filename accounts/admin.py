from django.contrib import admin
from .models import GoogleAccount, UserProfile, EmailCategory, ClassifiedEmail

admin.site.register([GoogleAccount, UserProfile, EmailCategory, ClassifiedEmail])


# from django.contrib import admin
# from .models import UserProfile

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'gmail_permission_granted', 'created_at')
#     search_fields = ('user__email',)
#     list_filter = ('gmail_permission_granted', 'created_at')
