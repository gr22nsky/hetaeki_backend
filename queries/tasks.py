from celery import shared_task
from queries.scripts.generate_hottopic import generate_top5_topics


@shared_task
def daily_generate_hot_topics():
    generate_top5_topics()
