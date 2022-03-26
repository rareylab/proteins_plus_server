"""Loads the celery app any time proteins_plus is imported"""
from .celery import app as celery_app

__all__ = ('celery_app',)
