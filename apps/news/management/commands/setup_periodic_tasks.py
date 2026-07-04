"""
Настраивает периодическую задачу «синхронизировать VK каждые N минут».

Расписание хранится в БД (django_celery_beat), поэтому позже
можно менять частоту прямо в админке: /admin/django_celery_beat/periodictask/

Использование:
    python manage.py setup_periodic_tasks
    python manage.py setup_periodic_tasks --interval 30
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Создаёт или обновляет периодические задачи Celery Beat.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=15,
            help='Как часто синхронизироваться с ВК, в минутах (по умолчанию 15).',
        )

    def handle(self, *args, **options):
        interval_minutes = options['interval']

        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=interval_minutes,
            period=IntervalSchedule.MINUTES,
        )

        task, created = PeriodicTask.objects.update_or_create(
            name='Sync VK feed',
            defaults={
                'task': 'news.sync_vk_feed',
                'interval': schedule,
                'enabled': True,
            },
        )

        action = 'создана' if created else 'обновлена'
        self.stdout.write(self.style.SUCCESS(
            f'Задача «{task.name}» {action}. '
            f'Расписание: каждые {interval_minutes} мин.'
        ))
