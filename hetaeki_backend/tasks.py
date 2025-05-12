from celery import shared_task
from documents.bokjiro_task import bokjiro_update

@shared_task
def update_bokjiro():
    bokjiro_update()
