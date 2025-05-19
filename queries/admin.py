from django.contrib import admin
from queries.models import UserQuery, HotTopic

@admin.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "created_at")
    search_fields = ("user__email", "question")
    list_filter = ("created_at",)


@admin.register(HotTopic)
class HotTopicAdmin(admin.ModelAdmin):
    list_display = ("age_group", "created_at")
    list_filter = ("age_group", "created_at")