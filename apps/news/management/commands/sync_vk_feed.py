"""
Команда для ручного или периодического (cron) вызова.

Использование:
    python manage.py sync_vk_feed
    python manage.py sync_vk_feed --count 50
"""
from django.core.management.base import BaseCommand

from apps.news.vk_sync import sync_vk_feed


class Command(BaseCommand):
    help = 'Забирает последние посты из группы ВКонтакте и сохраняет их в базу.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=20, help='Сколько постов забирать (по умолчанию 20).')

    def handle(self, *args, **options):
        result = sync_vk_feed(count=options['count'])

        if result['skipped_reason']:
            self.stdout.write(self.style.WARNING(f'Пропущено: {result["skipped_reason"]}'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Готово. Создано: {result["created"]}, обновлено: {result["updated"]}'
            ))
