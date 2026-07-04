"""
Модель поста из ВКонтакте.

Заполняется автоматически management-командой sync_vk_feed
(её можно поставить в cron/Celery Beat).
"""
from django.db import models


class VkPost(models.Model):
    vk_id = models.CharField('ID в ВК', max_length=64, unique=True)
    title = models.CharField(
        'Заголовок', max_length=200, blank=True,
        help_text='Автоматически берётся из первой строки текста.',
    )
    text = models.TextField('Текст поста', blank=True)
    image = models.URLField(
        'URL картинки', max_length=500, blank=True,
        help_text='Первая картинка из вложений поста.',
    )
    url = models.URLField('Ссылка на пост в ВК', max_length=500)
    published_at = models.DateTimeField('Дата публикации')
    likes = models.PositiveIntegerField('Лайков', default=0)
    comments = models.PositiveIntegerField('Комментариев', default=0)
    is_visible = models.BooleanField(
        'Показывать на сайте', default=True,
        help_text='Снимите галочку, чтобы скрыть пост, не удаляя его.',
    )

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Пост ВК'
        verbose_name_plural = 'Лента ВК'

    def __str__(self):
        return self.title or self.text[:60]
