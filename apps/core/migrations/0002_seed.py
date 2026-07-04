"""
Начальные данные: одна запись настроек сайта, 5 пунктов меню, 4 показателя баннера.
Запускается при первом migrate.
"""
from django.db import migrations


NAV_ITEMS = [
    # (label, slug, url, order)
    ('Главная',      'home',     '/',          1),
    ('Состав ИРВЦ',  'team',     '/team/',     2),
    ('Новости',      'news',     '/news/',     3),
    ('Проекты',      'projects', '/projects/', 4),
    ('Контакты',     'contacts', '/contacts/', 5),
]

HERO_STATS = [
    # (number, label, order)
    ('1 200+', 'волонтёров в базе',       1),
    ('86',     'проведённых мероприятий', 2),
    ('24',     'партнёрские организации', 3),
    ('7 лет',  'на службе городу',        4),
]


def seed(apps, schema_editor):
    SiteSettings = apps.get_model('core', 'SiteSettings')
    NavigationItem = apps.get_model('core', 'NavigationItem')
    HeroStat = apps.get_model('core', 'HeroStat')

    # SiteSettings — singleton. get_or_create создаёт запись с id=1
    # если её ещё нет (django-solo этого не делает автоматически при миграциях).
    SiteSettings.objects.get_or_create(pk=1)

    for label, slug, url, order in NAV_ITEMS:
        NavigationItem.objects.update_or_create(
            slug=slug,
            defaults={'label': label, 'url': url, 'order': order},
        )

    for number, label, order in HERO_STATS:
        HeroStat.objects.update_or_create(
            label=label,
            defaults={'number': number, 'order': order},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
