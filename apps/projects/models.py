"""
Модели раздела «Проекты».
"""
from django.db import models


class ProjectCategory(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('Ключ (для фильтра)', max_length=100, unique=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Категория проекта'
        verbose_name_plural = 'Категории проектов'

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('recruiting', 'Идёт набор'),
        ('archived', 'Архив'),
    ]

    title = models.CharField('Название', max_length=200)
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.PROTECT,
        related_name='projects', verbose_name='Категория',
    )
    lead = models.TextField('Краткое описание')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='active')

    # Три пары «значение — подпись» для показателей на карточке.
    stat_1_num = models.CharField('Показатель 1: значение', max_length=30, blank=True)
    stat_1_label = models.CharField('Показатель 1: подпись', max_length=60, blank=True)
    stat_2_num = models.CharField('Показатель 2: значение', max_length=30, blank=True)
    stat_2_label = models.CharField('Показатель 2: подпись', max_length=60, blank=True)
    stat_3_num = models.CharField('Показатель 3: значение', max_length=30, blank=True)
    stat_3_label = models.CharField('Показатель 3: подпись', max_length=60, blank=True)

    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.title

    def get_stats(self):
        """Список непустых показателей для отображения на карточке."""
        result = []
        for num, label in [
            (self.stat_1_num, self.stat_1_label),
            (self.stat_2_num, self.stat_2_label),
            (self.stat_3_num, self.stat_3_label),
        ]:
            if num and label:
                result.append({'num': num, 'label': label})
        return result
