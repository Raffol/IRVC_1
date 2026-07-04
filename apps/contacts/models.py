"""
Заявки из формы обратной связи на странице /contacts/.
"""
from django.db import models


class ContactMessage(models.Model):
    name = models.CharField('Имя', max_length=200)
    contact = models.CharField('Email или телефон', max_length=200)
    message = models.TextField('Сообщение', max_length=500)
    created_at = models.DateTimeField('Получено', auto_now_add=True)
    is_processed = models.BooleanField('Обработано', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка из формы'
        verbose_name_plural = 'Заявки из формы'

    def __str__(self):
        return f'{self.name} — {self.created_at:%d.%m.%Y}'
