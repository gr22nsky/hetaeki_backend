# Celery 자동 로딩을 위한 초기화
from .celery import app as celery_app

__all__ = ['celery_app']
