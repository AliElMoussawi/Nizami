import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import get_valid_filename


def unique_file_path(instance, filename):
    base, ext = os.path.splitext(get_valid_filename(filename))
    return f"profile-images/{base}_{uuid.uuid4().hex}{ext}"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100, null=True)
    date_of_birth = models.DateField(null=True)
    job_title = models.CharField(max_length=100, null=True)
    role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('user', 'User')], default='user')
    company_name = models.CharField(max_length=100, null=True)
    profile_image = models.FileField(null=True, upload_to=unique_file_path)
    language = models.CharField(max_length=10, choices=[('en', 'English'), ('ar', 'Arabic')], default='ar')
