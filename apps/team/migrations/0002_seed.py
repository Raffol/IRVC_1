"""Начальные группы команды. Участников добавляет админ через админку."""
from django.db import migrations


GROUPS = [
    ('Руководство',            1),
    ('Координация проектов',   2),
    ('Обучение и развитие',    3),
    ('Актив волонтёров',       4),
]


def seed(apps, schema_editor):
    TeamGroup = apps.get_model('team', 'TeamGroup')
    for name, order in GROUPS:
        TeamGroup.objects.update_or_create(name=name, defaults={'order': order})


class Migration(migrations.Migration):
    dependencies = [
        ('team', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
