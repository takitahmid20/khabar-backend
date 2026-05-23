from django.contrib import admin

from apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "mobile", "role", "is_staff")
    search_fields = ("email", "mobile")
