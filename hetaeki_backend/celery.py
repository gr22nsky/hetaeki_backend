import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hetaeki_backend.settings')

# Celery 인스턴스 생성 및 설정
app = Celery('hetaeki_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
