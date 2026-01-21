import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import get_valid_filename

from src.users.enums import LegalCompany


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
    legal_company_referrer = models.CharField(
        max_length=50,
        choices=[(company.value, company.name) for company in LegalCompany],
        null=True,
        blank=True,
        help_text="Legal company that referred this user"
    )

    def get_legal_company_referrer(self):
        """Returns the legal company referrer, defaulting to JP_LEGAL if null"""
        return self.legal_company_referrer or LegalCompany.JP_LEGAL.value
