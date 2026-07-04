"""
Ключевые модели: настройки сайта, навигация, статистика на баннере.
"""
import re

from django.db import models
from solo.models import SingletonModel


class SiteSettings(SingletonModel):
    """
    Одна запись на весь сайт. Хранит всё, что редактируется на главной:
    логотип, баннер, тексты hero, CTA, контактные данные, интеграции.
    """

    # --- Логотип и баннер ---
    logo = models.ImageField(
        'Логотип',
        upload_to='settings/',
        blank=True, null=True,
        help_text='Отображается в шапке и во вкладке браузера. Формат SVG или PNG с прозрачным фоном.',
    )
    banner = models.ImageField(
        'Фон hero-баннера',
        upload_to='settings/',
        blank=True, null=True,
        help_text='Крупное изображение для главной. Рекомендуемый размер — от 1600 × 900 px.',
    )

    # --- Тексты hero (первого баннера) ---
    hero_eyebrow = models.CharField(
        'Плашка над заголовком',
        max_length=120, blank=True,
        default='Набор открыт — присоединяйтесь',
        help_text='Короткая метка над основным заголовком. Оставьте пустой, чтобы скрыть.',
    )
    hero_title = models.CharField(
        'Заголовок баннера',
        max_length=200,
        default='Помогаем людям, делаем город',
    )
    hero_title_accent = models.CharField(
        'Выделенное слово в заголовке',
        max_length=80, blank=True,
        default='лучше',
        help_text='Показывается на новой строке с зелёным подчёркиванием.',
    )
    hero_lead = models.TextField(
        'Подзаголовок баннера',
        blank=True,
        help_text='Текст под заголовком, 1–3 предложения.',
    )
    hero_primary_text = models.CharField(
        'Текст основной кнопки', max_length=60, default='Присоединиться',
    )
    hero_secondary_text = models.CharField(
        'Текст второй кнопки', max_length=60, blank=True, default='Узнать больше',
        help_text='Оставьте пустой, чтобы скрыть вторую кнопку.',
    )
    hero_secondary_url = models.CharField(
        'Ссылка второй кнопки', max_length=500, blank=True, default='#about',
    )

    # --- CTA-блок ---
    cta_title = models.CharField(
        'Заголовок CTA-блока', max_length=200,
        default='Присоединяйтесь к команде волонтёров',
    )
    cta_lead = models.TextField(
        'Текст CTA-блока', blank=True,
        default='Заполните короткую анкету — мы свяжемся с вами и подберём '
                'направление, которое подходит именно вам.',
    )
    cta_button_text = models.CharField(
        'Текст кнопки CTA', max_length=60, default='Заполнить анкету',
    )

    # --- Общая ссылка «Стать волонтёром» ---
    join_url = models.URLField(
        'Ссылка «Стать волонтёром»', max_length=500, blank=True,
        help_text='Куда ведут все кнопки CTA. Обычно — Яндекс.Форма или Google Form.',
    )

    # --- Контакты (используются на странице «Контакты» и в футере) ---
    email = models.EmailField('Email', blank=True)
    phone = models.CharField(
        'Телефон', max_length=40, blank=True,
        help_text='Формат для показа: +7 (000) 000-00-00.',
    )
    phone_hint = models.CharField(
        'Подсказка к телефону', max_length=100, blank=True,
        default='пн–пт, 10:00–18:00',
    )
    address = models.CharField('Адрес', max_length=200, blank=True)
    address_hint = models.CharField(
        'Подсказка к адресу', max_length=200, blank=True,
        help_text='Например, «2 этаж, вход со двора».',
    )
    vk_url = models.URLField('ВКонтакте', blank=True)
    telegram_url = models.URLField('Telegram', blank=True)
    youtube_url = models.URLField('YouTube', blank=True)
    map_embed = models.TextField(
        'HTML-код карты', blank=True,
        help_text='Iframe с Яндекс.Карт (получить: «Поделиться» → «Код для сайта»).',
    )

    # --- Интеграция с ВК ---
    vk_group_id = models.CharField(
        'ID группы ВКонтакте', max_length=64, blank=True,
        help_text='Только цифры — например, для vk.com/club12345 введите 12345.',
    )

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'

    @property
    def phone_clean(self):
        """Телефон без разделителей — для href="tel:...". +7 (000) 000-00-00 → +70000000000."""
        return re.sub(r'\D', '', self.phone) if self.phone else ''


class NavigationItem(models.Model):
    """Пункты меню в шапке. Редактируются в админке, порядок — drag-and-drop через order."""

    SLUG_CHOICES = [
        ('home', 'Главная'),
        ('team', 'Состав ИРВЦ'),
        ('news', 'Новости'),
        ('projects', 'Проекты'),
        ('contacts', 'Контакты'),
    ]

    label = models.CharField('Название', max_length=60)
    slug = models.SlugField(
        'Ключ страницы', max_length=60, unique=True,
        help_text='Используется для подсветки активного пункта. Значения: home, team, news, projects, contacts.',
    )
    url = models.CharField(
        'Ссылка', max_length=500,
        help_text='Может быть якорем (#news), внутренним путём (/team/) или внешней ссылкой.',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'

    def __str__(self):
        return self.label


class HeroStat(models.Model):
    """Карточки статистики в hero-баннере (волонтёры, мероприятия, ...)."""

    number = models.CharField(
        'Значение', max_length=20,
        help_text='Например: «1 200+», «86», «7 лет».',
    )
    label = models.CharField('Подпись', max_length=100)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Показатель на баннере'
        verbose_name_plural = 'Показатели на баннере'

    def __str__(self):
        return f'{self.number} — {self.label}'
