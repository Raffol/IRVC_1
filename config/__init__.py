# Импорт Celery-приложения при старте Django,
# чтобы shared_task-декораторы могли зарегистрироваться в правильном контексте.
from .celery import app as celery_app

__all__ = ('celery_app',)
