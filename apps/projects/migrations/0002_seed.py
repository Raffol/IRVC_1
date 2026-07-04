"""Начальные категории проектов."""
from django.db import migrations


CATEGORIES = [
    # (name, slug, order)
    ('Социальные',      'social', 1),
    ('Экологические',   'eco',    2),
    ('Образовательные', 'edu',    3),
    ('Событийные',      'events', 4),
]


def seed(apps, schema_editor):
    ProjectCategory = apps.get_model('projects', 'ProjectCategory')
    for name, slug, order in CATEGORIES:
        ProjectCategory.objects.update_or_create(
            slug=slug,
            defaults={'name': name, 'order': order},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
