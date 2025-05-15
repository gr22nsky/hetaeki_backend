from django.db import models

class Document(models.Model):
    service_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=20, choices=[("central", "중앙부처"), ("local", "지자체")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


