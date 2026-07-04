"""
Модели раздела «Состав ИРВЦ».
"""
from django.db import models


class TeamGroup(models.Model):
    """Группа: Руководство, Координация, Обучение, Актив волонтёров."""

    name = models.CharField('Название группы', max_length=100)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Группа команды'
        verbose_name_plural = 'Группы команды'

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """Член команды. Привязан к группе."""

    group = models.ForeignKey(
        TeamGroup,
        on_delete=models.PROTECT,
        related_name='members',
        verbose_name='Группа',
    )
    name = models.CharField('ФИО', max_length=200)
    position = models.CharField('Должность', max_length=200)
    photo = models.ImageField(
        'Фото',
        upload_to='team/',
        blank=True, null=True,
        help_text='Соотношение 3:4, минимум 400 × 533 px.',
    )
    order = models.PositiveIntegerField('Порядок в группе', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['group__order', 'order', 'id']
        verbose_name = 'Член ИРВЦ'
        verbose_name_plural = 'Состав ИРВЦ'

    def __str__(self):
        return f'{self.name} — {self.position}'
