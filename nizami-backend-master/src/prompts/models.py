from django.db import models


class Prompt(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    value = models.TextField(null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
