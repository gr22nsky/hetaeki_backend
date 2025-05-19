from django.contrib import admin
from documents.models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "service_id", "source", "created_at")
    search_fields = ("title", "service_id")
    list_filter = ("source",)
