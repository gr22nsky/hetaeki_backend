from celery import shared_task
from documents.scripts.collector import collect_documents

@shared_task
def run_collector_central():
    collect_documents("central")

@shared_task
def run_collector_local():
    collect_documents("local")
