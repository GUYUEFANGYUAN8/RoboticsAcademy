"""Application configuration for the academy Django app."""

from django.apps import AppConfig


class AcademyConfig(AppConfig):
    """Django application metadata for Robotics Academy."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "academy"
