from celery import shared_task
from documents.scripts.collector import collect_documents

@shared_task
def run_collector_central():
    """중앙정부 복지 정책 수집 태스크."""
    collect_documents("central")

@shared_task
def run_collector_local():
    """지자체 복지 정책 수집 태스크."""
    collect_documents("local")
