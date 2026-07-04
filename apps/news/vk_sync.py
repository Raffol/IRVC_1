"""
Синхронизация ленты постов из группы ВКонтакте.

Метод VK API: wall.get — https://dev.vk.com/method/wall.get
Логика вынесена из management-команды в отдельную функцию, чтобы её было
удобно вызывать из Celery-задачи (шаг 3) и тестировать.
"""
from datetime import datetime, timezone

import requests
from django.conf import settings

from apps.core.models import SiteSettings

from .models import VkPost


VK_WALL_GET_URL = 'https://api.vk.com/method/wall.get'


def sync_vk_feed(count=20, fetcher=None):
    """
    Забираем последние посты из группы ВК и сохраняем в БД.

    :param count: сколько постов забирать за один вызов.
    :param fetcher: функция для HTTP-запроса (для мокинга в тестах).
                    По умолчанию — requests.get.
    :return: словарь {'created': N, 'updated': M, 'skipped_reason': str|None}
    """
    site = SiteSettings.get_solo()

    if not site.vk_group_id:
        return {'created': 0, 'updated': 0, 'skipped_reason': 'vk_group_id не задан в настройках сайта'}
    if not settings.VK_SERVICE_TOKEN:
        return {'created': 0, 'updated': 0, 'skipped_reason': 'VK_SERVICE_TOKEN не задан в окружении'}

    fetcher = fetcher or requests.get

    response = fetcher(
        VK_WALL_GET_URL,
        params={
            'owner_id': f'-{site.vk_group_id}',
            'count': count,
            'access_token': settings.VK_SERVICE_TOKEN,
            'v': settings.VK_API_VERSION,
        },
        timeout=10,
    )
    data = response.json()

    if 'error' in data:
        return {'created': 0, 'updated': 0, 'skipped_reason': f'VK API error: {data["error"].get("error_msg", "unknown")}'}

    created = 0
    updated = 0

    for item in data.get('response', {}).get('items', []):
        vk_id = str(item['id'])
        text = item.get('text', '') or ''
        title = _extract_title(text)
        image = _first_photo_url(item)
        post_url = f'https://vk.com/wall-{site.vk_group_id}_{vk_id}'
        published_at = datetime.fromtimestamp(item['date'], tz=timezone.utc)

        _, was_created = VkPost.objects.update_or_create(
            vk_id=vk_id,
            defaults={
                'title': title,
                'text': text,
                'image': image,
                'url': post_url,
                'published_at': published_at,
                'likes': item.get('likes', {}).get('count', 0),
                'comments': item.get('comments', {}).get('count', 0),
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return {'created': created, 'updated': updated, 'skipped_reason': None}


def _extract_title(text):
    """Первая строка текста — заголовок, максимум 200 символов."""
    if not text:
        return ''
    first_line = text.split('\n', 1)[0].strip()
    return first_line[:200]


def _first_photo_url(item):
    """Ищем самый большой размер первой картинки во вложениях."""
    for attach in item.get('attachments', []):
        if attach.get('type') == 'photo':
            sizes = attach.get('photo', {}).get('sizes', [])
            if sizes:
                # sizes отсортированы от маленького к большому в VK API
                largest = max(sizes, key=lambda s: s.get('width', 0) * s.get('height', 0))
                return largest.get('url', '')
    return ''
