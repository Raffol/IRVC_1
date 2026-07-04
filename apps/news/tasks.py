"""
Celery-задачи приложения news.

Расписание задаётся в БД через django_celery_beat.
См. management-команду setup_periodic_tasks — она создаёт задачу
«синхронизировать VK раз в 15 минут».
"""
from celery import shared_task

from .vk_sync import sync_vk_feed as _sync_vk_feed


@shared_task(name='news.sync_vk_feed', bind=True, max_retries=3, default_retry_delay=60)
def sync_vk_feed_task(self, count=20):
    """
    Забирает свежие посты из группы ВК и сохраняет в БД.

    :param count: сколько постов забирать (по умолчанию 20).
    :return: словарь {'created': N, 'updated': M, 'skipped_reason': str|None}
    """
    try:
        return _sync_vk_feed(count=count)
    except Exception as exc:
        raise self.retry(exc=exc)
